# Voice Emergency Checklist System — Master Technical & Certification Reference

> **DEMO / TRAINING USE ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**
> This document describes a bench / training prototype and a *certification-readiness
> roadmap*. As built, the unit is **not airworthy, not certified, and must never be
> installed in or relied upon aboard an aircraft.** Nothing here is an STC, TSO
> authorization, PMA, or NORSEE letter of approval. The certification sections (Part C)
> describe the path a productized unit **would** follow; they are a plan, not a claim of
> compliance.

**Product:** a generic, offline, voice-driven **advisory** emergency-checklist reader.
The pilot states an emergency by name; the device reads each checklist item aloud and
waits for a spoken completion word before advancing. It runs entirely on-device (no
cloud, no Wi-Fi). **The product itself is aircraft-agnostic** — all aircraft-specific
behavior comes from the **Aircraft Card** that is installed (Part B). The Cessna Citation
CJ2 is included only as the reference example card.

**This master reference supersedes and combines** the previously separate documents:
the technical data packet, the processor-selection note, and the enclosure specification.
Those remain in the repository for history; this is the single source of truth.

---

## Document map

| Part | Contents |
|---|---|
| **A. Product** | What the system is, the generic architecture, and the safety model |
| **B. Aircraft Card** | The card-defines-everything model + the formal card specification & validation |
| **C. Certification basis** | NORSEE / DO-160G / installation path, and the deliberate DO-178C-avoidance argument |
| **D. Hardware reference** | Pin map, per-device wiring, annunciator, lamp driver, power, BOM, processor selection |
| **E. Enclosure** | Two-piece mechanical specification for the fabricating engineer |
| **F. References** | All cited regulatory and component sources |

---

# PART A — THE PRODUCT

## A.1 What it is (and is not)

| It **is** | It **is not** |
|---|---|
| An **advisory** read-aloud reader of checklist items | A required or primary aircraft system |
| **Independent** — no electrical/data tie to any aircraft system | An interface to avionics, engines, or controls |
| Driven entirely by an installed **Aircraft Card** | Tied to one airframe in firmware |
| **Offline**, deterministic, single-chip | A cloud / connected / large-vocabulary STT device |
| A **complement** to the certified/required checklist | A substitute for the AFM/QRH or required checklist |

This framing is not cosmetic — it is the foundation of the certification argument in
Part C. A device that is non-required, advisory-only, independent of primary systems, and
fails to a clearly-annunciated safe state is the textbook profile for the **NORSEE**
(Non-Required Safety Enhancing Equipment) approval path, and it is what lets the program
**lean on DO-160G environmental qualification while avoiding DO-178C software assurance.**

## A.2 Generic system architecture

| Block | Function | Aircraft-specific? |
|---|---|---|
| **MCU + speech stack** | Wake word → command recognition → playback sequencing | No — fixed firmware |
| **Microphone (I2S)** | Captures crew speech for recognition | No |
| **Speaker + amplifier (I2S)** | Reads checklist items / annunciations aloud | No |
| **microSD (the Aircraft Card)** | Carries aircraft ID, checklist library, audio, config, validation | **Yes — this is the only aircraft-specific element** |
| **Annunciator switch** | Dark-cockpit status / fault indication, IN/OUT select | No |

The MCU runs Espressif **ESP-SR** (AFE noise-suppression/VAD → WakeNet wake word →
MultiNet fixed-grammar command recognition). The grammar (trigger phrases, advance words)
is small and bounded, which is what keeps an MCU-class part in scope (see D.7).

## A.3 The safety model (carried into the cert argument)

Three design rules define the failure behavior, and each one maps to a NORSEE requirement
(Part C):

1. **Revert-to-unopened.** If the card is missing, unreadable, malformed, fails schema
   validation, or any referenced audio clip is absent, the device **refuses to present any
   checklist** and enters a clearly-annunciated FAULT state. It never shows partial or
   stale data. *(Failure mode = loss of function, not misleading information.)*
2. **Dark-cockpit annunciation.** When selected IN and healthy, the unit shows **nothing**.
   A fault lights the amber FAULT legend. Selected OUT shows the white OFF status and
   **inhibits** the fault legend (a deliberately deselected system needs no crew action).
   A power-up lamp test proves the legend is alive.
3. **Independence.** The device draws power and nothing else from the aircraft; it neither
   reads from nor writes to any aircraft system. Loss of the device cannot affect any
   primary function.

---

# PART B — THE AIRCRAFT CARD (card defines everything)

## B.1 Principle

> **The product is generic. The installed card makes it a specific aircraft's checklist
> reader.** To support a new airframe — King Air, PC-12, TBM, another Citation — you
> author a new card. **No firmware change, no recompile, no hardware change.**

Everything that varies by aircraft lives on the card: the aircraft identity, the checklist
library (titles, trigger phrases, ordered items, per-item completion/advance words), the
read-aloud audio, and the universal advance vocabulary. The firmware contains only the
generic engine that loads, validates, and plays whatever a valid card provides.

## B.2 Card layout (microSD, FAT32)

```
/sdcard/
  config.txt                 (optional) one line: AIRCRAFT=<FOLDER>
  <FOLDER>/                  one folder per aircraft (e.g. CJ2, B200, PC12)
    checklists.json          the card manifest + checklist library
    audio/
      <clip>.wav             one read-aloud clip per referenced item + fault clips
```

- **Auto-select:** if exactly one aircraft folder is present, it loads automatically.
- **Explicit select:** if multiple folders exist, `config.txt` names the active one. A
  missing/invalid target is a fault (revert-to-unopened), not a silent guess.

## B.3 Card manifest schema (`checklists.json`)

Top-level object:

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `schema_version` | integer | rec. | Card schema version the firmware validates against |
| `aircraft` | string | **yes** | Short aircraft id; must match the folder name |
| `title` | string | **yes** | Human-readable aircraft name shown in logs |
| `universal_advance` | string[] | **yes** | Advance words accepted on every item (e.g. check, checked, complete, next) |
| `checklists` | object[] | **yes** | The checklist library (≥ 1) |

Each `checklists[]` entry:

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `id` | string | **yes** | Stable identifier (e.g. `engine_fire`) |
| `title` | string | **yes** | Spoken/displayed checklist name |
| `type` | string | rec. | `emergency`, `abnormal`, `normal` |
| `triggers` | string[] | **yes** | Phrases that invoke this checklist by voice |
| `items` | object[] | **yes** | Ordered checklist steps (≥ 1) |

Each `items[]` entry:

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `clip` | string | **yes** | Audio basename in `audio/` (read-aloud `<clip>.wav`) |
| `text` | string | **yes** | The item text (for logs / optional display) |
| `advance` | string[] | opt. | Item-specific completion words (in addition to `universal_advance`) |

### B.3.1 Voice-grammar rules (validation-enforced)
MultiNet (English) imposes grammar constraints that the card author **must** honor; the
validator rejects a card that violates them (revert-to-unopened):

- Phrases are **lowercase letters and single spaces only** — no digits or punctuation.
- **Spell numbers as words**: "V-one" → `v one`, not `V1`.
- Keep the **total command count modest** (well under the ~200-command MultiNet cap).
- Every `clip` referenced by any item **must** exist as `audio/<clip>.wav`.

## B.4 Card validation & the revert-to-unopened rule

On boot the firmware attempts a **complete, valid** load and returns exactly one status:

| Status | Meaning | Annunciation |
|---|---|---|
| `STORE_OK` | SD mounted, JSON parsed + schema-valid, **every** audio clip present | dark (healthy) |
| `FAULT_NO_CARD` | SD not detected / mount failed | amber FAULT |
| `FAULT_NO_AIRCRAFT` | No aircraft folder, or `config.txt` target missing | amber FAULT |
| `FAULT_NO_JSON` | `checklists.json` missing / unreadable | amber FAULT |
| `FAULT_PARSE` | JSON malformed | amber FAULT |
| `FAULT_VALIDATION` | Schema or voice-rule violation, empty data | amber FAULT |
| `FAULT_AUDIO_MISSING` | A referenced clip is absent | amber FAULT |
| `FAULT_NO_MEMORY` | Allocation failed while loading | amber FAULT |

**On any FAULT the in-memory checklist table is left EMPTY** — the device cannot present a
partial or stale checklist even if asked. This is the literal implementation of "always
revert to unopened if files are not available."

## B.5 Card integrity & provenance (recommended for a productized card)

For a card that drives a *safety-enhancing* device, integrity matters as much as schema
validity. Recommended additions (forward-looking, beyond the current demo):

- **Schema version gate** — firmware refuses a card whose `schema_version` it does not
  support, rather than mis-parsing it.
- **Manifest checksum / signature** — a per-card hash (and, for production, a signature)
  so a corrupted or tampered card is rejected as `FAULT_VALIDATION`.
- **Content provenance** — record, per card, the AFM/QRH source revision the checklist
  text was transcribed from, the author, and the date. Advisory equipment is only as good
  as the source it mirrors; provenance is part of the configuration-control story the FAA
  expects under NORSEE (Part C).
- **Read-only media** — distribute production cards write-protected.

---

# PART C — CERTIFICATION BASIS (STC / PMA / NORSEE-ready reference)

> **Status:** this part is a **roadmap**, not evidence of compliance. The demo unit holds
> no approvals. The intent is to design and document so that a productized unit can pursue
> approval efficiently.

## C.1 Why NORSEE is the right path

The product profile — non-required, advisory, independent of primary systems, failing to a
clearly-annunciated safe state — matches the FAA's **Non-Required Safety Enhancing
Equipment (NORSEE)** policy, **PS-AIR-21.8-1602** (issued 03/31/2016). NORSEE approval is a
**combined design and production approval** issued under **14 CFR § 21.8(d)** for equipment
that is "not required by any Federal regulation with the intent to measurably increase
aircraft safety," determined to be a **minor change to type design** with a **minor failure
condition.** A voice reader that simply reads aloud the same items already in the
certified/required checklist — while the paper/electronic required checklist remains the
authority — is a strong fit. *[Source: FAA PS-AIR-21.8-1602.]*

### C.1.1 Applicability limit (read this)
NORSEE policy **applies to aircraft certified under 14 CFR Part 23, 27, and 29** (and
predecessor categories) and **explicitly excludes Part 25 transport-category aircraft.**

- The reference example, the **Citation CJ2 (525A), is a Part 23 airplane** — so NORSEE is
  available for it.
- Because the product is generic, the card library will inevitably include **Part 25**
  aircraft (e.g. larger jets). **For a Part 25 installation, NORSEE is not available**; that
  installation must use an **STC** (or other major/minor-change path appropriate to the
  airframe). The product's certification status is therefore **per-airframe**, and the
  documentation must say so explicitly. *[Source: FAA PS-AIR-21.8-1602 applicability.]*

## C.2 Minimum Design Requirements (the standards we elect)

Under NORSEE the applicant **proposes the industry standard(s)** that become the Minimum
Design Requirements (MDR); the FAA accepts, partially accepts, or augments them. The FAA
recommends widely-accepted RTCA / SAE / ASTM standards. *[Source: PS-AIR-21.8-1602 §1.1–1.2.]*

**Proposed MDR for this product:**

| Topic | Elected standard / basis | Notes |
|---|---|---|
| **Environmental** | **RTCA/DO-160G** (Environmental Conditions and Test Procedures for Airborne Equipment) | Primary qualification evidence. Categories in C.4. FAA accepts DO-160 D/E/F/G per **AC 21-16G** and "strongly encourages DO-160G for new articles." |
| **Software** | **No DO-178C** sought — see C.3 | Argued out via function/failure classification, not avoided by omission |
| **Complex hardware** | **DO-254 not invoked** | Design uses COTS MCU + simple discrete logic; no custom complex devices (ASIC/FPGA/PLD). Per AC 20-152A, *simple* hardware verifiable by test does not require DO-254 methodical design assurance. |
| **Human factors / annunciation color** | **FAA AC 25-11B** conventions (amber=caution, white=status, dark-cockpit) | Used as accepted design convention even though the unit is not a Part 25 article |
| **System safety (if needed)** | **SAE ARP4761 / AC 23.1309-1** | Only invoked if the safety evaluation ever rises above "minor" (it should not) |

## C.3 The DO-178C-avoidance argument (deliberate, documented)

DO-178C is software *design-assurance* guidance whose rigor scales with the **failure
condition** the software can contribute to. NORSEE lets us classify the function and, for a
genuinely minor-failure advisory device, **scope software assurance down to essentially
nothing formal** — provided the architecture earns it. The argument has four legs:

1. **Function is advisory, not required.** The device does not perform, command, or feed any
   required function. The crew's authority is the certified/required checklist; this unit
   only reads it aloud.
2. **Worst-case failure is minor.** The two credible failures are (a) **loss of function** —
   it goes silent or annunciates FAULT, and the crew uses the paper/QRH exactly as today; and
   (b) **misleading information** — mitigated by the revert-to-unopened rule (no partial/stale
   output), card validation, and a procedural requirement that the crew cross-checks against
   the required checklist. Neither failure reduces the crew's ability to cope with a
   condition worse than minor — the NORSEE safety-evaluation test. *[Source: PS-AIR-21.8-1602
   §1.4.]*
3. **Independence.** No input from or output to any primary system; physical and electrical
   separation. This is one of the design considerations the policy lists for keeping a
   failure minor. *[Source: PS-AIR-21.8-1602 §1.4.]*
4. **Qualitative safety evaluation is permitted** for non-complex equipment; a quantitative
   probabilistic analysis (and the DO-178C machinery that feeds it) is not required for a
   minor-failure advisory function. *[Source: PS-AIR-21.8-1602 §1.4.]*

**Honest caveats (must stay in the doc):**
- This argument **must be agreed with the FAA ACO early** — the applicant proposes the
  classification; the FAA concurs. If the FAA judges the failure condition above minor (e.g.
  because of over-reliance/automation-dependency human factors), the program moves to
  **§2 of the NORSEE policy** (xx.1309, ARP4754A/ARP4761) and software assurance re-enters.
- "No DO-178C" is **earned by architecture and by procedural mitigations**, not by labeling.
  The revert-to-unopened behavior, the validation gate, the dark-cockpit annunciation, the
  independence, and a **mandatory limitation that the unit may not be used as a substitute
  for the required checklist** are the price of that classification.

## C.4 DO-160G environmental qualification plan

Categories a cockpit/avionics-bay unit would target. For the prototype these are **design
targets**, not completed tests. *[Source: RTCA/DO-160G; FAA AC 21-16G.]*

| DO-160G section | Target category | Rationale for this unit |
|---|---|---|
| §4 Temperature & Altitude | **Cat A2** (controlled/pressurized) | −15 °C to +55 °C operating; pressurized cabin |
| §5 Temperature Variation | Cat B | Cockpit rate of change |
| §6 Humidity | **Cat A** | Conformal coat recommended |
| §7 Operational/Crash Shock | Operational + crash-safety | Boards retained; nothing becomes a projectile |
| §8 Vibration | **Cat S** (fixed-wing) | Locking hardware; conformal coat; no press-fit-only parts |
| §15 Magnetic Effect | Class Z | Small device; classify by measured deflection |
| §16 Power Input | per installation (e.g. 28 VDC) | Only if a 28 V variant is built; TVS + fuse |
| §17 Voltage Spike | Cat A | Input transient protection |
| §18 AF Conducted Susceptibility | Cat — | As applicable to the chosen supply |
| §19 Induced Signal Susceptibility | Cat ZC | Cockpit |
| §20 RF Susceptibility | Cat — | Aluminum case + grounded shield |
| §21 RF Emission | **Cat M** (or better) | **Wi-Fi/BT disabled in firmware** materially helps emissions |
| §22 Lightning Induced Transient | as installed | Behind-panel mounting reduces exposure |
| §25 ESD | per §25 | Bond exposed metal; recessed connectors |
| §26 Flammability | UL94 **V-0** materials | Required if not aluminum |

> The deliberate choice to **disable Wi-Fi and Bluetooth in firmware** is both a security
> decision and an emissions-qualification advantage (§21).

## C.5 Approval & installation path (per airframe)

NORSEE approval is **design + production approval — not installation approval.** The full
chain for a Part 23/27/29 airframe:

1. **Pre-application** — engage the responsible FAA **ACO** early; agree on the NORSEE
   classification (minor change / minor failure) and the MDR (C.2).
2. **Design + test** — complete DO-160G qualification, the safety evaluation, human-factors
   assessment, and the configuration-control / card-provenance package.
3. **NORSEE Letter of Approval (LOA)** under **§ 21.8(d)**, with the **certifying statement
   of compliance** (template in C.6) and a quality system per the policy.
4. **Installation** — NORSEE *eligibility* still requires an installation approval on each
   aircraft:
   - If the installation is a **minor alteration**: a logbook entry / FAA Form 337 as
     applicable per the airframe's rules.
   - If it is a **major change** to type design (e.g. panel structure, electrical
     integration): **STC** or field-approval path. *[Source: PS-AIR-21.8-1602; FAA STC/PMA
     guidance.]*
5. **Part 25 aircraft** — skip NORSEE; pursue **STC** for the installation (C.1.1).

### C.5.1 Where TSO and PMA fit (and don't, here)
- **TSO authorization** is a *minimum-performance* design+production approval against a
  specific TSO. **There is no TSO that defines a "voice advisory checklist reader,"** so a
  TSOA is not the natural path; NORSEE (applicant-proposed MDR) is. A TSOA would also still
  require separate installation approval. *[Source: FAA TSO program; PS-AIR-21.8-1602.]*
- **PMA** is for *modification/replacement* articles for a type-certificated product and is
  typically tied to an STC or identicality. This unit is **added** equipment, not a
  replacement part, so PMA is not the primary path — though a production unit may end up
  holding PMA in conjunction with an STC for specific airframes. *[Source: FAA PMA guidance,
  14 CFR § 21.303.]*

## C.6 Certifying statement of compliance (template)

Per the NORSEE policy, the LOA application carries a statement in this form (placeholders to
be completed at application). *Reproduced as a template only — not a current certification.*

> "I, *(authorized representative)*, certify that *(company)* has complied with all
> applicable requirements as identified in *RTCA/DO-160G and the other Minimum Design
> Requirements accepted for this article*, and policy statement **PS-AIR-21.8-1602**, and
> that the article is produced under the required quality system."

Two limitation statements the FAA expects on advisory NORSEE, to be placarded / in the
manual:
> "**No operational credit may be taken for installation of this system.**"
> "**This system is not a required system and may not be used as a substitution for the
> certificated aircraft checklist.**" *[Source: PS-AIR-21.8-1602.]*

## C.7 Compliance summary matrix

| Requirement | Means of compliance | Status (demo) |
|---|---|---|
| Non-required, safety-enhancing | NORSEE PS-AIR-21.8-1602, § 21.8(d) | Argued; not applied |
| Minor change / minor failure | Qualitative safety evaluation (C.3) | Drafted; ACO concurrence pending |
| Environmental | RTCA/DO-160G (C.4) per AC 21-16G | Targets defined; **not tested** |
| Software assurance | **DO-178C not sought** — advisory/minor (C.3) | Architecture supports it; ACO concurrence pending |
| Complex hardware | DO-254 not invoked (simple COTS) — AC 20-152A | N/A by design |
| Human factors / color | AC 25-11B conventions, dark-cockpit | Implemented in design |
| Installation | Minor alteration or STC, per airframe | Per-aircraft; none performed |
| Part 25 airframes | STC (NORSEE excluded) | Flagged |

---

# PART D — HARDWARE REFERENCE

> Pin numbers match `firmware/main/board_pins.h`. The wiring diagram is in
> `firmware/docs/wiring_diagram.png`. Logic level is **3.3 V** (the ESP32-S3 is **not**
> 5 V tolerant on GPIO).

## D.1 System overview

| Item | Value |
|---|---|
| MCU | **ESP32-S3** (dual-core LX7 @ 240 MHz) — **PSRAM required** by ESP-SR |
| Recommended module | ESP32-S3-WROOM-1 **N16R8** (16 MB flash, 8 MB octal PSRAM) |
| Speech stack | Espressif **ESP-SR**: AFE (NS/VAD) → WakeNet "Hi ESP" → MultiNet English |
| Mic input | I2S MEMS microphone on **I2S_NUM_0** |
| Audio output | I2S Class-D amplifier on **I2S_NUM_1** → 4–8 Ω speaker |
| Config storage | **microSD** — the Aircraft Card (Part B), FAT32 |
| Annunciation | Applied Avionics split-legend switch (dark-cockpit, AC 25-11B) |

Two build paths: **Integrated** (ESP32-S3-Korvo-2 dev board — on-board dual mic, ES8311
codec, NS4150 amp, microSD slot; best mic performance) or **DIY** (ESP32-S3 DevKitC-1 N16R8
+ INMP441 mic + MAX98357A amp + microSD breakout + the annunciator switch).

## D.2 Master pin map

| Function | Macro | GPIO | Dir | Notes |
|---|---|---|---|---|
| Push-to-talk | `PTT_GPIO` | 0 | in (PU) | BOOT button; active-low |
| SELECT switch | `SELECT_GPIO` | 10 | in (PU) | IN = GPIO→GND (active-low) |
| Legend OFF (white) | `LEGEND_OFF_GPIO` | 21 | out | top legend half (via driver) |
| Legend FAULT (amber) | `LEGEND_FAULT_GPIO` | 14 | out | bottom legend half (via driver) |
| Status LED | `STATUS_LED_GPIO` | 48 | out | on-board RGB on most S3 devkits |
| Mic bit clock | `MIC_BCLK_GPIO` | 4 | out | I2S0 BCLK → mic SCK |
| Mic word select | `MIC_LRCLK_GPIO` | 5 | out | I2S0 WS → mic WS |
| Mic data in | `MIC_DIN_GPIO` | 6 | in | mic SD → ESP DIN |
| SD clock | `SD_CLK_GPIO` | 7 | out | SDMMC CLK |
| SD command | `SD_CMD_GPIO` | 9 | i/o | SDMMC CMD (needs pull-up) |
| SD data 0 | `SD_D0_GPIO` | 8 | i/o | SDMMC DAT0 (needs pull-up) |
| Speaker bit clock | `SPK_BCLK_GPIO` | 15 | out | I2S1 BCLK → amp BCLK |
| Speaker word select | `SPK_LRCLK_GPIO` | 16 | out | I2S1 WS → amp LRC |
| Speaker data out | `SPK_DOUT_GPIO` | 17 | out | I2S1 DOUT → amp DIN |

**Polarity macros:** `PTT_ACTIVE_LOW=1`, `SELECT_ACTIVE_LOW=1`, `LEGEND_OFF_ACTIVE_HIGH=1`,
`LEGEND_FAULT_ACTIVE_HIGH=1`, `STATUS_LED_ACTIVE_HIGH=1`, `LAMP_TEST_MS=2000`. Set any
unused output to `-1` to disable it cleanly.

**Reserved / avoid pins (N16R8):** GPIO33–37 (octal PSRAM/flash bus — do not use),
GPIO19/20 (USB D-/D+), GPIO0/45/46 (strapping — must boot in the right state),
GPIO26–32 (SPI flash on some modules). GPIO0 here is only the BOOT/PTT button, so it is safe.

## D.3 Per-device wiring

**D.3.1 INMP441 MEMS mic → ESP32-S3 (I2S_NUM_0).** Supply 1.8–3.3 V (never 5 V), ~2.2–2.5 mA.
VDD→3V3, GND→GND, SCK→GPIO4, WS→GPIO5, SD→GPIO6, L/R→GND (left channel). Decouple 0.1 µF;
100 kΩ pulldown on SD; never clock with VDD off.

**D.3.2 MAX98357A Class-D amp → ESP32-S3 (I2S_NUM_1).** Supply 2.5–5.5 V; ~2.4 mA quiescent;
peak ~650 mA at 5 V/4 Ω; no MCLK. VIN→5 V (full output), GND→GND, BCLK→GPIO15, LRC→GPIO16,
DIN→GPIO17, GAIN NC = 9 dB, SD/mode float = mono. **OUT+/OUT− are bridge-tied — never to GND.**

**D.3.3 microSD (the Aircraft Card) → SDMMC 1-bit.** 3.3 V card. CLK→GPIO7, CMD→GPIO9
(10 kΩ→3V3), DAT0→GPIO8 (10 kΩ→3V3), VDD→3V3, VSS→GND. FAT32; layout per Part B.

**D.3.4 Discrete inputs.** SELECT (GPIO10): LOW = selected IN; pull-up HIGH = OUT. PTT
(GPIO0): LOW = pressed. Each is a simple SPST to GND; debounce in software.

## D.4 Annunciator switch (split-legend, dark-cockpit)

| State | TOP — white **VOICE CHKLST OFF** | BOTTOM — amber **VOICE CHKLST FAULT** |
|---|---|---|
| Selected **IN**, healthy | dark | dark ← true dark cockpit |
| Selected **IN**, fault | dark | **amber ON** |
| Selected **OUT** | **white ON** | dark (fault inhibited) |

Power-up **lamp test**: both halves on for ~2 s, then dark, so a dead LED cannot masquerade
as healthy. **OUT inhibits fault** per AC 25-11B — a deselected system needs no crew action,
so only the white OFF status shows; recognition and fault monitoring are suspended while OUT.

## D.5 Lamp-driver circuit (one per legend half)

An ESP32 GPIO (~20 mA default, 40 mA max; 1.5 A total chip limit) **cannot drive a 28 V — or
5 V at lamp current — legend directly.** Use a low-side switch per half:

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

One driver for GPIO21 (OFF/white), one for GPIO14 (FAULT/amber). The 10 kΩ pulldown
guarantees the lamp is OFF during boot/reset before the GPIO is configured (dark-cockpit
integrity). For a 28 V incandescent legend, use a FET with Vds ≥ 40 V and current ≥ inrush.
Applied Avionics VIVISUN/Korry legends come in 28 VDC, 5 VDC, 28 VAC, 5 VAC, and 115 V lamp
variants. For a quick bench mock-up, substitute two 3.3 V LEDs (white + amber) with series
resistors driven straight from GPIO21/GPIO14 within the ~20 mA limit.

## D.6 Power budget

| Rail | Loads | Typical | Peak |
|---|---|---|---|
| **3.3 V** | ESP32-S3 (Wi-Fi off) + mic + microSD | ~80–150 mA | ~250 mA (SD init / SR burst) |
| **5 V** | MAX98357A output | a few mA idle | **~650 mA** (5 V/4 Ω, loud) |
| **Lamp rail** | up to 2 legend halves | 0 (dark) | per lamp spec (e.g. 28 V incand.) |

Power from **USB 5 V ≥ 1 A**. Keep a 28 V legend supply separate from logic 5 V (grounds
common only). Bulk decoupling ≥ 100 µF near the amp VIN plus 0.1 µF per device.

## D.7 Processor selection

This is a narrow, bounded workload — a **small fixed vocabulary** (checklist triggers +
universal advance words, well under the ~200-command MultiNet cap), **offline**, and
**deterministic**. That is command recognition on a fixed grammar, **not** open-ended
transcription, which keeps an MCU-class part firmly in scope and makes a Linux SBC overkill.
It is also exactly the property that supports the minor-failure / no-DO-178C argument (C.3):
a single-chip, fixed-grammar device has a small, well-understood failure surface.

**Recommendation: keep the ESP32-S3 as the baseline; consider the ESP32-P4 only for
headroom.** ESP-SR (v2.1+) supports S3 and P4 for English MultiNet; the classic ESP32 is no
longer supported by the current speech algorithms and should be avoided.

| Option | Summary | Verdict |
|---|---|---|
| **ESP32-S3** (baseline) | LX7 dual-core @240 MHz + AI vector ext, 512 KB SRAM, Wi-Fi+BLE, ~$8–15 | Best AI/voice part in the line, most mature tooling; the firmware/diagram/BOM are built on it |
| **ESP32-P4** (upgrade) | RISC-V to 400 MHz + AI ext, 768 KB SRAM, ~2.5× compute, **no Wi-Fi/BT** | Worth it only for more compute or a future display; no-radio is arguably a safety plus |
| Syntiant NDP120 | Always-on ultra-low-power NDP | Overkill; we have panel power and need full grammar + playback + SD |
| Picovoice Porcupine+Rhino | Offline wake+intent on Cortex-M4 | Clean fit but needs a per-deployment license key — undesirable for self-contained safety gear |
| Fluent.ai / NXP i.MX RT600 | Commercial intent / heavy audio DSP | More licensing/board complexity than a fixed 13-checklist grammar needs |
| Raspberry Pi (whisper/Vosk) | Full Linux STT | Non-deterministic boot, higher power/cost — less robust for fixed-grammar safety device |

## D.8 Firmware build notes

| Topic | Value |
|---|---|
| Framework | **ESP-IDF ≥ 5.2** |
| Components | `esp-sr`, `esp_spiffs`, `driver`, `json` (cJSON), `fatfs`, `sdmmc`, `esp_driver_sdmmc` |
| Speech models | WakeNet `WN9_HIESP`; MultiNet English `mn6_en`/`mn7_en` (S3 only) |
| Partitions | factory app 3 MB + model 5 MB + storage 2 MB → needs **16 MB** flash (N16R8) |
| Grammar rules | lowercase + single spaces; spell numbers ("v one"); ~200-cmd cap |
| Fault behavior | any card fault → `ST_FAULT`, amber legend, **no checklist shown** |

## D.9 Bill of materials (DIY build)

| Qty | Part | Spec / example |
|---|---|---|
| 1 | ESP32-S3 DevKit | DevKitC-1 **N16R8** (PSRAM) |
| 1 | I2S MEMS mic | **INMP441** / ICS-43434 breakout |
| 1 | I2S amp | **MAX98357A** breakout |
| 1 | Speaker | 4–8 Ω, ≥ 2 W |
| 1 | microSD card + breakout | FAT32 (the Aircraft Card) |
| 1 | Annunciator switch | Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench) |
| 2 | Lamp driver | logic-level N-MOSFET (2N7002/AO3400) or NPN (2N2222) |
| 4 | Resistors | 1 kΩ ×2 (gate), 10 kΩ ×2 (pulldown) |
| 2–3 | Pull-ups | 10 kΩ on SD CMD/DAT0 (if breakout lacks them) |
| — | Caps | 0.1 µF per device, 100 µF bulk near amp |
| 1 | PTT button | momentary SPST (or use BOOT) |

Integrated alternative: **ESP32-S3-Korvo-2** (~$45–55) replaces mic/codec/amp/SD; use its
BSP pin map and ES8311 codec init.

---

# PART E — ENCLOSURE SPECIFICATION (for the fabricating engineer)

The housing is **generic** — it is sized for the electronics and the panel interface, not
for a specific airframe. The only airframe-specific item is the **mounting variant**
(DZUS slot vs. round instrument hole) chosen for the target panel, and the card inside it.

## E.1 Two-piece architecture

| Piece | Contents | Where | Why |
|---|---|---|---|
| **A. Panel bezel** | Split-legend annunciator switch, speaker + grille, optional PTT | Front panel / pedestal, on the **DZUS rail** | Crew must see/reach it; dark-cockpit annunciator in the normal scan |
| **B. Remote processor box** | ESP32-S3, mic, amp, **microSD card slot**, lamp-driver, power conditioning | Avionics bay / behind-panel, blind | Keeps heat, the card slot, and wiring out of the panel |

A single all-in-one box is acceptable for a pure bench demo, but the two-piece split mirrors
real remote-mount avionics and keeps the mic away from fan/avionics noise.

## E.2 Piece A — panel bezel

- **DZUS rail mount:** fastener pitch **3/8 in (9.525 mm)**; clearance hole **0.255 in
  (6.48 mm)**; bezel height a whole multiple of 3/8 in (target 3-unit = **28.575 mm**, or
  4-unit = **38.1 mm** if the grille needs room); standard pedestal width **≈ 146 mm**
  aluminum (144.45 mm face); backplate **1/16 in (1.6 mm)** 6061-T6; first/last fastener
  **14.29 mm** from each end.
- **Round-hole variant:** fits a standard **3-1/8 in (79.4 mm)** instrument cutout with four
  6-32 screws on the standard bolt circle, to replace a blanking plate where no DZUS slot
  exists.
- **Face layout (top→bottom):** split-legend annunciator switch (cut per the *specific*
  switch datasheet — typical VIVISUN bezel ≈ 15×15 mm to 19×19 mm; top half `VOICE CHKLST
  OFF` white, bottom `VOICE CHKLST FAULT` amber, upright when installed); speaker grille
  (≥ 40 % open over the cone, offset from the switch); optional guarded/recessed PTT.
- **Material/finish:** 6061-T6 aluminum 2.0–3.0 mm (or ABS/PC for a non-structural demo);
  **matte black, low-gloss (≤ 10 gloss units)** to suppress glare; legend by the switch's
  internal engraving (preferred) or laser-etch + white/amber paint-fill; edges chamfered
  0.5 mm.

## E.3 Piece B — remote processor box

- **Envelope:** sized around the ESP32-S3 DevKitC-1 (≈ 70×26 mm) plus amp, mic, microSD
  breakout, and the 2-channel lamp-driver; practical outer **≈ 110 × 80 × 45 mm**. Confirm
  against the actual stacked board set.
- **Mounting:** internal standoffs / M2.5 brass inserts — boards screwed down, not floating
  (vibration). Keep the mic away from the amp/any fan; if the mic lives here, add a meshed
  acoustic port; mic may instead live in the bezel (keep the I2S run < 150 mm).
- **Access & connectors:** externally swappable **microSD (Aircraft Card)** carrier labeled
  `CONFIG CARD — FAT32` (swap without opening the box); covered/recessed **USB-C** service
  port (bench use only); one keyed, positive-latching main connector (small MIL-circular or
  9-pin D-sub) carrying SELECT, both legend drives, PTT, speaker +/−, power/ground (pinout
  from `board_pins.h`). Accept USB 5 V ≥ 1 A; optional internal **28 V→5 V DC-DC** (≥ 2 A)
  with TVS + fuse if a 28 V bus mock-up is wanted (mark as demo regulator, not DO-160
  qualified).
- **Material/EMI:** aluminum preferred (doubles as EMI shield + heatsink); if plastic, add a
  grounded conductive shield liner/coating; single-point chassis ground stud bonded to the
  connector shell and ESP32 ground.

## E.4 Audio, thermal, environmental, labeling

- **Audio:** 4–8 Ω, ≥ 2 W speaker, sealed-back or small rear volume (5–15 cm³); grille
  ≥ 40 % open with acoustic mesh; gasket the speaker to prevent buzz.
- **Thermal:** ESP32-S3 + ESP-SR is low-power (a few hundred mW) — **no fan.** Passive
  convection (vent slots low/high) or conduction (thermal pad to the aluminum wall). If
  sealed, verify internal rise < 20 °C above 55 °C ambient. DC-DC (if fitted) on its own
  thermal path.
- **Environmental:** design toward the DO-160G categories in **C.4** (Cat A2 temp, Cat S
  vibration, etc.) — design guidance for the prototype, formal test for a productized unit.
- **Labeling:** placard `DEMO / TRAINING ONLY — NOT FOR FLIGHT`; box exterior carries unit
  name, serial/asset field, `FAT32` card format, and the USB "bench use only" note;
  annunciator legends `VOICE CHKLST OFF` (white) / `VOICE CHKLST FAULT` (amber); amber =
  caution, white = status per AC 25-11B.

## E.5 Deliverables & open items for the engineer

**Deliverables:** STEP + native 3D CAD of both pieces (boards + switch modeled in place);
fully-dimensioned 2D drawings (DZUS pattern, switch cutout from the chosen datasheet, grille,
connector cutouts; GD&T on the switch cutout and DZUS holes); connector pinout mapped to
`board_pins.h`; an FDM/SLA printable prototype for fit-check; a mechanical BOM; tolerances
(switch cutout ±0.1 mm, DZUS holes ±0.1 mm on the 9.525 mm pitch, general ±0.25 mm).

**Open items (confirm before CAD):** the **exact Applied Avionics switch part number** — the
single most critical dimension; nothing finalizes until it is fixed. Also: DZUS slot vs.
3-1/8 in round hole in the target panel; where the mic lives; whether a 28 V input is
wanted; and the speaker model (sets grille open area + rear-volume cavity).

**Reference dimensions:** DZUS pitch 9.525 mm · DZUS hole 6.48 mm · backplate 1.6 mm · first
fastener offset 14.29 mm · pedestal panel width ≈ 146 mm · round instrument hole 79.4 mm ·
remote box ≈ 110 × 80 × 45 mm · speaker 4–8 Ω ≥ 2 W.

---

# PART F — REFERENCES

**Certification & regulatory**
- FAA Policy Statement **PS-AIR-21.8-1602**, "Approval of Non-Required Safety Enhancing
  Equipment (NORSEE)" — https://www.gajsc.org/wordpress/wp-content/uploads/2016/08/PS-AIR-21.8-1602.pdf
- FAA **Technical Standard Orders (TSO)** program overview — https://www.faa.gov/aircraft/air_cert/design_approvals/tso
- FAA **AC 21-16G**, acceptance of RTCA/DO-160 versions D–G — https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1019280
- RTCA **DO-160G**, Environmental Conditions and Test Procedures for Airborne Equipment — https://www.rtca.org/training/do-160g-training/
- FAA **AC 20-152A**, Development Assurance for Airborne Electronic Hardware (DO-254 scope; simple-hardware relief) — https://en.wikipedia.org/wiki/AC_20-152
- FAA **AC 20-168 / RTCA DO-313**, installation of non-essential, non-required equipment — https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/315695
- TSO / TC / STC / PMA primer — https://afuzion.com/tso-tc-stc-and-pma-intro/
- FAA **AC 25-11B**, electronic flight displays — annunciation color / dark-cockpit conventions — https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf

**Hardware & components**
- INMP441 microphone datasheet — https://www.farnell.com/datasheets/1824785.pdf
- MAX98357A amplifier datasheet (Analog Devices) — https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf
- MAX98357A breakout guide (Adafruit) — https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf
- ESP32-S3 GPIO drive current — https://esp32.com/viewtopic.php?t=20097
- microSD operating current — https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975
- Applied Avionics VIVISUN lighted pushbutton switches — https://www.appliedavionics.com/led-lighted-pushbutton-switches.html
- Espressif **ESP-SR** speech framework — https://docs.espressif.com/projects/esp-sr/en/latest/esp32s3/index.html
- Espressif **ESP32-P4** product page — https://www.espressif.com/en/products/socs/esp32-p4
- ESP32-P4 vs ESP32-S3 performance — https://www.elecrow.com/blog/who-is-the-true-performance-king-esp32-p4-vs-esp32-s3.html

**Mechanical / panel**
- DZUS panel-building dimensions guide (MyCockpit) — https://www.mycockpit.org/tutorials/Panelbuildingfocussedondimensions.pdf
- Standard 3-1/8 in instrument cutout (Aircraft Spruce) — https://www.aircraftspruce.com/catalog/inpages/instradaptkit.php

---

> **DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.** Repository:
> github.com/flas-tech/cj2-voice-emergency-checklist (MIT License). The certification
> sections describe a path, not held approvals; no NORSEE LOA, STC, PMA, or TSOA exists for
> this article.
