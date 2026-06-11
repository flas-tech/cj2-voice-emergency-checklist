/*
 * checklists.h — CJ2 (CE 525A) emergency checklist data for ESP32-S3
 *
 * Mirrors the web demo's checklists.js. Each checklist has:
 *   - a set of TRIGGER phrases (spoken to select it)
 *   - an ordered list of ITEMS; each item has:
 *       read_clip : basename of the WAV clip read aloud (in /spiffs or /sdcard)
 *       text      : human-readable item text (for the log / optional display)
 *       advance[] : spoken completion phrases that move to the next item
 *
 * IMPORTANT (MultiNet command rules):
 *   - English MultiNet (mn6_en / mn7_en) requires ESP32-S3.
 *   - Command strings: lowercase/uppercase letters and spaces only.
 *     NO digits, NO punctuation. Spell numbers as words ("v one", "two hundred").
 *   - Keep phrases short and acoustically distinct for best accuracy.
 *
 * DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.
 */
#pragma once
#include <stddef.h>

#define MAX_ADVANCE   4
#define MAX_ITEMS     12
#define MAX_TRIGGERS  4

typedef struct {
    const char *read_clip;              /* WAV file basename, no extension      */
    const char *text;                   /* readable description (log/display)   */
    const char *advance[MAX_ADVANCE];   /* completion phrases (NULL-terminated) */
} cl_item_t;

typedef struct {
    const char *id;
    const char *title;
    const char *triggers[MAX_TRIGGERS]; /* NULL-terminated                      */
    const cl_item_t items[MAX_ITEMS];
    int item_count;
} checklist_t;

/* Universal completion words accepted on ANY item, in addition to per-item. */
extern const char *UNIVERSAL_ADVANCE[];
extern const int   UNIVERSAL_ADVANCE_COUNT;

extern const checklist_t CHECKLISTS[];
extern const int CHECKLIST_COUNT;
