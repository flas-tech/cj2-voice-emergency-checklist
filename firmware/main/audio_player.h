/* audio_player.h — minimal WAV playback over I2S (MAX98357A / ES8311) */
#pragma once
#include "esp_err.h"

/* Initialise the I2S TX channel used for speaker output. */
esp_err_t audio_player_init(void);

/*
 * Play a 16-bit PCM mono WAV file by basename.
 * Looks for /spiffs/<basename>.wav (falls back to /sdcard/<basename>.wav).
 * Blocks until playback finishes. Returns ESP_OK on success.
 */
esp_err_t audio_play_clip(const char *basename);

/* Convenience: play a known UI clip ("beep", "ready", "complete", ...). */
esp_err_t audio_play_ui(const char *name);

/* Play a WAV by absolute path (e.g. "/sdcard/CJ2/audio/engine_fire.wav").
 * Blocks until playback finishes. Returns ESP_OK on success. */
esp_err_t audio_play_path(const char *path);
