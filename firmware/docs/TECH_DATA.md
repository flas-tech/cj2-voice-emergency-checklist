# Technical Data — CJ2 Voice Emergency Checklist (ESP32-S3)

> **DEMO / TRAINING USE ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**
> This is a bench/educational prototype. It is not airworthy, not certified, and
> must never be installed in or relied upon aboard an aircraft.

This document is the complete electrical/hardware reference for the firmware in
`firmware/`. All GPIO numbers match [`main/board_pins.h`](../main/board_pins.h).
See [`wiring_diagram.png`](wiring_diagram.png) for the schematic.

---

## 1. System overview

| Item | Value |
|---|---|
| MCU | **ESP32-S3** (dual-core LX7 @ 240 MHz) — **PSRAM required** by ESP-SR |
| Recommended module | ESP32-S3-WROOM-1 **N16R8** (16 MB flash, 8 MB octal PSRAM) |
| Speech stack | Espressif **ESP-SR**: AFE (NS/VAD) → WakeNet "Hi ESP" → MultiNet English |
| Crew audio input | **From the aircraft audio panel** on **I2S_NUM_0**, selectable per install: **analog** (isolated line tap → I2S codec ADC) or **digital** (I2S codec fed from a buffered tap). Onboard MEMS mic = bench-test only |
| Audio output | **I2S_NUM_1** DAC → isolated line-level output stage (isolation transformer + line driver on the TX line) → **dedicated COM3-style audio-panel input channel**; crew hears checklist read-aloud in-headset. **Onboard speaker/amplifier removed.** Bench-test speaker-amp (MAX98357A) optionally substituted during development only. |
| Config storage | **microSD** (SDMMC 1-bit), FAT32, one folder per aircraft |
| Annunciation | Applied Avionics split-legend switch (dark-cockpit, FAA AC 25-11) |
| Logic level | **3.3 V** (ESP32-S3 is **not** 5 V tolerant on GPIO) |

Two build paths are supported:

- **Integrated:** **ESP32-S3-Korvo-2** dev board (on-board ES8311 codec, microSD slot).
  Repurpose line-in for the audio-panel receive feed; add isolated COM3 output stage
  (DAC/line driver + output isolation transformer) externally.
- **DIY (this document):** ESP32-S3 DevKitC-1 N16R8 + audio-panel input stage
  (isolation transformer + I2S codec ADC) + isolated audio output stage
  (I2S DAC → isolation transformer → line-level TX to COM3 channel) +
  microSD breakout + the annunciator switch.
  The INMP441 mic and MAX98357A amp are bench-test items only; neither is installed.

---

## 2. Master pin map (`board_pins.h`)

| Function | Macro | GPIO | Dir | Net | Notes |
|---|---|---|---|---|---|
| Push-to-talk | `PTT_GPIO` | **0** | in (PU) | control | BOOT button; active-low |
| SELECT switch | `SELECT_GPIO` | **10** | in (PU) | control | IN = GPIO→GND (active-low) |
| Legend OFF (white) | `LEGEND_OFF_GPIO` | **21** | out | lamp | drives top legend half (via driver) |
| Legend FAULT (amber) | `LEGEND_FAULT_GPIO` | **14** | out | lamp | drives bottom legend half (via driver) |
| Status LED | `STATUS_LED_GPIO` | **48** | out | control | on-board RGB on most S3 devkits |
| Mic bit clock | `MIC_BCLK_GPIO` | **4** | out | mic I2S | I2S0 BCLK → mic SCK |
| Mic word select | `MIC_LRCLK_GPIO` | **5** | out | mic I2S | I2S0 WS → mic WS |
| Mic data in | `MIC_DIN_GPIO` | **6** | in | mic I2S | mic SD → ESP DIN |
| SD clock | `SD_CLK_GPIO` | **7** | out | microSD | SDMMC CLK |
| SD command | `SD_CMD_GPIO` | **9** | i/o | microSD | SDMMC CMD (needs pull-up) |
| SD data 0 | `SD_D0_GPIO` | **8** | i/o | microSD | SDMMC DAT0 (needs pull-up) |
| Audio-out bit clock | `AOUT_BCLK_GPIO` | **15** | out | audio-out I2S | I2S1 BCLK → isolated audio-out (COM3) line driver/DAC |
| Audio-out word select | `AOUT_LRCLK_GPIO` | **16** | out | audio-out I2S | I2S1 WS → isolated audio-out (COM3) line driver/DAC |
| Audio-out data | `AOUT_DOUT_GPIO` | **17** | out | audio-out I2S | I2S1 DOUT → isolated audio-out (COM3) DIN; DAC → isolation transformer → line-level TX to COM3-style audio-panel channel. **Bench-test note:** MAX98357A speaker-amp may be substituted here for bench testing only; not the installed output. |

**Polarity macros** (flip to match your hardware):
`PTT_ACTIVE_LOW=1`, `SELECT_ACTIVE_LOW=1`, `LEGEND_OFF_ACTIVE_HIGH=1`,
`LEGEND_FAULT_ACTIVE_HIGH=1`, `STATUS_LED_ACTIVE_HIGH=1`. `LAMP_TEST_MS=2000`.

> Set any unused output to `-1` in `board_pins.h` to disable it cleanly.

### Reserved / avoid pins (ESP32-S3-WROOM-1 N16R8)

| Pins | Reason |
|---|---|
| **GPIO33–37** | Octal PSRAM/flash internal bus — **do not use** on R8 modules |
| **GPIO19, GPIO20** | USB D-/D+ (native USB / USB-Serial-JTAG) |
| **GPIO0, 45, 46** | Strapping pins — usable but must be in the correct state at boot |
| **GPIO26–32** | SPI flash on some modules — verify your board |

GPIO0 is used here only as the BOOT/PTT button (its natural strapping use), so it
is safe. None of the chosen pins above conflict with the reserved set.

---

## 3. Per-device wiring

### 3.1 INMP441 MEMS microphone → ESP32-S3 (I2S_NUM_0)
Supply **1.8–3.3 V** (never 5 V), ~2.2–2.5 mA at 3.3 V. ([INMP441 datasheet](https://www.farnell.com/datasheets/1824785.pdf))

| INMP441 pin | Connects to | Net |
|---|---|---|
| VDD | ESP **3V3** | 3.3 V |
| GND | ESP **GND** | GND |
| SCK | ESP **GPIO4** (BCLK) | mic I2S |
| WS | ESP **GPIO5** (WS) | mic I2S |
| SD | ESP **GPIO6** (DIN) | mic I2S |
| L/R | **GND** | — (selects **left** channel) |

- Decouple VDD→GND with **0.1 µF** close to the module.
- Add a **100 kΩ pulldown** on the SD line (recommended by the datasheet to
  discharge the bus when tri-stated). Most breakout boards include it.
- Do **not** clock WS/SCK with VDD unpowered (stresses ESD diodes).

### 3.2 Isolated audio output stage → COM3-style audio-panel channel (I2S_NUM_1) — installed output

The installed output is a galvanically-isolated, line-level output stage on I2S_NUM_1
(GPIO15 BCLK, GPIO16 LRC, GPIO17 DOUT). Chain: ESP32-S3 I2S DAC → I2S-to-analog
DAC/line driver (e.g. PCM5102A class) → line-level isolation transformer → line-level TX
to dedicated COM3-style audio-panel input channel. The isolation transformer provides
galvanic isolation; a device fault **cannot key, jam, load, or back-feed** the panel's
other channels or required COM radios.

**Bench-test-only option — MAX98357A Class-D amplifier.** For bench verification before
the isolated output stage is fitted, a MAX98357A may be wired on GPIO15/16/17.
Supply **2.5–5.5 V**; 2.4 mA quiescent; peak speaker current up to **~650 mA** at
5 V/4 Ω. **No MCLK required.** ([Analog Devices datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf), [Adafruit guide](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf))
**This bench speaker is NOT routed to the aircraft audio panel and is NOT the installed output.**

| MAX98357A pin | Connects to | Net |
|---|---|---|
| VIN | **5 V** (USB/VBUS) for full output (3.3 V also works, less power) | 5 V |
| GND | ESP **GND** | GND |
| BCLK | ESP **GPIO15** | spk I2S |
| LRC | ESP **GPIO16** | spk I2S |
| DIN | ESP **GPIO17** | spk I2S |
| GAIN | **NC** = 9 dB (default) | — |
| SD (mode) | **float** = mono (L+R)/2 | — |
| OUT+/OUT− | speaker (4–8 Ω) | bridge-tied, no ground ref |

- **GAIN options:** 100 kΩ→GND = 15 dB; →GND = 12 dB; **NC = 9 dB**; →VIN = 6 dB;
  100 kΩ→VIN = 3 dB.
- **SD/mode pin:** <0.16 V = shutdown; 0.16–0.77 V = (L+R)/2 mono; 0.77–1.4 V = right;
  >1.4 V = left. Breakouts usually have a 1 MΩ to VIN giving mono — leave floating.
- The OUT pins are **bridge-tied** — never connect either to GND.

### 3.3 microSD card → ESP32-S3 (SDMMC, 1-bit)
**3.3 V** card. Sleep ~100–200 µA; init/read peaks **50–200 mA**. ([SD current notes](https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975))

| SD signal | ESP32-S3 | Net | Pull-up |
|---|---|---|---|
| CLK | **GPIO7** | microSD | — |
| CMD | **GPIO9** | microSD | **10 kΩ → 3V3** |
| DAT0 | **GPIO8** | microSD | **10 kΩ → 3V3** |
| VDD | **3V3** | 3.3 V | — |
| VSS | **GND** | GND | — |

- 1-bit mode uses only DAT0 (DAT1–3 unused). For 4-bit, add DAT1/2/3 with pull-ups.
- Keep CLK trace short; SDMMC runs at MHz clocks.
- Format **FAT32**. Layout and JSON schema are in the firmware README.

### 3.4 Discrete inputs
| Input | ESP32-S3 | Active | Idle |
|---|---|---|---|
| SELECT switch (IN/OUT) | **GPIO10** | LOW = selected IN | internal pull-up → HIGH = OUT |
| Push-to-talk | **GPIO0** | LOW = pressed | internal pull-up → HIGH |

Wire each as a simple SPST contact to **GND**. No external resistor needed
(internal pull-ups enabled in firmware). Debounce is handled in software.

---

## 4. The annunciator switch (Applied Avionics split-legend)

Two independently driven legend halves, dark-cockpit philosophy per
[FAA AC 25-11B](https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf)
and the [AEA design guidance](https://aea.net/AvionicsNews/ANArchives/DesignDisplayOct03.pdf):

| State | TOP — white **VOICE CHKLST OFF** | BOTTOM — amber **VOICE CHKLST FAULT** |
|---|---|---|
| Selected **IN**, healthy | dark | dark ← true dark cockpit |
| Selected **IN**, fault | dark | **amber ON** |
| Selected **OUT** | **white ON** | dark (fault inhibited) |

- **Power-up lamp test:** both halves on for `LAMP_TEST_MS` (~2 s) so a dead LED
  cannot be mistaken for a healthy dark state, then dark.
- **OUT inhibits fault:** a deliberately deselected system needs no crew action, so
  AC 25-11 keeps the amber caution off; only the white OFF status shows. Recognition
  and fault monitoring are suspended while OUT.

### 4.1 VIVISUN voltage options
Applied Avionics VIVISUN / Korry lighted pushbuttons are offered in **28 VDC, 5 VDC,
28 VAC, 5 VAC, 115 V** lamp variants. ([Applied Avionics](https://www.appliedavionics.com/led-lighted-pushbutton-switches.html))
**An ESP32 GPIO cannot drive a 28 V (or even 5 V at lamp current) legend directly** —
use a low-side driver per half (below). For a quick bench mock-up, substitute two
ordinary 3.3 V LEDs (white + amber) with series resistors driven straight from
GPIO21/GPIO14, observing the ~20 mA GPIO limit.

### 4.2 Lamp-driver circuit (one per legend half)
ESP32-S3 GPIO sources ~20 mA default (40 mA max, configurable), with a **1.5 A total**
chip limit. ([ESP32 GPIO current](https://esp32.com/viewtopic.php?t=20097)) Legend lamps
need their own supply and a switch device:

```
            +V_lamp (5 V or 28 V, separate rail)
                  |
              [ legend lamp ]        <- VIVISUN legend (white or amber)
                  |
                  +------------------ Drain
   GPIO21 --[1k]--|G   N-ch MOSFET (logic-level, e.g. 2N7002 / AO3400)
   (or G14)       |    or NPN (e.g. 2N2222 with base resistor)
              [10k]                  <- gate/base pulldown -> GND (defined OFF)
                  |
                 GND  (Source) ------ common ground with ESP32
```

- One driver for **GPIO21** (OFF/white half), one for **GPIO14** (FAULT/amber half).
- **10 kΩ gate/base pulldown** guarantees the lamp is OFF during boot/reset before the
  GPIO is configured (important for dark-cockpit integrity).
- Choose a MOSFET/transistor and supply rated for the lamp current and voltage. For a
  28 V incandescent legend, ensure the FET Vds rating ≥ 40 V and current ≥ lamp inrush.
- Tie the **lamp supply ground to the ESP32 ground** (single common ground).

---

## 5. Power budget & supply

| Rail | Loads | Typical | Peak |
|---|---|---|---|
| **3.3 V** | ESP32-S3 + Wi-Fi off + audio codec + audio output DAC/line driver + microSD | ~90–180 mA | ~290 mA (SD init / SR burst) |
| **5 V** | Audio output line driver (installed; typically low-current line-level stage) | a few mA | ~50 mA (varies; **not the ~650 mA speaker-amp figure** — speaker amp removed) |
| **Lamp rail** | up to 2 legend halves | 0 (dark) | per lamp spec (e.g. 28 V incand.) |

- Power the board from **USB 5 V capable of ≥ 1 A** (the removed MAX98357A was the
  dominant load; the new isolated output stage is much lower current).
- Keep the **legend-lamp supply separate** from the logic 5 V if using 28 V lamps;
  only the grounds are common.
- Add bulk decoupling: **≥ 100 µF** near the output line driver (if applicable) plus
  0.1 µF per device.

---

## 6. Bill of materials (DIY build)

| Qty | Part | Spec / example | Approx. |
|---|---|---|---|
| 1 | ESP32-S3 DevKit | DevKitC-1 **N16R8** (PSRAM!) | $12–18 |
| 1 | Audio-panel input codec | I2S codec ADC with line-in: **ES8388/ES7210** (MCLK+I2C) or **PCM1808/CS5343** (self-clocking) | $5–12 |
| 1 | **Audio isolation transformer** (input) | 600Ω:600Ω aviation audio ground-loop isolator (**Allen Avionics AGL** series) | varies |
| 1 | **Audio output isolation transformer** | 600Ω:600Ω line-level isolation transformer for TX output stage (e.g. Allen Avionics AGL series or equivalent) | varies |
| 1 | **Audio output DAC / line driver** | I2S DAC IC (e.g. PCM5102A class) for COM3 output stage | $5–10 |
| *(bench only)* | I2S amp | **MAX98357A** breakout — bench-test use only; not installed | $4–7 |
| *(bench only)* | Speaker | 4–8 Ω, ≥ 2 W — bench-test use only; not installed | $2–5 |
| 1 | microSD card + breakout | FAT32; Korvo-2 has on-board slot | $5–8 |
| 1 | Annunciator switch | Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench) | varies |
| 2 | Lamp driver | logic-level N-MOSFET (2N7002/AO3400) **or** NPN (2N2222) | <$1 |
| 4 | Resistors | 1 kΩ ×2 (gate), 10 kΩ ×2 (pulldown) | <$1 |
| 2–3 | Pull-ups | 10 kΩ on SD CMD/DAT0 (if breakout lacks them) | <$1 |
| — | Caps | 0.1 µF per device, 100 µF bulk near output line driver (if applicable) | <$1 |
| 1 | PTT button | momentary SPST (or use BOOT) | <$1 |

**Integrated alternative:** ESP32-S3-Korvo-2 (~$45–55) provides codec/SD on-board;
use its BSP pin map and the ES8311 codec init, repurpose its line-in for the audio-panel
receive feed, and add the isolated COM3 output stage externally (DAC/line driver +
output isolation transformer).

---

## 7. Korvo-2 differences (integrated build)

- Audio codec is **ES8311** (I2C control + I2S data). Initialize over I2C (see
  `esp_codec_dev`/BSP). The NS4150 speaker amp on the board is **not used** in the
  installed configuration (speaker removed); the isolated COM3 output stage is added
  externally on the AOUT_BCLK/LRCLK/DOUT lines (GPIO15/16/17).
- **Dual mics** feed the AFE → markedly better recognition in noise than one INMP441
  (bench-test input only; installed input is the audio-panel tap).
- microSD slot is wired on the board; map `SD_*` pins to the Korvo-2 schematic.
- Expose the annunciator on free header GPIOs; keep the same firmware logic.

---

## 8. Firmware build notes

| Topic | Value |
|---|---|
| Framework | **ESP-IDF ≥ 5.2** |
| Components | `esp-sr`, `esp_spiffs`, `driver`, `json` (cJSON), `fatfs`, `sdmmc`, `esp_driver_sdmmc` |
| Speech models | WakeNet `WN9_HIESP`; MultiNet English `mn6_en`/`mn7_en` (S3 only) |
| Partitions | factory app 3 MB + model 5 MB + storage(UI clips) 2 MB → needs **16 MB** flash |
| MultiNet phrases | lowercase letters + single spaces only; spell numbers ("v one"); ~200 cmd cap |
| Fault behavior | any SD/parse/validation/audio fault → `ST_FAULT`, amber legend, no checklist shown |

> **Important:** the partition table assumes a **16 MB** flash part (N16R8). An 8 MB
> module will not fit the 3 MB app + 5 MB model + 2 MB storage layout.

---

## 9. Processor selection

### 9.1 What this application actually needs

This is **not** a general dictation device. The workload is narrow and well bounded:

| Requirement | Implication |
|---|---|
| **Small, fixed vocabulary** | ~13 checklist triggers + a handful of universal advance words = well under the ~200-command MultiNet cap. No large-vocabulary STT needed. |
| **Offline, no connectivity** | A safety/training device should not depend on WiFi, BT, or cloud. Connectivity is a liability, not a feature. |
| **Deterministic + safe** | Must revert to a safe (unopened) state on any fault; single-chip, well-understood toolchain reduces failure surface. |
| **Dark-cockpit annunciation** | A few GPIO + I2S in/out + SD. No high-end peripherals required. |
| **Low cost, mature tooling** | Demo/training hardware; reproducible by the user with off-the-shelf parts. |

The net: command-recognition on a fixed grammar, not open-ended transcription. That keeps an MCU-class part firmly in scope and makes a Linux SBC overkill.

### 9.2 Recommendation

**Keep the ESP32-S3 as the baseline; consider the ESP32-P4 only if you want more headroom.** Espressif's ESP-SR (v2.1+) explicitly supports **S3 and P4** for English MultiNet command recognition, running wake word + AEC/NS + intent on a single chip. The classic ESP32 is no longer supported by the current speech algorithms, so it should be avoided.

- **ESP32-S3 (recommended baseline):** Xtensa LX7 dual-core @240 MHz with AI vector instructions, 512 KB SRAM, WiFi+BLE, ~$8–15. Rated the best AI/voice part in the ESP line, most mature tooling, runs `mn6_en`/`mn7_en`. The web/firmware, wiring diagram, and BOM are already built around it. ([Espressif ESP-SR](https://docs.espressif.com/projects/esp-sr/en/latest/esp32s3/index.html), [espboards.dev](https://www.espboards.dev/blog/esp32-soc-options/))
- **ESP32-P4 (upgrade path):** dual-core RISC-V up to **400 MHz** + AI instructions + a 40 MHz low-power core, 768 KB SRAM, ~2.5× the compute of the S3, runs `mn7_en`. **No WiFi/BT** — which for a safety device is arguably a *plus* (removes an attack/distraction surface). The trade-off is needing a companion radio if you ever wanted connectivity, and slightly less mature tooling. Good choice if you later add a display or more audio processing. ([Espressif ESP32-P4](https://www.espressif.com/en/products/socs/esp32-p4), [Elecrow P4 vs S3](https://www.elecrow.com/blog/who-is-the-true-performance-king-esp32-p4-vs-esp32-s3.html))

For this fixed-vocabulary workload the S3 has ample margin, so the P4 is a "want more headroom / future display" upgrade rather than a necessity.

### 9.3 Alternatives considered (and why not, for this build)

| Option | What it is | Verdict for this app |
|---|---|---|
| **Syntiant NDP120** (Arduino Nicla Voice) | Always-on Neural Decision Processor, ultra-low-power, embedded Cortex-M0 | Excellent for battery always-on wake-word; overkill/awkward here since we have panel power and need full command grammar + audio playback + SD. ([Syntiant](https://www.syntiant.com/ndp120)) |
| **Picovoice Porcupine + Rhino** | Wake-word + speech-to-intent, offline on Arm Cortex-M4 | Technically a clean fit for fixed grammar, but requires a per-deployment **AccessKey** (license dependency) — undesirable for a self-contained demo. ([Picovoice](https://picovoice.ai/blog/keyword-spotting-on-microcontrollers/)) |
| **Fluent.ai** | End-to-end speech-to-intent on Cortex-M4 @100 MHz, multilingual | Good for productized multilingual intent; commercial licensing, less open tooling than ESP-SR. |
| **NXP i.MX RT600** | Cortex-M33 @300 MHz + Cadence HiFi4 DSP @600 MHz, 4.5 MB SRAM | Strong audio DSP, but more complex board + toolchain than needed for a fixed 13-checklist grammar. |
| **Raspberry Pi** (whisper.cpp / Vosk) | Full offline STT on Linux | Real large-vocabulary transcription, but Linux boot, higher power/cost, non-deterministic boot — overkill and less robust for a fixed-grammar safety device. |

**Bottom line:** the ESP32-S3 remains the right baseline; the ESP32-P4 is the only "strictly better" silicon in the same family and is worth it only if you want extra compute or a display. The dedicated voice chips (Syntiant, Picovoice, Fluent.ai) and the Pi solve problems this app doesn't have.

> *DEMO/TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.*

---

## 10. Source references

- INMP441 microphone datasheet — [Farnell/InvenSense](https://www.farnell.com/datasheets/1824785.pdf)
- MAX98357A amplifier datasheet — [Analog Devices](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf); [Adafruit guide](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf)
- ESP32-S3 GPIO drive current — [Espressif forum](https://esp32.com/viewtopic.php?t=20097); [GPIO reference](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html)
- ESP32-S3 reserved/strapping pins (R8 octal) — [Arduino forum summary](https://forum.arduino.cc/t/advice-on-using-all-pins-of-an-esp32-s3-devkit/1294310)
- microSD operating current — [Arduino forum](https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975)
- VIVISUN lamp voltage options — [Applied Avionics](https://www.appliedavionics.com/led-lighted-pushbutton-switches.html)
- Annunciation color/dark-cockpit guidance — [FAA AC 25-11B](https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf); [AEA design article](https://aea.net/AvionicsNews/ANArchives/DesignDisplayOct03.pdf)
