# CJ2 Voice Emergency Checklist — ESP32-S3 Firmware

Offline, on-device version of the [web demo](../README.md), running on an **ESP32-S3**
using Espressif's **ESP-SR** speech framework (**WakeNet** wake word + **MultiNet**
offline English command recognition). No cloud, no Wi-Fi, no phone.

The pilot says an emergency (after the wake word **"Hi ESP"** or while holding a
**push-to-talk** button); the board reads each checklist item aloud from pre-recorded
audio clips and waits for the spoken completion word before advancing.

Checklist data lives on a **removable microSD card** (one folder per aircraft), so the
same hardware is configured for any airplane and updated by swapping the card. Per the
FAA-aligned safety rule, if the card is missing or its data is invalid the device
**refuses to present any checklist** and annunciates a fault — it never shows a partial
or stale list. System status is shown on an **Applied Avionics split-legend annunciator
switch** following **dark-cockpit philosophy**: nothing is lit when the system is on and
healthy.

> ⚠️ **DEMO / TRAINING USE ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**

> 📐 **Wiring diagram & full electrical data:** see [`docs/wiring_diagram.png`](docs/wiring_diagram.png)
> and [`docs/TECH_DATA.md`](docs/TECH_DATA.md) (master pin map, per-device wiring, power
> budget, BOM, and the legend lamp-driver circuit).

---

## 1. Hardware you need

### Recommended: one all-in-one board (easiest)
| Item | Why | Approx. |
|---|---|---|
| **ESP32-S3-Korvo-2** dev board | Purpose-built for ESP-SR: dual-mic array, **ES8311 codec**, **NS4150 3 W amp**, speaker header, 8 MB PSRAM + 16 MB flash. No wiring. | ~$45–55 |
| **Small 4–8 Ω speaker** (often included) | Audio readout | ~$3 |
| **USB-C cable** | Flashing + power | — |
| **Momentary push-button** (optional) | Push-to-talk (or use an onboard button) | ~$1 |

This is the path the firmware targets by default for the audio codec, and what I'd
buy for a clean demo. Adafruit and Mouser/DigiKey stock the Korvo-2.

### DIY alternative (cheaper, more wiring)
| Item | Notes |
|---|---|
| **ESP32-S3 DevKitC-1 (N8R8 or N16R8)** | Must have **PSRAM** — ESP-SR requires it. The "R8" = 8 MB PSRAM. ~$15 |
| **INMP441** or **ICS-43434** I2S MEMS mic | Digital mic, 16 kHz. ~$5 |
| **MAX98357A** I2S class-D amp + **4–8 Ω speaker** | Audio out. ~$6 |
| **microSD card** (FAT32) + breakout/slot | Holds the aircraft checklist data + audio. The Korvo-2 has an onboard slot. ~$5 |
| **Applied Avionics VIVISUN / Korry split-legend switch** (optional) | Panel annunciator switch with two driven legend halves. Any 2-LED + SPST switch works for a bench demo. |
| Jumper wires / breadboard | — |

> ❗ The classic **ESP32 (non-S3) will not work** for English commands — Espressif's
> English MultiNet models exist only for the **ESP32-S3** (and ESP32-P4).

### DIY wiring (defaults in `main/board_pins.h`)
```
INMP441 mic (I2S0)        MAX98357A amp (I2S1)
  VDD -> 3V3                VIN -> 5V (or 3V3)
  GND -> GND                GND -> GND
  SCK -> GPIO4  (BCLK)      BCLK-> GPIO15
  WS  -> GPIO5  (LRCLK)     LRC -> GPIO16
  SD  -> GPIO6  (DIN)       DIN -> GPIO17
  L/R -> GND (left)         GAIN-> (see note)  SD -> float (mono)

microSD (SDMMC 1-bit)     Applied Avionics split-legend switch
  CLK -> GPIO7              SELECT contact -> GPIO10 to GND (IN=closed)
  CMD -> GPIO9              TOP   legend "VOICE CHKLST OFF"  -> GPIO21 (white)
  D0  -> GPIO8              BOTTOM legend "VOICE CHKLST FAULT"-> GPIO14 (amber)
  VDD -> 3V3, GND -> GND    (drive lamps via a transistor/lamp driver if >~10 mA)

Push-to-talk button: GPIO0 (BOOT) to GND, or any GPIO -> GND (active-low).
```
Change any pin in `board_pins.h`. For the **Korvo-2**, use its BSP pin map and the
ES8311 codec init (see *Adapting for the Korvo-2 codec* below); the Korvo-2's onboard
microSD slot maps to the SD pins.

---

## 2. Software prerequisites

- **ESP-IDF v5.2 or newer** — [install guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/).
- **esp-sr** is pulled automatically as a managed component (`main/idf_component.yml`).
- A TTS tool to render the spoken clips (one of): macOS `say`, `espeak-ng`, or
  [piper](https://github.com/rhasspy/piper) (best quality, offline).

---

## 3. Build & flash

```bash
cd firmware

# 1) Render the spoken checklist clips into ./audio (pick your TTS engine):
python3 scripts/make_audio.py --engine say                 # macOS
# or:  python3 scripts/make_audio.py --engine espeak
# or:  python3 scripts/make_audio.py --engine piper --voice /path/en_US-amy-medium.onnx

# 2) Target the S3 and build/flash (models + audio are embedded automatically):
idf.py set-target esp32s3
idf.py menuconfig          # optional — defaults already select Hi ESP + mn6_en
idf.py build flash monitor
```

`sdkconfig.defaults` already enables PSRAM, the 8 MB flash layout, the **"Hi ESP"**
wake word, and the **English MultiNet 6** model. The custom `partitions.csv` reserves
a `model` partition (speech models) and a `storage` partition (your audio clips).

---

## 4. The annunciator switch (dark-cockpit philosophy)

The system status is shown on an **Applied Avionics split-legend switch** with two
independently driven legend halves, following **dark-cockpit philosophy** (FAA AC 25-11):
*the absence of light means everything is normal.*

| State | TOP half (white **VOICE CHKLST OFF**) | BOTTOM half (amber **VOICE CHKLST FAULT**) |
|---|---|---|
| Selected **IN**, healthy | dark | dark &larr; true dark cockpit |
| Selected **IN**, fault | dark | **amber ON** |
| Selected **OUT** (deselected) | **white ON** | dark (fault inhibited) |

- **SELECT switch** is a physical discrete input (GPIO10). Selected IN = system on;
  selected OUT = system off.
- When **selected OUT**, the system is intentionally off, so per AC 25-11 the amber
  caution is **inhibited** (no crew action is required for a deliberately-off system) —
  only the white OFF legend shows. Voice recognition and fault monitoring are suspended
  until the switch is selected back IN.
- A **fault** (no card, no aircraft folder, bad/missing data, or a missing audio clip)
  lights the amber FAULT half *and* annunciates the cause audibly. The device keeps
  retrying, so reinserting a good card clears the fault automatically.
- At **power-up** both halves illuminate for ~2 s (a **lamp test**) so a burned-out LED
  can never be mistaken for a healthy dark state. Adjust `LAMP_TEST_MS` in `board_pins.h`.

The legend GPIOs are plain digital outputs; drive a panel lamp or relay through a
transistor/lamp driver if it needs more than the GPIO's current limit. Set any unused
legend or the SELECT pin to `-1` / always-IN in `board_pins.h` for a software-only demo.

---

## 5. Using it

0. **Select the switch IN.** (If OUT, the white **VOICE CHKLST OFF** legend is lit and
   the system ignores voice.)
1. **Wake**: say **"Hi ESP"** (or hold the push-to-talk button).
2. **State the emergency**: e.g. *"engine fire"*, *"emergency evacuation"*, *"cabin altitude"*.
3. The board reads the first item aloud, then listens.
4. **Say the completion word** shown for that item (e.g. *"idle"*, *"push"*), or a
   universal word: **"check" / "complete" / "next"**. It advances and reads the next item.
5. At the end it announces **"Checklist complete"** and returns to the home state.
6. Say **"reset"** any time to start over.

Push-to-talk keeps the mic listening only while held (best in a noisy cockpit/intercom);
the wake word is the hands-free alternative.

---

## 6. The microSD card (aircraft configuration)

Checklist data is loaded from the card at boot. Layout:

```
/sdcard/
  config.txt                 (optional) one line:  AIRCRAFT=CJ2
  CJ2/
    checklists.json          the checklist data (schema below)
    audio/
      engine_fire_1.wav      one 16-bit/16 kHz/mono WAV per item "clip"
      engine_fire_2.wav
      ready.wav  complete.wav ...
```

- **Auto-select**: if the card has exactly **one** aircraft folder it loads automatically
  — `config.txt` is only needed when **multiple** folders are present (it names the one
  to use). There is **no compiled-in fallback**: data comes only from the card.
- A ready-to-copy template is in **`sdcard_template/`** (CJ2 with 13 example checklists).
  Generate/refresh it with `python3 scripts/build_aircraft.py`, then copy the contents to
  the card root and render the audio into the aircraft's `audio/` folder.

### `checklists.json` schema
```json
{
  "aircraft": "CJ2",
  "universal_advance": ["check", "checked", "complete", "next"],
  "checklists": [
    {
      "id": "engine_fire",
      "title": "Engine Fire",
      "triggers": ["engine fire"],
      "items": [
        { "clip": "engine_fire_1", "text": "Throttle ... idle", "advance": ["idle"] }
      ]
    }
  ]
}
```
**Voice-phrase rule** (all `triggers`, `advance`, `universal_advance`): **lowercase
letters and single spaces only** — no digits or punctuation (MultiNet limitation). Spell
numbers as words ("v one"). `clip` is the WAV basename in `audio/`. Limits: ≤ `MAX_ITEMS`
items per checklist, ≤ `MAX_TRIGGERS` triggers, ≤ `MAX_ADVANCE` advance words per item
(see `checklists.h`). The loader **validates the whole file and verifies every audio clip
exists** before going live; any violation = FAULT, and no checklist is presented.

---

## 7. How the firmware is organised

```
firmware/
  main/
    main.c             AFE + WakeNet + MultiNet pipeline, PTT, SELECT switch, state machine
    checklists.h       structs + UNIVERSAL_ADVANCE globals (data now comes from SD)
    checklists.c       UNIVERSAL_ADVANCE definition (legacy compiled data kept for ref)
    checklist_store.c/.h  mounts SD, selects aircraft, parses+validates JSON, checks audio
    audio_player.c/.h  WAV playback over I2S (by basename or absolute path)
    annunciator.c/.h   split-legend switch logic + power-up lamp test
    board_pins.h       GPIO map incl. SELECT + legend halves (edit for your board)
    idf_component.yml  pulls espressif/esp-sr
    CMakeLists.txt     builds + embeds the UI/fault clips into internal SPIFFS
  scripts/make_audio.py     renders the spoken clips (UI/fault + items)
  scripts/build_aircraft.py builds the SD aircraft package (checklists.json)
  sdcard_template/CJ2/       ready-to-copy SD card contents
  partitions.csv     factory app + model + storage(UI clips) partitions
  sdkconfig.defaults model + PSRAM + flash configuration
```

> **Fault-safe loading.** `checklist_store_load()` returns a specific `FAULT_*` code on
> any problem and leaves the table empty; `main.c` then enters `ST_FAULT`, lights the
> amber legend, and annunciates the cause. The UI/fault clips live in **internal SPIFFS**
> (not the card) so the device can still speak a fault even with **no card inserted**.

**State machine** mirrors the web demo: `HOME` recognises a checklist trigger and loads
it; `RUN` recognises each item's advance word and steps forward. To keep recognition
fast and accurate, the firmware **re-registers only the phrases relevant to the current
step** (via `esp_mn_commands_add` + `esp_mn_commands_update`).

### Adapting for the Korvo-2 codec
The default `audio_player.c` drives a **MAX98357A** (no codec setup needed). On the
Korvo-2, initialise the **ES8311** codec over I2C using `esp_codec_dev` (add the
`espressif/esp_codec_dev` managed component), then keep the same I2S write loop. The
mic side already works through ESP-SR's AFE.

---

## 6. Design notes & limits

- **English + ESP32-S3 only.** Other languages need a different MultiNet model
  (Chinese is available; others require TFLite Micro custom training).
- **MultiNet command rules**: letters + spaces only — no digits or punctuation. That's
  why numbers are spelled out ("v one", "two hundred") in `checklists.c`.
- **~200 command cap.** This demo registers far fewer at any moment (only the active
  step's words), so there's plenty of headroom.
- **No on-device TTS** — readout uses pre-rendered WAV clips. Re-run `make_audio.py`
  after editing any wording.
- The **Emergency Evacuation branch** (cabin door vs emergency exit) is flattened into a
  single decision step; saying either option advances. A true branch is easy to add in
  `handle_phrase()` if you want separate paths.

---

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| **"No English MultiNet model"** at boot | In `idf.py menuconfig` → *ESP Speech Recognition*, enable an English model (`mn6_en`). Rebuild. |
| **Build fails on PSRAM/heap** | Use an **R8** S3 module (has PSRAM) and keep `CONFIG_SPIRAM=y`. The Korvo-2 and DevKitC-1-N16R8 qualify. |
| **No audio / silence** | Check amp wiring (DIN/BCLK/LRC), speaker 4–8 Ω, MAX98357A SD pin floating, and that `make_audio.py` actually wrote files to `audio/`. |
| **"clip not found"** in log | You flashed before generating clips, or an item's `clip` has no matching WAV on the card. Run `make_audio.py` / refresh the card's `audio/` folder. |
| **Amber FAULT legend stays lit** | Check the card is inserted/FAT32, has one aircraft folder (or a `config.txt` `AIRCRAFT=`), and `checklists.json` is valid. The serial log prints the exact `FAULT_*` cause. |
| **Both legend halves stay on** | That's the ~2 s power-up lamp test; they should go dark after. If they never change, check the legend GPIO wiring (GPIO21/GPIO14). |
| **White OFF legend won't clear** | The SELECT switch reads OUT. Verify GPIO10 is pulled to GND when selected IN (active-low), or flip `SELECT_ACTIVE_LOW`. |
| **"No aircraft folder" fault** | Card root needs exactly one aircraft subfolder, or a `config.txt` line `AIRCRAFT=<folder>` when several exist. |
| **Poor recognition** | Speak clearly, reduce background noise, keep phrases short. The dual-mic Korvo-2 is far better than a single INMP441 in noise. |
| **Wake word never triggers** | Confirm `CONFIG_SR_WN_WN9_HIESP=y`; say "Hi ESP" clearly, or just use push-to-talk. |
| **Mic reads garbage** | Verify INMP441 L/R pin is grounded (left channel) and SD→DIN GPIO matches `board_pins.h`. |

---

## License
MIT (see repo root `LICENSE`). Checklist text reproduced for demonstration/training only.
