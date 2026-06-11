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
| Mic input | I2S MEMS microphone on **I2S_NUM_0** |
| Audio output | I2S Class-D amplifier on **I2S_NUM_1** → 4–8 Ω speaker |
| Config storage | **microSD** (SDMMC 1-bit), FAT32, one folder per aircraft |
| Annunciation | Applied Avionics split-legend switch (dark-cockpit, FAA AC 25-11) |
| Logic level | **3.3 V** (ESP32-S3 is **not** 5 V tolerant on GPIO) |

Two build paths are supported:

- **Integrated:** **ESP32-S3-Korvo-2** dev board (on-board dual mic, ES8311 codec,
  NS4150 amp, microSD slot). Least wiring; best mic performance.
- **DIY (this document):** ESP32-S3 DevKitC-1 N16R8 + INMP441 mic + MAX98357A amp +
  microSD breakout + the annunciator switch.

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
| Speaker bit clock | `SPK_BCLK_GPIO` | **15** | out | spk I2S | I2S1 BCLK → amp BCLK |
| Speaker word select | `SPK_LRCLK_GPIO` | **16** | out | spk I2S | I2S1 WS → amp LRC |
| Speaker data out | `SPK_DOUT_GPIO` | **17** | out | spk I2S | I2S1 DOUT → amp DIN |

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

### 3.2 MAX98357A Class-D amplifier → ESP32-S3 (I2S_NUM_1)
Supply **2.5–5.5 V**; 2.4 mA quiescent; peak speaker current up to **~650 mA** at
5 V/4 Ω. **No MCLK required.** ([Analog Devices datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf), [Adafruit guide](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf))

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
| **3.3 V** | ESP32-S3 + Wi-Fi off + mic + microSD | ~80–150 mA | ~250 mA (SD init / SR burst) |
| **5 V** | MAX98357A speaker output | a few mA idle | **~650 mA** (5 V/4 Ω, loud) |
| **Lamp rail** | up to 2 legend halves | 0 (dark) | per lamp spec (e.g. 28 V incand.) |

- Power the board from **USB 5 V capable of ≥ 1 A** (the on-board 3.3 V LDO feeds the
  S3, mic, and SD). Reserve headroom for the amp's peak.
- Keep the **legend-lamp supply separate** from the logic 5 V if using 28 V lamps;
  only the grounds are common.
- Add bulk decoupling: **≥ 100 µF** near the amp VIN plus 0.1 µF per device.

---

## 6. Bill of materials (DIY build)

| Qty | Part | Spec / example | Approx. |
|---|---|---|---|
| 1 | ESP32-S3 DevKit | DevKitC-1 **N16R8** (PSRAM!) | $12–18 |
| 1 | I2S MEMS mic | **INMP441** or ICS-43434 breakout | $4–6 |
| 1 | I2S amp | **MAX98357A** breakout | $4–7 |
| 1 | Speaker | 4–8 Ω, ≥ 2 W | $2–5 |
| 1 | microSD card + breakout | FAT32; Korvo-2 has on-board slot | $5–8 |
| 1 | Annunciator switch | Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench) | varies |
| 2 | Lamp driver | logic-level N-MOSFET (2N7002/AO3400) **or** NPN (2N2222) | <$1 |
| 4 | Resistors | 1 kΩ ×2 (gate), 10 kΩ ×2 (pulldown) | <$1 |
| 2–3 | Pull-ups | 10 kΩ on SD CMD/DAT0 (if breakout lacks them) | <$1 |
| — | Caps | 0.1 µF per device, 100 µF bulk near amp | <$1 |
| 1 | PTT button | momentary SPST (or use BOOT) | <$1 |

**Integrated alternative:** ESP32-S3-Korvo-2 (~$45–55) replaces the mic/codec/amp/SD
items above; use its BSP pin map and the ES8311 codec init.

---

## 7. Korvo-2 differences (integrated build)

- Audio codec is **ES8311** (I2C control + I2S data) with an **NS4150** speaker amp —
  not the MAX98357A path. Initialize the codec over I2C (see `esp_codec_dev`/BSP).
- **Dual mics** feed the AFE → markedly better recognition in noise than one INMP441.
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

## 9. Source references

- INMP441 microphone datasheet — [Farnell/InvenSense](https://www.farnell.com/datasheets/1824785.pdf)
- MAX98357A amplifier datasheet — [Analog Devices](https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf); [Adafruit guide](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf)
- ESP32-S3 GPIO drive current — [Espressif forum](https://esp32.com/viewtopic.php?t=20097); [GPIO reference](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html)
- ESP32-S3 reserved/strapping pins (R8 octal) — [Arduino forum summary](https://forum.arduino.cc/t/advice-on-using-all-pins-of-an-esp32-s3-devkit/1294310)
- microSD operating current — [Arduino forum](https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975)
- VIVISUN lamp voltage options — [Applied Avionics](https://www.appliedavionics.com/led-lighted-pushbutton-switches.html)
- Annunciation color/dark-cockpit guidance — [FAA AC 25-11B](https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf); [AEA design article](https://aea.net/AvionicsNews/ANArchives/DesignDisplayOct03.pdf)
