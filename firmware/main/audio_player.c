/*
 * audio_player.c — play 16-bit PCM mono WAV clips over I2S.
 *
 * Works with:
 *   - MAX98357A class-D amp (generic ESP32-S3 wiring), or
 *   - ES8311 codec on the ESP32-S3-Korvo-2 (see note below).
 *
 * For the Korvo-2 the ES8311 codec must also be configured over I2C; this file
 * shows the generic MAX98357A path which needs no codec setup. If you build for
 * the Korvo-2, initialise the ES8311 via esp_codec_dev (see README) and keep the
 * same I2S write loop here.
 */
#include "audio_player.h"
#include <stdio.h>
#include <string.h>
#include "driver/i2s_std.h"
#include "esp_log.h"

#include "board_pins.h"

static const char *TAG = "audio";
static i2s_chan_handle_t tx_chan = NULL;
static uint32_t cur_rate = 0;

typedef struct __attribute__((packed)) {
    char riff[4]; uint32_t size; char wave[4];
    char fmt[4];  uint32_t fmt_size; uint16_t fmt_type; uint16_t channels;
    uint32_t sample_rate; uint32_t byte_rate; uint16_t block_align; uint16_t bits;
} wav_header_t;

static esp_err_t i2s_set_rate(uint32_t rate)
{
    if (rate == cur_rate) return ESP_OK;
    i2s_std_clk_config_t clk = I2S_STD_CLK_DEFAULT_CONFIG(rate);
    ESP_ERROR_CHECK(i2s_channel_disable(tx_chan));
    esp_err_t e = i2s_channel_reconfig_std_clock(tx_chan, &clk);
    ESP_ERROR_CHECK(i2s_channel_enable(tx_chan));
    if (e == ESP_OK) cur_rate = rate;
    return e;
}

esp_err_t audio_player_init(void)
{
    i2s_chan_config_t chan_cfg =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_1, I2S_ROLE_MASTER);
    ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, &tx_chan, NULL));

    i2s_std_config_t std_cfg = {
        .clk_cfg  = I2S_STD_CLK_DEFAULT_CONFIG(16000),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
                        I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = AOUT_BCLK_GPIO,
            .ws   = AOUT_LRCLK_GPIO,
            .dout = AOUT_DOUT_GPIO,
            .din  = I2S_GPIO_UNUSED,
            .invert_flags = { .mclk_inv=false, .bclk_inv=false, .ws_inv=false },
        },
    };
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(tx_chan, &std_cfg));
    ESP_ERROR_CHECK(i2s_channel_enable(tx_chan));
    cur_rate = 16000;
    ESP_LOGI(TAG, "I2S audio-out (COM3) init on BCLK=%d WS=%d DOUT=%d",
             AOUT_BCLK_GPIO, AOUT_LRCLK_GPIO, AOUT_DOUT_GPIO);
    return ESP_OK;
}

static esp_err_t play_path(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) return ESP_ERR_NOT_FOUND;

    wav_header_t h;
    if (fread(&h, 1, sizeof(h), f) != sizeof(h) ||
        memcmp(h.riff, "RIFF", 4) || memcmp(h.wave, "WAVE", 4)) {
        ESP_LOGE(TAG, "bad WAV header: %s", path); fclose(f); return ESP_FAIL;
    }
    /* Skip to the data chunk (handles optional chunks between fmt and data). */
    char cid[4]; uint32_t csz;
    if (memcmp(h.fmt, "fmt ", 4) == 0 && h.fmt_size > 16)
        fseek(f, h.fmt_size - 16, SEEK_CUR);
    while (fread(cid, 1, 4, f) == 4 && fread(&csz, 4, 1, f) == 1) {
        if (memcmp(cid, "data", 4) == 0) break;
        fseek(f, csz, SEEK_CUR);
    }
    i2s_set_rate(h.sample_rate ? h.sample_rate : 16000);

    static int16_t buf[512];
    size_t n, written;
    while ((n = fread(buf, 1, sizeof(buf), f)) > 0) {
        i2s_channel_write(tx_chan, buf, n, &written, portMAX_DELAY);
    }
    fclose(f);
    return ESP_OK;
}

esp_err_t audio_play_clip(const char *basename)
{
    char path[96];
    snprintf(path, sizeof(path), "/spiffs/%s.wav", basename);
    if (play_path(path) == ESP_OK) return ESP_OK;
    snprintf(path, sizeof(path), "/sdcard/%s.wav", basename);
    esp_err_t e = play_path(path);
    if (e != ESP_OK) ESP_LOGW(TAG, "clip not found: %s", basename);
    return e;
}

esp_err_t audio_play_ui(const char *name) { return audio_play_clip(name); }

esp_err_t audio_play_path(const char *path)
{
    esp_err_t e = play_path(path);
    if (e != ESP_OK) ESP_LOGW(TAG, "clip not found: %s", path);
    return e;
}
