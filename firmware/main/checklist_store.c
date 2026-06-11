/*
 * checklist_store.c — load + validate aircraft checklists from SD card.
 *
 * FAA-aligned fault rule: any failure leaves the store EMPTY and returns a
 * specific FAULT_* code. The app must then stay in its safe "unopened" state
 * and annunciate the fault; it must never present a partial/stale checklist.
 */
#include "checklist_store.h"
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <sys/stat.h>
#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "driver/sdmmc_host.h"
#include "cJSON.h"
#include "board_pins.h"

static const char *TAG = "store";
#define SD_MOUNT "/sdcard"

/* ---- loaded data (heap) ---- */
static checklist_t *g_lists = NULL;
static int          g_count = 0;
static bool         g_ready = false;
static char         g_base[64] = {0};
static sdmmc_card_t *g_card = NULL;

/* ----- small helpers ----- */
const char *store_status_str(store_status_t s) {
    switch (s) {
        case STORE_OK:            return "OK";
        case FAULT_NO_CARD:       return "NO_CARD";
        case FAULT_NO_AIRCRAFT:   return "NO_AIRCRAFT";
        case FAULT_NO_JSON:       return "NO_JSON";
        case FAULT_PARSE:         return "PARSE_ERROR";
        case FAULT_VALIDATION:    return "VALIDATION_ERROR";
        case FAULT_AUDIO_MISSING: return "AUDIO_MISSING";
        case FAULT_NO_MEMORY:     return "NO_MEMORY";
    }
    return "UNKNOWN";
}
const char *store_fault_clip(store_status_t s) {
    switch (s) {
        case FAULT_NO_CARD:       return "fault_no_card";
        case FAULT_NO_AIRCRAFT:   return "fault_no_aircraft";
        case FAULT_NO_JSON:
        case FAULT_PARSE:
        case FAULT_VALIDATION:    return "fault_load_error";
        case FAULT_AUDIO_MISSING: return "fault_audio";
        case FAULT_NO_MEMORY:     return "fault_load_error";
        default:                  return "fault_load_error";
    }
}

const checklist_t *store_checklists(void) { return g_ready ? g_lists : NULL; }
int  store_count(void) { return g_ready ? g_count : 0; }
bool store_is_ready(void) { return g_ready; }

bool store_clip_path(const char *clip, char *out, size_t out_len) {
    if (!g_ready || !g_base[0]) return false;
    snprintf(out, out_len, "%s/audio/%s.wav", g_base, clip);
    return true;
}

/* phrase must be lowercase letters + single spaces only (MultiNet rule). */
static bool phrase_ok(const char *p) {
    if (!p || !*p) return false;
    bool prev_space = true;            /* disallow leading space */
    for (const char *c = p; *c; c++) {
        if (*c == ' ') { if (prev_space) return false; prev_space = true; }
        else if (*c >= 'a' && *c <= 'z') { prev_space = false; }
        else return false;             /* digit/uppercase/punct -> invalid */
    }
    return !prev_space;                /* disallow trailing space */
}

static void free_all(void) {
    if (g_lists) {
        for (int i = 0; i < g_count; i++) {
            free((void*)g_lists[i].id);
            free((void*)g_lists[i].title);
            for (int t = 0; t < MAX_TRIGGERS && g_lists[i].triggers[t]; t++)
                free((void*)g_lists[i].triggers[t]);
            for (int k = 0; k < g_lists[i].item_count; k++) {
                free((void*)g_lists[i].items[k].read_clip);
                free((void*)g_lists[i].items[k].text);
                for (int a = 0; a < MAX_ADVANCE && g_lists[i].items[k].advance[a]; a++)
                    free((void*)g_lists[i].items[k].advance[a]);
            }
        }
        free(g_lists);
    }
    g_lists = NULL; g_count = 0; g_ready = false; g_base[0] = 0;
}
void checklist_store_free(void) { free_all(); }

static char *dup_str(const char *s) { return s ? strdup(s) : NULL; }

#define FAIL(code, ...) do { \
        snprintf(r.detail, sizeof(r.detail), __VA_ARGS__); \
        r.status = (code); ESP_LOGE(TAG, "%s: %s", store_status_str(code), r.detail); \
        free_all(); cJSON_Delete(root); if (txt) free(txt); return r; \
    } while (0)

/* ---- SD mount (SDMMC 1-bit; switch to SPI in board_pins.h if needed) ---- */
static esp_err_t mount_sd(void) {
    esp_vfs_fat_sdmmc_mount_config_t mcfg = {
        .format_if_mount_failed = false, .max_files = 8,
        .allocation_unit_size = 16 * 1024,
    };
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    sdmmc_slot_config_t slot = SDMMC_SLOT_CONFIG_DEFAULT();
    slot.width = 1;                    /* 1-bit is simplest/most compatible */
#ifdef SD_CLK_GPIO
    slot.clk = SD_CLK_GPIO; slot.cmd = SD_CMD_GPIO; slot.d0 = SD_D0_GPIO;
#endif
    return esp_vfs_fat_sdmmc_mount(SD_MOUNT, &host, &slot, &mcfg, &g_card);
}

/* pick aircraft folder: config.txt "AIRCRAFT=" wins; else the sole subfolder. */
static bool select_aircraft(char *out, size_t out_len, char *why, size_t why_len) {
    /* try config.txt */
    FILE *cf = fopen(SD_MOUNT "/config.txt", "r");
    if (cf) {
        char line[64];
        while (fgets(line, sizeof(line), cf)) {
            char *p = strstr(line, "AIRCRAFT=");
            if (p) { p += 9; p[strcspn(p, "\r\n")] = 0;
                     if (*p) { snprintf(out, out_len, "%s", p); fclose(cf); return true; } }
        }
        fclose(cf);
    }
    /* else: find the single subdirectory */
    DIR *d = opendir(SD_MOUNT);
    if (!d) { snprintf(why, why_len, "cannot read SD root"); return false; }
    char found[32] = {0}; int n = 0;
    struct dirent *e;
    while ((e = readdir(d)) != NULL) {
        if (e->d_name[0] == '.') continue;
        char path[80]; struct stat st;
        snprintf(path, sizeof(path), SD_MOUNT "/%s", e->d_name);
        if (stat(path, &st) == 0 && S_ISDIR(st.st_mode)) {
            n++; if (n == 1) snprintf(found, sizeof(found), "%s", e->d_name);
        }
    }
    closedir(d);
    if (n == 0) { snprintf(why, why_len, "no aircraft folder on card"); return false; }
    if (n > 1)  { snprintf(why, why_len, "multiple aircraft; add config.txt AIRCRAFT="); return false; }
    snprintf(out, out_len, "%s", found);
    return true;
}

static char *read_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    if (n <= 0 || n > 256 * 1024) { fclose(f); return NULL; }
    char *buf = malloc(n + 1);
    if (!buf) { fclose(f); return NULL; }
    size_t rd = fread(buf, 1, n, f); fclose(f);
    buf[rd] = 0; return buf;
}

static bool file_exists(const char *path) {
    struct stat st; return stat(path, &st) == 0;
}

store_result_t checklist_store_load(bool require_audio) {
    store_result_t r = {0};
    cJSON *root = NULL; char *txt = NULL;
    free_all();

    if (mount_sd() != ESP_OK)
        FAIL(FAULT_NO_CARD, "SD card not detected or mount failed");

    char tail[32] = {0}, why[64] = {0};
    if (!select_aircraft(tail, sizeof(tail), why, sizeof(why)))
        FAIL(FAULT_NO_AIRCRAFT, "%s", why);

    char base[64]; snprintf(base, sizeof(base), SD_MOUNT "/%s", tail);
    char jpath[96]; snprintf(jpath, sizeof(jpath), "%s/checklists.json", base);

    txt = read_file(jpath);
    if (!txt) FAIL(FAULT_NO_JSON, "checklists.json missing/unreadable in %s", tail);

    root = cJSON_Parse(txt);
    if (!root) FAIL(FAULT_PARSE, "checklists.json is not valid JSON");

    cJSON *jlists = cJSON_GetObjectItem(root, "checklists");
    if (!cJSON_IsArray(jlists) || cJSON_GetArraySize(jlists) == 0)
        FAIL(FAULT_VALIDATION, "no checklists in data");

    cJSON *juniv = cJSON_GetObjectItem(root, "universal_advance");
    /* universal_advance is optional but if present must be valid phrases */
    if (juniv && cJSON_IsArray(juniv)) {
        cJSON *u; cJSON_ArrayForEach(u, juniv)
            if (!cJSON_IsString(u) || !phrase_ok(u->valuestring))
                FAIL(FAULT_VALIDATION, "bad universal_advance phrase");
    }

    int n = cJSON_GetArraySize(jlists);
    g_lists = calloc(n, sizeof(checklist_t));
    if (!g_lists) FAIL(FAULT_NO_MEMORY, "out of memory");

    int idx = 0;
    cJSON *cl;
    cJSON_ArrayForEach(cl, jlists) {
        checklist_t *out = &g_lists[idx];

        cJSON *jid = cJSON_GetObjectItem(cl, "id");
        cJSON *jtitle = cJSON_GetObjectItem(cl, "title");
        cJSON *jtrig = cJSON_GetObjectItem(cl, "triggers");
        cJSON *jitems = cJSON_GetObjectItem(cl, "items");
        if (!cJSON_IsString(jid) || !cJSON_IsArray(jtrig) || !cJSON_IsArray(jitems))
            FAIL(FAULT_VALIDATION, "checklist %d missing id/triggers/items", idx);

        out->id = dup_str(jid->valuestring);
        out->title = dup_str(cJSON_IsString(jtitle) ? jtitle->valuestring : jid->valuestring);

        /* triggers */
        int tn = cJSON_GetArraySize(jtrig);
        if (tn == 0) FAIL(FAULT_VALIDATION, "%s: needs >=1 trigger", out->id);
        if (tn > MAX_TRIGGERS) tn = MAX_TRIGGERS;
        for (int t = 0; t < tn; t++) {
            cJSON *tt = cJSON_GetArrayItem(jtrig, t);
            if (!cJSON_IsString(tt) || !phrase_ok(tt->valuestring))
                FAIL(FAULT_VALIDATION, "%s: invalid trigger phrase", out->id);
            out->triggers[t] = dup_str(tt->valuestring);
        }

        /* items */
        int in = cJSON_GetArraySize(jitems);
        if (in == 0) FAIL(FAULT_VALIDATION, "%s: needs >=1 item", out->id);
        if (in > MAX_ITEMS) FAIL(FAULT_VALIDATION, "%s: too many items (max %d)", out->id, MAX_ITEMS);
        out->item_count = in;
        for (int k = 0; k < in; k++) {
            cJSON *it = cJSON_GetArrayItem(jitems, k);
            cJSON *jclip = cJSON_GetObjectItem(it, "clip");
            cJSON *jtext = cJSON_GetObjectItem(it, "text");
            cJSON *jadv  = cJSON_GetObjectItem(it, "advance");
            if (!cJSON_IsString(jclip))
                FAIL(FAULT_VALIDATION, "%s item %d: missing clip", out->id, k);
            cl_item_t *oi = (cl_item_t*)&out->items[k];
            oi->read_clip = dup_str(jclip->valuestring);
            oi->text = dup_str(cJSON_IsString(jtext) ? jtext->valuestring : "");
            if (cJSON_IsArray(jadv)) {
                int an = cJSON_GetArraySize(jadv); if (an > MAX_ADVANCE) an = MAX_ADVANCE;
                for (int a = 0; a < an; a++) {
                    cJSON *av = cJSON_GetArrayItem(jadv, a);
                    if (!cJSON_IsString(av) || !phrase_ok(av->valuestring))
                        FAIL(FAULT_VALIDATION, "%s/%s: invalid advance phrase",
                             out->id, oi->read_clip);
                    oi->advance[a] = dup_str(av->valuestring);
                }
            }
            /* audio presence check (hard fault unless disabled) */
            if (require_audio) {
                char ap[112];
                snprintf(ap, sizeof(ap), "%s/audio/%s.wav", base, oi->read_clip);
                if (!file_exists(ap))
                    FAIL(FAULT_AUDIO_MISSING, "missing clip %s.wav", oi->read_clip);
            }
        }
        idx++;
    }

    /* success */
    g_count = idx;
    snprintf(g_base, sizeof(g_base), "%s", base);
    snprintf(r.aircraft, sizeof(r.aircraft), "%s", tail);
    snprintf(r.base_path, sizeof(r.base_path), "%s", base);
    r.checklist_count = g_count;
    int items = 0; for (int i=0;i<g_count;i++) items += g_lists[i].item_count;
    r.item_count = items;
    r.status = STORE_OK;
    g_ready = true;
    cJSON_Delete(root); free(txt);
    ESP_LOGI(TAG, "Loaded %s: %d checklists, %d items", tail, g_count, items);
    return r;
}
