/*
 * main.c — CJ2 Voice Emergency Checklist (ESP32-S3), SD-card configurable.
 *
 * Pipeline:
 *   I2S mic -> AFE (NS, VAD) -> WakeNet ("Hi ESP") OR push-to-talk
 *           -> MultiNet (offline English command recognition)
 *           -> checklist state machine -> WAV readout over I2S
 *
 * Checklist DATA is loaded from an SD card at boot (checklist_store.c).
 *
 * ANNUNCIATION — Applied Avionics split-legend switch, dark-cockpit philosophy
 * (FAA AC 25-11). A physical SELECT switch (discrete input) turns the system
 * IN/OUT. The switch legend has two halves:
 *   TOP   white "VOICE CHKLST OFF"  — lit only when selected OUT
 *   BOTTOM amber "VOICE CHKLST FAULT" — lit only when selected IN + fault
 * Selected IN + healthy = both dark (true dark cockpit). A power-up lamp test
 * proves both LEDs. Per AC 25-11, OUT inhibits the fault caution.
 *
 * SAFETY (FAA-aligned): when selected IN, if the SD card is missing, unreadable,
 * or the data fails to parse/validate (or a referenced audio clip is missing),
 * the device does NOT present any checklist. It enters ST_FAULT, lights the
 * amber FAULT half, and annunciates the fault audibly. It retries loading so
 * inserting a valid card recovers it. A partial/stale checklist is never shown.
 *
 * DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.
 */
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/gpio.h"
#include "driver/i2s_std.h"
#include "esp_spiffs.h"

#include "esp_afe_sr_models.h"
#include "esp_mn_models.h"
#include "esp_mn_speech_commands.h"
#include "model_path.h"

#include "board_pins.h"
#include "checklists.h"
#include "checklist_store.h"
#include "audio_player.h"
#include "annunciator.h"

static const char *TAG = "cj2";

/* ---------------- recognition handles ---------------- */
static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t  *afe_data   = NULL;
static esp_mn_iface_t     *multinet   = NULL;
static model_iface_data_t *mn_model   = NULL;
static srmodel_list_t     *models     = NULL;

/* ---------------- app state ----------------
 * ST_OFF   : switch selected OUT — system off, OFF legend lit, no recognition.
 * ST_FAULT : selected IN but checklists unavailable — amber FAULT legend.
 * ST_HOME  : selected IN, healthy, awaiting an emergency name.
 * ST_RUN   : selected IN, healthy, reading a checklist.
 */
typedef enum { ST_OFF, ST_FAULT, ST_HOME, ST_RUN } app_state_t;
static volatile app_state_t state = ST_OFF;
static const checklist_t *active = NULL;
static int item_idx = 0;
static volatile bool ptt_down = false;

/* checklist data comes from the SD store */
static const checklist_t *LISTS = NULL;
static int LIST_COUNT = 0;

static inline bool sys_active(void) { return state == ST_HOME || state == ST_RUN; }

/* ---- phrase registry (maps MultiNet command_id -> phrase string) ---- */
#define MAX_PHRASES 200
static char phrase_text[MAX_PHRASES][48];
static int  phrase_count = 0;

static int register_phrase(const char *p) {
    if (!p) return -1;
    for (int i = 0; i < phrase_count; i++)
        if (strcmp(phrase_text[i], p) == 0) return i + 1;
    if (phrase_count >= MAX_PHRASES) return -1;
    strncpy(phrase_text[phrase_count], p, sizeof(phrase_text[0]) - 1);
    int id = phrase_count + 1;
    esp_mn_commands_add(id, (char *)p);
    phrase_count++;
    return id;
}

static void load_commands_for_state(void) {
    esp_mn_commands_clear();
    phrase_count = 0;
    /* Recognise nothing unless the system is active (selected IN + healthy). */
    if (!sys_active()) { esp_mn_commands_update(); return; }
    register_phrase("reset");
    if (state == ST_HOME) {
        for (int c = 0; c < LIST_COUNT; c++)
            for (int t = 0; t < MAX_TRIGGERS && LISTS[c].triggers[t]; t++)
                register_phrase(LISTS[c].triggers[t]);
    } else if (state == ST_RUN && active) {
        const cl_item_t *it = &active->items[item_idx];
        for (int a = 0; a < MAX_ADVANCE && it->advance[a]; a++)
            register_phrase(it->advance[a]);
        for (int u = 0; u < UNIVERSAL_ADVANCE_COUNT; u++)
            register_phrase(UNIVERSAL_ADVANCE[u]);
    }
    esp_mn_error_t *err = esp_mn_commands_update();
    if (err && err->num) ESP_LOGW(TAG, "%d phrases failed to parse", err->num);
}

/* ---------------- SELECT switch (discrete input) ---------------- */
static void select_init(void) {
    gpio_config_t io = { .pin_bit_mask = 1ULL << SELECT_GPIO, .mode = GPIO_MODE_INPUT,
                         .pull_up_en = GPIO_PULLUP_ENABLE };
    gpio_config(&io);
}
static inline bool selected_in(void) {
    int lvl = gpio_get_level(SELECT_GPIO);
    return SELECT_ACTIVE_LOW ? (lvl == 0) : (lvl == 1);
}

/* Refresh the split-legend switch from the current state. */
static void refresh_annunciator(void) {
    bool in = (state != ST_OFF);
    bool fault = (state == ST_FAULT);
    annunciator_update(in, fault);
    annunciator_set_ready(sys_active());
}

/* play a clip from the SD aircraft folder (audio_player resolves the path) */
static void play_sd_clip(const char *clip) {
    char path[112];
    if (store_clip_path(clip, path, sizeof(path)))
        audio_play_path(path);
}

/* ---------------- OFF (deselected) handling ---------------- */
static void enter_off(void) {
    state = ST_OFF; active = NULL; item_idx = 0; LISTS = NULL; LIST_COUNT = 0;
    refresh_annunciator();              /* white OFF legend; fault inhibited */
    load_commands_for_state();          /* listen for nothing */
    ESP_LOGI(TAG, "SELECT OUT — voice checklist OFF");
}

/* ---------------- FAULT handling ---------------- */
static void enter_fault(store_status_t s, const char *detail) {
    state = ST_FAULT; active = NULL; item_idx = 0; LISTS = NULL; LIST_COUNT = 0;
    refresh_annunciator();              /* amber FAULT legend ON (selected IN) */
    load_commands_for_state();          /* listen for nothing */
    ESP_LOGE(TAG, "FAULT [%s]: %s — checklists unavailable; staying in safe state",
             store_status_str(s), detail ? detail : "");
    /* Audible annunciation: generic fault tone + specific cause if clip exists. */
    audio_play_ui("fault");
    play_sd_clip(store_fault_clip(s));
}

/* ---------------- checklist actions ---------------- */
static void enter_home(void) {
    state = ST_HOME; active = NULL; item_idx = 0;
    refresh_annunciator();              /* healthy: both legend halves dark */
    load_commands_for_state();
    ESP_LOGI(TAG, "HOME — say an emergency name (or 'Hi ESP' then the name)");
    play_sd_clip("ready");
}

static void read_current_item(void) {
    const cl_item_t *it = &active->items[item_idx];
    ESP_LOGI(TAG, "[%s] step %d/%d: %s",
             active->id, item_idx + 1, active->item_count, it->text);
    play_sd_clip(it->read_clip);
    load_commands_for_state();
}

static void start_checklist(const checklist_t *c) {
    active = c; item_idx = 0; state = ST_RUN;
    refresh_annunciator();
    ESP_LOGI(TAG, "Loading checklist: %s", c->title);
    read_current_item();
}

static void advance_item(void) {
    if (++item_idx >= active->item_count) {
        ESP_LOGI(TAG, "Checklist complete: %s", active->title);
        play_sd_clip("complete");
        enter_home();
        return;
    }
    read_current_item();
}

static void handle_phrase(int cmd_id) {
    if (!sys_active()) return;          /* never act on speech unless active */
    if (cmd_id < 1 || cmd_id > phrase_count) return;
    const char *p = phrase_text[cmd_id - 1];
    ESP_LOGI(TAG, "recognized: \"%s\"", p);

    if (strcmp(p, "reset") == 0) { enter_home(); return; }

    if (state == ST_HOME) {
        for (int c = 0; c < LIST_COUNT; c++)
            for (int t = 0; t < MAX_TRIGGERS && LISTS[c].triggers[t]; t++)
                if (strcmp(p, LISTS[c].triggers[t]) == 0) { start_checklist(&LISTS[c]); return; }
    } else if (state == ST_RUN) {
        advance_item();                 /* any registered advance/universal word */
    }
}

/* ---------------- PTT button ---------------- */
static void ptt_init(void) {
    gpio_config_t io = { .pin_bit_mask = 1ULL << PTT_GPIO,
                         .mode = GPIO_MODE_INPUT, .pull_up_en = GPIO_PULLUP_ENABLE };
    gpio_config(&io);
}
static inline bool ptt_pressed(void) {
    int lvl = gpio_get_level(PTT_GPIO);
    return PTT_ACTIVE_LOW ? (lvl == 0) : (lvl == 1);
}

/* ---------------- audio feed + detect tasks ---------------- */
static void feed_task(void *arg) {
    int chunk = afe_handle->get_feed_chunksize(afe_data);
    int nch   = afe_handle->get_feed_channel_num(afe_data);
    int16_t *buf = malloc(chunk * nch * sizeof(int16_t));

    i2s_chan_handle_t rx;
    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    i2s_new_channel(&cc, NULL, &rx);
    i2s_std_config_t sc = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(16000),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
                        I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = { .mclk=I2S_GPIO_UNUSED, .bclk=MIC_BCLK_GPIO,
                      .ws=MIC_LRCLK_GPIO, .dout=I2S_GPIO_UNUSED, .din=MIC_DIN_GPIO },
    };
    i2s_channel_init_std_mode(rx, &sc);
    i2s_channel_enable(rx);

    size_t got;
    while (1) {
        i2s_channel_read(rx, buf, chunk * nch * sizeof(int16_t), &got, portMAX_DELAY);
        afe_handle->feed(afe_data, buf);
    }
}

static void detect_task(void *arg) {
    bool awake = false;
    while (1) {
        afe_fetch_result_t *r = afe_handle->fetch(afe_data);
        if (!r || r->ret_value == ESP_FAIL) continue;
        if (!sys_active()) { awake = false; continue; }  /* ignore audio unless active */

        bool ptt = ptt_pressed();
        if (ptt && !ptt_down) { ptt_down = true; awake = true; multinet->clean(mn_model); }
        if (!ptt && ptt_down) ptt_down = false;

        if (r->wakeup_state == WAKENET_DETECTED) { awake = true; multinet->clean(mn_model); }

        if (awake) {
            esp_mn_state_t s = multinet->detect(mn_model, r->data);
            if (s == ESP_MN_STATE_DETECTED) {
                esp_mn_results_t *res = multinet->get_results(mn_model);
                if (res && res->num > 0) handle_phrase(res->command_id[0]);
                multinet->clean(mn_model);
                if (!ptt_down) awake = false;
            } else if (s == ESP_MN_STATE_TIMEOUT) {
                if (!ptt_down) awake = false;
                multinet->clean(mn_model);
            }
        }
    }
}

/* ---------------- data load + monitor ---------------- */
static bool try_load_checklists(void) {
    store_result_t res = checklist_store_load(true /* require audio */);
    if (res.status != STORE_OK) { enter_fault(res.status, res.detail); return false; }
    LISTS = store_checklists();
    LIST_COUNT = store_count();
    if (!LISTS || LIST_COUNT == 0) { enter_fault(FAULT_VALIDATION, "empty after load"); return false; }
    ESP_LOGI(TAG, "Loaded aircraft %s: %d checklists, %d items",
             res.aircraft, res.checklist_count, res.item_count);
    enter_home();
    return true;
}

/* Apply the system to a freshly-read SELECT position. */
static void apply_select(bool in) {
    if (in) {
        /* Selected IN: attempt to load; enters HOME or FAULT. */
        checklist_store_free();
        try_load_checklists();
    } else {
        enter_off();
    }
}

/* Poll the SELECT switch (debounced) and, while selected IN + faulted,
 * periodically retry loading so inserting a good card recovers us. */
static void select_monitor_task(void *arg) {
    bool last = selected_in();
    int stable = 0;
    while (1) {
        bool now = selected_in();
        if (now == last) {
            stable = (stable < 5) ? stable + 1 : stable;
        } else {
            last = now; stable = 0;     /* changed — wait for it to settle */
        }
        /* Act on a debounced edge: state disagrees with the switch. */
        bool sw_in = last;
        bool sys_in = (state != ST_OFF);
        if (stable >= 3 && sw_in != sys_in) {
            ESP_LOGI(TAG, "SELECT %s", sw_in ? "IN" : "OUT");
            apply_select(sw_in);
        }
        /* Retry loading while faulted (only meaningful when selected IN). */
        if (state == ST_FAULT) {
            checklist_store_free();
            if (try_load_checklists())
                ESP_LOGI(TAG, "Recovered from fault — checklists now available");
        }
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}

/* ---------------- init ---------------- */
static void mount_internal_spiffs(void) {
    /* internal SPIFFS holds only the UI/fault clips (ready, complete, fault). */
    esp_vfs_spiffs_conf_t conf = { .base_path = "/spiffs", .partition_label = NULL,
                                   .max_files = 6, .format_if_mount_failed = false };
    if (esp_vfs_spiffs_register(&conf) != ESP_OK)
        ESP_LOGW(TAG, "internal SPIFFS mount failed — UI clips unavailable");
}

static void sr_init(void) {
    models = esp_srmodel_init("model");
    afe_config_t *afe_cfg = afe_config_init("MR", models, AFE_TYPE_SR, AFE_MODE_LOW_COST);
    afe_handle = esp_afe_handle_from_config(afe_cfg);
    afe_data   = afe_handle->create_from_config(afe_cfg);

    char *mn_name = esp_srmodel_filter(models, ESP_MN_PREFIX, ESP_MN_ENGLISH);
    if (!mn_name) { ESP_LOGE(TAG, "No English MultiNet model — enable mn*_en"); return; }
    multinet = esp_mn_handle_from_name(mn_name);
    mn_model = multinet->create(mn_name, 5760);
    ESP_LOGI(TAG, "MultiNet model: %s", mn_name);
}

void app_main(void) {
    ESP_LOGI(TAG, "CJ2 Voice Emergency Checklist — DEMO/TRAINING ONLY");
    annunciator_init();                 /* power-up lamp test, then dark */
    mount_internal_spiffs();
    audio_player_init();
    ptt_init();
    select_init();
    sr_init();

    /* Resolve initial state from the physical SELECT switch. */
    if (!selected_in()) {
        enter_off();
    } else if (!multinet) {
        enter_fault(FAULT_NO_MEMORY, "speech model init failed");
    } else {
        try_load_checklists();          /* HOME on success, FAULT on any problem */
    }

    xTaskCreatePinnedToCore(feed_task,          "feed",    4 * 1024, NULL, 5, NULL, 0);
    xTaskCreatePinnedToCore(detect_task,        "detect",  8 * 1024, NULL, 5, NULL, 1);
    xTaskCreatePinnedToCore(select_monitor_task,"selmon",  4 * 1024, NULL, 3, NULL, 0);
}
