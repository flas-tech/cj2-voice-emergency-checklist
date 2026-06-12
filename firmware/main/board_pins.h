/*
 * board_pins.h — GPIO assignments.
 *
 * INSTALLED DESIGN: crew audio is RECEIVE-ONLY off the aircraft audio panel
 * (isolated I2S codec ADC / analog line tap on I2S_NUM_0 = audio INPUT), and
 * checklist read-aloud audio is sent OUT through a dedicated, galvanically-
 * isolated COM3-style audio-panel channel (line driver / DAC on I2S_NUM_1 =
 * audio OUTPUT). These are two electrically separate, isolated channels.
 *
 * The onboard MAX98357A speaker-amp and an INMP441 mic are BENCH-TEST ONLY
 * (development), never the installed audio source/sink. For the ESP32-S3-
 * Korvo-2, the codec is on-board; use the Korvo-2 BSP pin map (see README).
 *
 * Pick any free GPIOs; keep the audio INPUT and OUTPUT on separate I2S ports.
 */
#pragma once

/* ---- Push-to-talk button (active low, internal pull-up) ---- */
#define PTT_GPIO            0      /* BOOT button on most S3 devkits */
#define PTT_ACTIVE_LOW      1

/* ================================================================
 * APPLIED AVIONICS split-legend annunciator switch (VIVISUN / Korry style)
 * ----------------------------------------------------------------
 * DARK COCKPIT PHILOSOPHY (FAA AC 25-11): the switch shows NOTHING when the
 * system is selected IN and fully functional. The legend has two independently
 * driven halves:
 *
 *   TOP half  — white  "VOICE CHKLST OFF"  : lit only when selected OUT
 *   BOTTOM half— amber  "VOICE CHKLST FAULT": lit only when selected IN + fault
 *
 *   State                     | TOP (OFF) | BOTTOM (FAULT)
 *   --------------------------|-----------|----------------
 *   Selected IN  + healthy    |   dark    |   dark      <- true dark cockpit
 *   Selected IN  + fault      |   dark    |   AMBER ON
 *   Selected OUT (deselected) | WHITE ON  |   dark      <- fault inhibited (AC 25-11)
 *
 * Per AC 25-11 quiet/dark guidance, a deliberately-deselected system does not
 * annunciate a caution (no crew action is required), so OUT inhibits the FAULT
 * half. A power-up LAMP TEST drives both halves briefly so a dead LED can't be
 * mistaken for a healthy dark state.
 * ================================================================ */

/* ---- SELECT switch: physical discrete input read by the firmware ----
 * Wire the switch contact so that SELECTED IN connects the GPIO to GND
 * (active-low with internal pull-up). When the switch is pulled OUT the
 * line floats high via the pull-up = deselected.
 */
#define SELECT_GPIO            10     /* discrete in: IN/OUT of the panel switch */
#define SELECT_ACTIVE_LOW      1      /* 1: GPIO LOW = selected IN (system on)   */

/* ---- Legend half: TOP "VOICE CHKLST OFF" (white) ---- */
#define LEGEND_OFF_GPIO        21     /* set to -1 to disable */
#define LEGEND_OFF_ACTIVE_HIGH 1      /* 1: GPIO HIGH = lamp ON */

/* ---- Legend half: BOTTOM "VOICE CHKLST FAULT" (amber) ---- */
#define LEGEND_FAULT_GPIO      14     /* set to -1 to disable */
#define LEGEND_FAULT_ACTIVE_HIGH 1    /* 1: GPIO HIGH = lamp ON */

/* Power-up lamp test duration (both legend halves on), milliseconds. */
#define LAMP_TEST_MS           2000

/* ---- Status LED (optional) — lit when READY/listening ---- */
#define STATUS_LED_GPIO     48     /* onboard RGB on many S3 devkits; -1 to disable */
#define STATUS_LED_ACTIVE_HIGH 1

/* ---- microSD (SDMMC 1-bit). Korvo-2 has a slot wired to these by default.
 * For a custom board, set these to your wiring (or switch to SPI mode). ---- */
#define SD_CLK_GPIO         7
#define SD_CMD_GPIO         9
#define SD_D0_GPIO          8

/* ---- Audio INPUT (crew speech): isolated I2S codec ADC / analog line tap
 *      off the aircraft audio panel, on I2S_NUM_0. RECEIVE-ONLY.
 *      (Bench-test: an INMP441 / ICS-43434 mic may be wired here instead.) ---- */
#define AIN_BCLK_GPIO       4
#define AIN_LRCLK_GPIO      5      /* WS */
#define AIN_DIN_GPIO        6      /* SD from codec ADC / mic */
/* Analog-tap option uses the codec line input; source selected per Config Card. */

/* ---- Audio OUTPUT (checklist read-aloud): isolated line driver / DAC on
 *      I2S_NUM_1, feeding a galvanically-isolated COM3-style audio-panel
 *      channel. The output stage cannot key/jam/back-feed required COM.
 *      (Bench-test: a MAX98357A speaker-amp may be substituted here.) ---- */
#define AOUT_BCLK_GPIO      15
#define AOUT_LRCLK_GPIO     16     /* LRC */
#define AOUT_DOUT_GPIO      17     /* DIN on the line driver / DAC */
