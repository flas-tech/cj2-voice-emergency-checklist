/*
 * board_pins.h — GPIO assignments.
 *
 * DEFAULT: generic ESP32-S3 + INMP441 I2S mic + MAX98357A I2S amp.
 * For the ESP32-S3-Korvo-2, the mics/codec/amp are on-board; use the
 * Korvo-2 BSP pin map instead (see README) and the ES8311 codec path.
 *
 * Pick any free GPIOs; just keep mic and speaker on separate I2S ports.
 */
#pragma once

/* ---- Push-to-talk button (active low, internal pull-up) ---- */
#define PTT_GPIO            0      /* BOOT button on most S3 devkits */
#define PTT_ACTIVE_LOW      1

/* ---- Status LED (optional) ---- */
#define STATUS_LED_GPIO     48     /* onboard RGB on many S3 devkits; -1 to disable */

/* ---- Microphone: INMP441 / ICS-43434 on I2S_NUM_0 ---- */
#define MIC_BCLK_GPIO       4
#define MIC_LRCLK_GPIO      5      /* WS */
#define MIC_DIN_GPIO        6      /* SD from mic */
/* INMP441 L/R pin tied to GND => left channel. */

/* ---- Speaker: MAX98357A on I2S_NUM_1 ---- */
#define SPK_BCLK_GPIO       15
#define SPK_LRCLK_GPIO      16     /* LRC */
#define SPK_DOUT_GPIO       7      /* DIN on the amp */
/* MAX98357A: SD pin floating = mono (L+R)/2; GAIN pin sets volume. */
