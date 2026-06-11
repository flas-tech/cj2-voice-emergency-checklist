/*
 * main.c — CJ2 Voice Emergency Checklist (ESP32-S3)
 *
 * Pipeline:
 *   I2S mic -> AFE (noise suppression, VAD) -> WakeNet ("Hi ESP") OR push-to-talk
 *           -> MultiNet (offline English command recognition)
 *           -> checklist state machine -> WAV readout over I2S
 *
 * Two ways to start listening for commands:
 *   1) Wake word: say "Hi ESP", then speak.
 *   2) Push-to-talk: hold the PTT button (board_pins.h) while speaking.
 *
 * State machine (mirrors the web demo):
 *   HOME  -> recognise a checklist TRIGGER -> load it, read item 0
 *   RUN   -> after each item, recognise its ADVANCE word -> read next item
 *         -> at end, play "complete", return to HOME
 *   Say "reset" any time to return to HOME.
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
#include "audio_player.h"

static const char *TAG = "cj2";

/* ---------------- recognition handles ---------------- */
static esp_afe_sr_iface_t *afe_handle = NULL;
static esp_afe_sr_data_t  *afe_data   = NULL;
static esp_mn_iface_t     *multinet   = NULL;
static model_iface_data_t *mn_model   = NULL;
static srmodel_list_t     *models     = NULL;

/* ---------------- app state ---------------- */
typedef enum { ST_HOME, ST_RUN } app_state_t;
static volatile app_state_t state = ST_HOME;
static const checklist_t *active = NULL;
static int item_idx = 0;
static volatile bool ptt_down = false;   /* push-to-talk held */

/* Command-ID space we register into MultiNet:
 *   We register every distinct phrase the app might need (triggers + advance +
 *   "reset") and map each command_id back to a meaning we look up in software.
 * MultiNet returns the command_id of the matched phrase; we keep a parallel
 * table of phrase strings so we can interpret it.
 */
#define MAX_PHRASES 200
static char  phrase_text[MAX_PHRASES][48];
static int   phrase_count = 0;

static int register_phrase(const char *p)
{
    if (!p) return -1;
    /* dedupe */
    for (int i = 0; i < phrase_count; i++)
        if (strcmp(phrase_text[i], p) == 0) return i + 1;   /* id is 1-based */
    if (phrase_count >= MAX_PHRASES) return -1;
    strncpy(phrase_text[phrase_count], p, sizeof(phrase_text[0]) - 1);
    int id = phrase_count + 1;
    esp_mn_commands_add(id, (char *)p);
    phrase_count++;
    return id;
}

/* Register the phrases relevant to the CURRENT state so the recognizer only
 * listens for what matters (improves accuracy and speed). */
static void load_commands_for_state(void)
{
    esp_mn_commands_clear();
    phrase_count = 0;
    register_phrase("reset");

    if (state == ST_HOME) {
        for (int c = 0; c < CHECKLIST_COUNT; c++)
            for (int t = 0; t < MAX_TRIGGERS && CHECKLISTS[c].triggers[t]; t++)
                register_phrase(CHECKLISTS[c].triggers[t]);
    } else if (state == ST_RUN && active) {
        const cl_item_t *it = &active->items[item_idx];
        for (int a = 0; a < MAX_ADVANCE && it->advance[a]; a++)
            register_phrase(it->advance[a]);
        for (int u = 0; u < UNIVERSAL_ADVANCE_COUNT; u++)
            register_phrase(UNIVERSAL_ADVANCE[u]);
    }
    esp_mn_error_t *err = esp_mn_commands_update();
    if (err && err->num) ESP_LOGW(TAG, "%d command phrases failed to parse", err->num);
}

/* ---------------- checklist actions ---------------- */
static void enter_home(void)
{
    state = ST_HOME; active = NULL; item_idx = 0;
    load_commands_for_state();
    ESP_LOGI(TAG, "HOME — say an emergency name (or 'Hi ESP' then the name)");
    audio_play_ui("ready");          /* e.g. "State the emergency" */
}

static void read_current_item(void)
{
    const cl_item_t *it = &active->items[item_idx];
    ESP_LOGI(TAG, "[%s] step %d/%d: %s",
             active->id, item_idx + 1, active->item_count, it->text);
    audio_play_clip(it->read_clip);
    load_commands_for_state();
}

static void start_checklist(const checklist_t *c)
{
    active = c; item_idx = 0; state = ST_RUN;
    ESP_LOGI(TAG, "Loading checklist: %s", c->title);
    audio_play_clip(c->id);          /* optional title clip; ok if missing */
    read_current_item();
}

static void advance_item(void)
{
    item_idx++;
    if (item_idx >= active->item_count) {
        ESP_LOGI(TAG, "Checklist complete: %s", active->title);
        audio_play_ui("complete");
        enter_home();
        return;
    }
    read_current_item();
}

/* Map a recognized phrase id to an action depending on state. */
static void handle_phrase(int cmd_id)
{
    if (cmd_id < 1 || cmd_id > phrase_count) return;
    const char *p = phrase_text[cmd_id - 1];
    ESP_LOGI(TAG, "recognized: \"%s\"", p);

    if (strcmp(p, "reset") == 0) { enter_home(); return; }

    if (state == ST_HOME) {
        for (int c = 0; c < CHECKLIST_COUNT; c++)
            for (int t = 0; t < MAX_TRIGGERS && CHECKLISTS[c].triggers[t]; t++)
                if (strcmp(p, CHECKLISTS[c].triggers[t]) == 0) {
                    start_checklist(&CHECKLISTS[c]); return;
                }
    } else if (state == ST_RUN) {
        /* any registered advance/universal phrase advances the item */
        advance_item();
    }
}

/* ---------------- PTT button ---------------- */
static void ptt_init(void)
{
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << PTT_GPIO,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&io);
}
static inline bool ptt_pressed(void)
{
    int lvl = gpio_get_level(PTT_GPIO);
    return PTT_ACTIVE_LOW ? (lvl == 0) : (lvl == 1);
}

/* ---------------- audio feed + detect tasks ---------------- */
static void feed_task(void *arg)
{
    int chunk = afe_handle->get_feed_chunksize(afe_data);
    int nch   = afe_handle->get_feed_channel_num(afe_data);
    int16_t *buf = malloc(chunk * nch * sizeof(int16_t));

    /* Mic I2S RX on I2S_NUM_0 */
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

static void detect_task(void *arg)
{
    bool awake = false;          /* WakeNet OR PTT enables command detection */
    while (1) {
        afe_fetch_result_t *r = afe_handle->fetch(afe_data);
        if (!r || r->ret_value == ESP_FAIL) continue;

        bool ptt = ptt_pressed();
        if (ptt && !ptt_down) { ptt_down = true; awake = true; multinet->clean(mn_model); }
        if (!ptt && ptt_down) { ptt_down = false; }

        if (r->wakeup_state == WAKENET_DETECTED) {
            awake = true;
            multinet->clean(mn_model);
            ESP_LOGI(TAG, "wake word detected");
        }

        if (awake) {
            esp_mn_state_t s = multinet->detect(mn_model, r->data);
            if (s == ESP_MN_STATE_DETECTED) {
                esp_mn_results_t *res = multinet->get_results(mn_model);
                if (res && res->num > 0) handle_phrase(res->command_id[0]);
                multinet->clean(mn_model);
                if (!ptt_down) awake = false;     /* re-arm wake word */
            } else if (s == ESP_MN_STATE_TIMEOUT) {
                if (!ptt_down) awake = false;
                multinet->clean(mn_model);
            }
        }
    }
}

/* ---------------- init ---------------- */
static void mount_spiffs(void)
{
    esp_vfs_spiffs_conf_t conf = {
        .base_path = "/spiffs", .partition_label = NULL,
        .max_files = 8, .format_if_mount_failed = false,
    };
    esp_err_t e = esp_vfs_spiffs_register(&conf);
    if (e != ESP_OK) ESP_LOGW(TAG, "SPIFFS mount failed (%s) — audio clips unavailable",
                              esp_err_to_name(e));
}

static void sr_init(void)
{
    models = esp_srmodel_init("model");

    afe_config_t *afe_cfg = afe_config_init("MR", models, AFE_TYPE_SR, AFE_MODE_LOW_COST);
    afe_handle = esp_afe_handle_from_config(afe_cfg);
    afe_data   = afe_handle->create_from_config(afe_cfg);

    char *mn_name = esp_srmodel_filter(models, ESP_MN_PREFIX, ESP_MN_ENGLISH);
    if (!mn_name) { ESP_LOGE(TAG, "No English MultiNet model — select mn*_en in menuconfig"); return; }
    multinet = esp_mn_handle_from_name(mn_name);
    mn_model = multinet->create(mn_name, 5760);   /* ~6s detection window */
    ESP_LOGI(TAG, "MultiNet model: %s", mn_name);
}

void app_main(void)
{
    ESP_LOGI(TAG, "CJ2 Voice Emergency Checklist — DEMO/TRAINING ONLY");
    mount_spiffs();
    audio_player_init();
    ptt_init();
    sr_init();
    if (!multinet) { ESP_LOGE(TAG, "Speech model init failed; halting."); return; }

    enter_home();
    xTaskCreatePinnedToCore(feed_task,   "feed",   4 * 1024, NULL, 5, NULL, 0);
    xTaskCreatePinnedToCore(detect_task, "detect", 8 * 1024, NULL, 5, NULL, 1);
}
