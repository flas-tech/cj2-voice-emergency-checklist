/*
 * checklist_store.h — SD-card-backed checklist storage + fault model.
 *
 * The device loads aircraft checklist data from an SD card at boot. Per the
 * FAA-aligned safety requirement, if anything prevents a COMPLETE, VALID load,
 * the system MUST refuse to present any checklist and revert to a safe
 * "unopened" FAULT state with a clear annunciation — never a partial or stale
 * checklist.
 *
 * SD layout (auto-load the single aircraft folder; config.txt only if many):
 *   /sdcard/config.txt            (optional) one line: AIRCRAFT=<folder>
 *   /sdcard/<TAIL>/checklists.json
 *   /sdcard/<TAIL>/audio/*.wav
 *
 * DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.
 */
#pragma once
#include <stdbool.h>
#include "checklists.h"   /* checklist_t, cl_item_t */

/* Result of attempting to bring the checklist data online. */
typedef enum {
    STORE_OK = 0,             /* SD mounted, JSON parsed+validated, audio present */
    FAULT_NO_CARD,            /* SD not detected / mount failed                    */
    FAULT_NO_AIRCRAFT,        /* no aircraft folder (or config.txt target missing) */
    FAULT_NO_JSON,            /* checklists.json missing or unreadable             */
    FAULT_PARSE,              /* JSON malformed                                    */
    FAULT_VALIDATION,         /* schema/voice-rule violation, empty data, etc.     */
    FAULT_AUDIO_MISSING,      /* a referenced read-aloud clip is absent            */
    FAULT_NO_MEMORY,          /* allocation failed while loading                   */
} store_status_t;

typedef struct {
    store_status_t status;
    char aircraft[32];        /* loaded aircraft id, when STORE_OK                 */
    char base_path[64];       /* e.g. "/sdcard/CJ2"                                */
    char detail[128];         /* human-readable fault detail for logs/annunciation */
    int  checklist_count;
    int  item_count;
} store_result_t;

/*
 * Mount SD, select aircraft, parse + validate checklists.json, and verify every
 * referenced audio clip exists. On success, fills the global checklist table
 * (accessible via store_checklists()/store_count()) and returns STORE_OK.
 * On ANY problem returns the specific FAULT_* code and leaves the table EMPTY.
 *
 * `require_audio`: if true (recommended/default), a missing clip is a hard fault.
 */
store_result_t checklist_store_load(bool require_audio);

/* Loaded data — valid only when the last load returned STORE_OK. */
const checklist_t *store_checklists(void);
int                store_count(void);

/* True only if a complete, valid data set is currently loaded. */
bool store_is_ready(void);

/* Map a fault code to a short audio-clip basename for annunciation. */
const char *store_fault_clip(store_status_t s);

/* Human-readable name for logs. */
const char *store_status_str(store_status_t s);

/* Release loaded data (used on reload). */
void checklist_store_free(void);

/* Resolve an audio clip path for the loaded aircraft: "<base>/audio/<clip>.wav".
 * Returns false if no aircraft is loaded. Buffer should be >=96 bytes. */
bool store_clip_path(const char *clip, char *out, size_t out_len);
