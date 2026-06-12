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
behavior comes from the installed cards (Part B). The Cessna Citation
CJ2 is included only as the reference example.

**Crew audio is taken from the aircraft audio panel** (analog or digital, selectable per
installation), and recognition is **voice-activated (VOX)** by default — the pilot simply
speaks, with a push-to-talk (PTT) button retained as a manual override. **Configuration
and checklist data live on two separate cards** — a write-protected **Config Card** that
defines the installation (aircraft selection, audio source, VOX behavior, hardware
options) and a **Data Card** that carries the checklist library and audio. Checklist
read-aloud audio is played back **out to the aircraft audio panel** through a **dedicated,
separate, galvanically-isolated COM3-style audio output channel** (an isolated line-level
transmit stage), so the crew hears checklist items in their headsets; the onboard
speaker/amplifier used in the earlier design is removed. The audio-panel INPUT tap
(receive-only, galvanically isolated) and the audio-panel OUTPUT channel (isolated TX to
COM3-style aux channel) are **electrically separate paths on separate connectors**. This
two-card, audio-panel-fed design is a deliberate change from the earlier onboard-microphone
/ single-card demo and carries certification consequences addressed honestly in Part C;
the addition of the isolated COM3-style audio output is the most significant
interface-risk change in this revision.

**This master reference supersedes and combines** the previously separate documents:
the technical data packet, the processor-selection note, and the enclosure specification.
Those remain in the repository for history; this is the single source of truth.

---

## Document map

| Part | Contents |
|---|---|
| **A. Product** | What the system is, the generic architecture, and the safety model |
| **B. The cards** | The two-card (Config + Data) model + the formal card specifications & validation |
| **C. Certification basis** | NORSEE / DO-160G / installation path, the deliberate DO-178C-avoidance argument, and the audio-panel-interface impact — both the receive-only INPUT tap and the isolated COM3-style OUTPUT injection channel, and the added cert risk the output path introduces |
| **D. Hardware reference** | Pin map, audio-input stage, VOX/PTT, per-device wiring, annunciator, lamp driver, power, BOM, processor selection |
| **E. Enclosure** | Two-piece mechanical specification (dual card slots, isolated audio interface) for the fabricating engineer |
| **F. References** | All cited regulatory and component sources |

---

# PART A — THE PRODUCT

## A.1 What it is (and is not)

| It **is** | It **is not** |
|---|---|
| An **advisory** read-aloud reader of checklist items | A required or primary aircraft system |
| **Receive-only on the audio-panel INPUT tap** (galvanically isolated, listen-only); plus a **separate, galvanically-isolated OUTPUT into a dedicated COM3-style audio-panel channel** for checklist read-aloud; no command/data to any aircraft system | A transmitter on aircraft COM radios, a panel control, or an interface to avionics/engines/flight controls. It **does** inject advisory audio into one dedicated aux/COM3-style channel via an isolated output — but that output is on a **separate channel** from the receive tap and is electrically isolated from required COM channels |
| Driven entirely by the installed **Config Card + Data Card** | Tied to one airframe in firmware |
| **Offline**, deterministic, single-chip | A cloud / connected / large-vocabulary STT device |
| A **complement** to the certified/required checklist | A substitute for the AFM/QRH or required checklist |

This framing is not cosmetic — it is the foundation of the certification argument in
Part C. The device connects to the aircraft audio panel through **two electrically
separate, galvanically-isolated channels**: (1) a **receive-only isolated INPUT tap**
(listen-only; cannot back-feed) used as the ASR speech source, and (2) a **separate,
galvanically-isolated OUTPUT into a dedicated COM3-style audio-panel channel** (an
isolated line-level TX stage) through which checklist read-aloud audio is delivered to
the crew in-headset. The input-tap language of "receive-only, isolated" is preserved
and accurate for the INPUT side; the OUTPUT side adds a carefully scoped, isolated
unidirectional injection into one dedicated aux channel. This dual-isolated-channel
architecture still fits the **NORSEE** (Non-Required Safety Enhancing Equipment) approval
path and lets the program **lean on DO-160G environmental qualification while avoiding
DO-178C software assurance** — but the isolated audio OUTPUT is the **most significant
certification/interface-risk item in this revision** (superseding the prior "audio-panel
tap" note), and it must be addressed explicitly in the isolation design and safety
assessment. Part C addresses this honestly.

## A.2 Generic system architecture

| Block | Function | Installation-/aircraft-specific? |
|---|---|---|
| **MCU + speech stack** | VOX/wake word → command recognition → playback sequencing | No — fixed firmware |
| **Audio-panel input stage** | Takes crew speech **from the aircraft audio panel** — analog (isolated line tap) or digital (I2S codec), selectable per install | **Config-driven** — the source is set by the Config Card; the hardware path is wired at install |
| **Audio-panel output stage (isolated TX to COM3-style channel)** | Delivers checklist read-aloud audio **out to a dedicated COM3-style audio-panel input channel** via a galvanically-isolated, line-level output stage (isolation transformer + line driver on the TX line); crew hears checklist items in-headset. **Onboard speaker/amplifier removed.** The output is on a **separate channel and separate connector** from the receive-only INPUT tap. An isolation transformer on the TX line ensures a device fault cannot key, jam, load, or back-feed the panel's other channels or required COM radios. | No (fixed output stage hardware; the audio-panel COM3 channel it drives is chosen at installation) |
| **Config Card (microSD, slot 1)** | Defines the installation: active aircraft, audio source (analog/digital), VOX parameters, hardware options | **Yes — per installation** |
| **Data Card (microSD, slot 2)** | Carries the checklist library, trigger/advance vocabulary, and read-aloud audio | **Yes — per aircraft** |
| **Annunciator switch** | Dark-cockpit status / fault indication, IN/OUT select, PTT override | No |

The MCU runs Espressif **ESP-SR** (AFE noise-suppression/VAD → WakeNet wake word →
MultiNet fixed-grammar command recognition). The **AFE's voice-activity detector (VAD) is
what enables hands-free VOX**: the pilot speaks and the device gates recognition on detected
speech, with the PTT button retained as a manual override (force-listen). The grammar
(trigger phrases, advance words) is small and bounded, which is what keeps an MCU-class part
in scope (see D.7).

The crew-audio source is **no longer an onboard microphone in the operational design** — it
is a tap off the aircraft audio panel. An onboard MEMS microphone is retained only as a
documented **bench-test** option (D.3), never as the installed audio source.

## A.3 The safety model (carried into the cert argument)

Three design rules define the failure behavior, and each one maps to a NORSEE requirement
(Part C):

1. **Revert-to-unopened.** If **either card** is missing, unreadable, malformed, fails
   schema validation, or any referenced audio clip is absent — or the Config Card and Data
   Card disagree on the active aircraft — the device **refuses to present any checklist** and
   enters a clearly-annunciated FAULT state. It never shows partial or stale data.
   *(Failure mode = loss of function, not misleading information.)*
2. **Dark-cockpit annunciation.** When selected IN and healthy, the unit shows **nothing**.
   A fault lights the amber FAULT legend. Selected OUT shows the white OFF status and
   **inhibits** the fault legend (a deliberately deselected system needs no crew action).
   A power-up lamp test proves the legend is alive.
3. **Dual-isolated-channel interface.** The device connects to the aircraft audio panel
   through **two electrically separate, galvanically-isolated channels** (see C.3a, D.3.1,
   D.3.3a):
   - **Receive-only INPUT tap** — a high-impedance, isolation-transformer-coupled (analog)
     or buffered-receive-only (digital) tap off the audio panel; one-way listen only; the
     unit **cannot transmit, key, mute, or back-feed** via this path; a short, open, or
     device failure cannot affect audio-panel function on this side.
   - **Isolated OUTPUT into a dedicated COM3-style channel** — a galvanically-isolated,
     line-level output stage (isolation transformer on the TX line) that injects
     checklist read-aloud audio into one dedicated auxiliary audio-panel channel
     ("COM3-style"); physically separate connector from the input tap. The isolation
     barrier ensures a device fault **cannot key, jam, load, or back-feed the panel's
     other channels or required COM radios**. This output channel is the most significant
     cert/interface-risk item in this revision and must be addressed in the isolation
     design and safety assessment (Part C).
   The device draws power on its own protected rail. This dual-isolated-channel posture
   replaces the former "receive-only only" claim with a narrower, testable one covering
   both directions — and it is the crux of the Part C argument.

---

# PART B — THE TWO CARDS (configuration + data)

## B.1 Principle

> **The product is generic. The two installed cards make it a specific aircraft's checklist
> reader, installed a specific way.** Responsibility is split: the **Config Card** describes
> *this installation* (which aircraft, which audio source, how VOX behaves, what hardware is
> fitted); the **Data Card** carries *the checklist content* (library, vocabulary, audio).
> To support a new airframe you author a new Data Card; to re-use it in a different aircraft
> or wiring you change only the Config Card. **No firmware change, no recompile.**

Why two cards? Configuration is **installation-controlled** (set by the installer/shop and
locked) while checklist data is **content-controlled** (authored from the AFM/QRH and revised
as the source revises). Separating them keeps a content revision from silently changing the
installation's audio/VOX setup, and lets a write-protected Config Card serve as the
configuration-control record the FAA expects under NORSEE (Part C). Both cards are
microSD/FAT32 and sit in **two physical slots** (slot 1 = CONFIG, slot 2 = DATA; see E.3).

## B.2 Config Card (slot 1) — layout & schema

```
/sdcard-config/   (slot 1, microSD, FAT32)
  config.json     the single installation-configuration manifest
```

`config.json` top-level object:

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `schema_version` | integer | rec. | Config-schema version the firmware validates against |
| `aircraft` | string | **yes** | Active aircraft id; **must match** a folder on the Data Card |
| `audio_source` | string | **yes** | `analog` or `digital` — selects the audio-panel input path (D.3.1) |
| `audio` | object | **yes** | Audio-input parameters (below) |
| `vox` | object | **yes** | VOX behavior (below) |
| `hardware` | object | opt. | Fitted-hardware options (codec part, legend rail, PTT present, etc.) |
| `install` | object | rec. | Provenance: shop, installer, date, work-order (configuration control) |

`audio` object:

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `input_gain_db` | number | rec. | Input trim for the line-level tap (typ. 0–6 dB) |
| `codec` | string | when `digital` | I2S codec fitted (e.g. `es8388`, `es7210`, `pcm1808`) |
| `sample_rate_hz` | integer | rec. | 16000 for ESP-SR |

`vox` object:

| Field | Type | Req. | Meaning |
|---|---|---|---|
| `mode` | string | **yes** | `vox` (default, hands-free) or `ptt_only` (override-only) |
| `vad_sensitivity` | integer | rec. | AFE VAD aggressiveness 0–3 (higher = less false-trigger, may clip onset) |
| `hangover_ms` | integer | rec. | How long to keep listening after speech stops (debounce, typ. 300–600 ms) |
| `ptt_override` | boolean | rec. | `true` keeps PTT as a force-listen override even in `vox` mode |

- **`ptt_only` mode** disables VOX and reverts to the legacy push-to-talk behavior.
- A Config Card whose `aircraft` has no matching Data Card folder is a fault
  (`FAULT_AIRCRAFT_MISMATCH`), not a silent guess.

## B.3 Data Card (slot 2) — layout

```
/sdcard-data/   (slot 2, microSD, FAT32)
  <FOLDER>/                  one folder per aircraft (e.g. CJ2, B200, PC12)
    checklists.json          the data manifest + checklist library
    audio/
      <clip>.wav             one read-aloud clip per referenced item + fault clips
```

- The firmware loads the folder named by the **Config Card's** `aircraft` field. (If no
  Config Card is present at all, that is `FAULT_NO_CONFIG` — the device does **not** fall back
  to guessing a folder.)

## B.3a Data Card manifest schema (`checklists.json`)

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

## B.4 Two-card validation & the revert-to-unopened rule

On boot the firmware attempts a **complete, valid** load of **both cards** and returns
exactly one status. Both cards must be present, valid, and **mutually consistent** (the
Config Card's `aircraft` must resolve to a Data Card folder):

| Status | Card | Meaning | Annunciation |
|---|---|---|---|
| `STORE_OK` | both | Both cards mounted, both manifests parsed + schema-valid, **every** audio clip present, aircraft consistent | dark (healthy) |
| `FAULT_NO_CONFIG` | config | Config Card not detected / `config.json` missing / unreadable | amber FAULT |
| `FAULT_CONFIG_PARSE` | config | `config.json` malformed | amber FAULT |
| `FAULT_CONFIG_VALIDATION` | config | Config schema / value violation (bad `audio_source`, bad `vox.mode`, missing required field) | amber FAULT |
| `FAULT_NO_CARD` | data | Data Card not detected / mount failed | amber FAULT |
| `FAULT_AIRCRAFT_MISMATCH` | both | Config `aircraft` has no matching Data Card folder | amber FAULT |
| `FAULT_NO_JSON` | data | `checklists.json` missing / unreadable | amber FAULT |
| `FAULT_PARSE` | data | Data JSON malformed | amber FAULT |
| `FAULT_VALIDATION` | data | Data schema or voice-rule violation, empty data | amber FAULT |
| `FAULT_AUDIO_MISSING` | data | A referenced clip is absent | amber FAULT |
| `FAULT_NO_MEMORY` | — | Allocation failed while loading | amber FAULT |

**On any FAULT the in-memory checklist table is left EMPTY** — the device cannot present a
partial or stale checklist even if asked. This is the literal implementation of "always
revert to unopened if files are not available." The boot order is **Config Card first**
(it names the aircraft and the audio source the input stage must initialize), then the
matching Data Card folder.

## B.5 Card integrity & provenance (recommended for productized cards)

For cards that drive a *safety-enhancing* device, integrity matters as much as schema
validity. Recommended additions (forward-looking, beyond the current demo):

- **Schema version gate** — firmware refuses either card whose `schema_version` it does not
  support, rather than mis-parsing it.
- **Manifest checksum / signature** — a per-card hash (and, for production, a signature)
  so a corrupted or tampered card is rejected (`FAULT_CONFIG_VALIDATION` / `FAULT_VALIDATION`).
- **Content provenance (Data Card)** — record the AFM/QRH source revision the checklist
  text was transcribed from, the author, and the date.
- **Installation provenance (Config Card)** — the `install` object records shop, installer,
  date, and work-order. The Config Card is the per-tail **configuration-control record** the
  FAA expects under NORSEE (Part C): it documents *how this specific aircraft was set up*,
  including the audio source and VOX behavior.
- **Read-only media** — distribute production cards write-protected; the Config Card in
  particular should be **locked after installation** so configuration cannot drift in service.

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
3. **Bounded dual-isolated interface.** This revision adds **two** ties to an aircraft
   system (C.3a), both galvanically isolated: (a) a **receive-only isolated INPUT tap** off
   the audio panel — the device takes no input that commands a function and produces no
   output via this path; and (b) a **dedicated isolated OUTPUT** into a COM3-style
   audio-panel channel for checklist read-aloud — this is a unidirectional audio injection
   through an isolation transformer, not a control/keying/command path. The device still
   produces **no command or control output to any aircraft system**, but it does inject
   advisory audio into one dedicated aux channel. Physical/electrical separation is
   preserved on the power and signal-return side by the isolation barriers on both paths.
   The output injection is a **more invasive interface than a pure receive-only tap** and is
   the argument's weakest point; the strength of the argument now rests on *isolation +
   directionality + channel separation* rather than *total receive-only.* *[Source:
   PS-AIR-21.8-1602 §1.4 — design considerations for keeping a failure minor.]*
4. **Qualitative safety evaluation is permitted** for non-complex equipment; a quantitative
   probabilistic analysis (and the DO-178C machinery that feeds it) is not required for a
   minor-failure advisory function. *[Source: PS-AIR-21.8-1602 §1.4.]*

**Honest caveats (must stay in the doc):**
- This argument **must be agreed with the FAA ACO early** — the applicant proposes the
  classification; the FAA concurs. If the FAA judges the failure condition above minor (e.g.
  because of over-reliance/automation-dependency human factors, **or because the audio-panel
  interface is judged to compromise an aircraft communication system**), the program moves to
  **§2 of the NORSEE policy** (xx.1309, ARP4754A/ARP4761) and software assurance re-enters.
- "No DO-178C" is **earned by architecture and by procedural mitigations**, not by labeling.
  The revert-to-unopened behavior, the validation gate, the dark-cockpit annunciation, the
  **dual-isolated-channel interface** (receive-only input tap + isolated output into a
  dedicated COM3-style channel), and a **mandatory limitation that the unit may not be
  used as a substitute for the required checklist** are the price of that classification.
- **The audio-panel interface raises the installation bar — further still with the output
  channel.** What was arguably a minor alteration (a self-contained box drawing only power)
  now wires into an **aircraft communication system** for both receive and transmit. The
  addition of an isolated audio OUTPUT into an audio-panel channel is a more invasive
  interface than a pure receive-only tap. That makes an STC (or at minimum careful
  field-approval scrutiny of the interface) the more likely installation path on most
  airframes — see C.3a and C.5. Do not assume a logbook-entry minor alteration any more.
- **VOX adds a human-factors failure mode.** Hands-free activation can **false-trigger** on
  ambient cockpit speech, ATC audio, or crew conversation, potentially reading a checklist
  the crew did not request. This is a *misleading/nuisance* mode the ACO will scrutinize; it
  is mitigated by VAD sensitivity tuning, a bounded wake/trigger grammar, the retained PTT
  override, and the standing limitation that the required checklist remains the authority
  (C.3a, D.3.2).

## C.3a Audio-panel interface impact (the honest part)

This revision adds **two** interfaces to the aircraft audio panel: a receive-only isolated
INPUT tap (the original change from Rev A) and now a **dedicated isolated OUTPUT** channel
(COM3-style) for checklist read-aloud delivery. Both must be argued explicitly. The goal is
to make both interfaces so narrow and so demonstrably direction-controlled and isolated that
the residual failure stays minor. The output path is the more significant of the two.

**What the interface is — and is not:**

| Property | INPUT tap (receive-only) | OUTPUT channel (isolated TX to COM3) |
|---|---|---|
| **Directionality** | **Receive-only.** No path to transmit, key a radio, mute, or back-feed. | **Output-only.** Unidirectional line-level audio injection into the panel's dedicated COM3-style aux channel. Not a keying or control path. |
| **Isolation** | **600 Ω aviation audio isolation transformer** (e.g. Allen Avionics AGL series) on the analog path; buffered receive-only I2S for the digital path. No data driven back toward any aircraft bus. | **Line-level isolation transformer** on the TX output line; galvanic barrier between the device and the panel's COM3 input. A fault in the device cannot key, jam, load, or back-feed the panel's other channels or required COM radios. |
| **Fault containment** | Short, open, or power loss inside the device cannot load down, ground, or back-feed the panel via the input path. | Short, open, or power loss cannot key or jam the panel via the output path; the isolation transformer is the primary barrier. |
| **Channel separation** | INPUT and OUTPUT are on **separate connectors and separate galvanic barriers**. They do not share a conductor path. | (same) |
| **No operational credit** | The panel feed is *listened to* for recognition only. | The injected audio is advisory/informational only; the crew's authority is the required checklist. |

**Why this still supports a minor classification:**
- The input tap is parallel and high-impedance; the audio panel and intercom **continue to
  function identically whether the device is present, powered, or failed** on the input side.
- The output channel is a **dedicated aux channel** (COM3-style), not the crew intercom or
  any required COM radio channel; a failure on the output side (silence, noise, device
  failure) does not remove any required function.
- The DO-160G conducted/induced-susceptibility and audio-system installation tests (C.4) are
  the appropriate means to demonstrate no degradation on either path.

**Why the output channel raises the bar (do not gloss over this):**
- **Isolation/failure modes (primary risk).** The most significant question is whether the
  isolation design ensures a fault inside the device (including output-stage failure, supply
  fault, or software runaway) **cannot key, jam, load, or back-feed** the panel's COM
  channels or intercom. The isolation transformer on the TX line is the primary barrier;
  the design must demonstrate this under all failure conditions.
- **Interference with required COM audio.** The ACO may require substantiation that the
  injected advisory audio **cannot interfere with** required ATC/aircraft audio on the panel —
  e.g., that the output level is set conservatively, that the COM3 channel cannot bleed onto
  required COM1/COM2 channels, and that the injected audio cannot mask or be mistaken for
  required ATC communication.
- **Intelligibility / masking.** There is a human-factors question: can the crew mistake the
  injected checklist audio for required ATC/aircraft audio, or can the injected audio mask
  required communications? Mitigations include a distinctively different voice/audio
  treatment, a conservative output level, and the standing limitation that the required
  checklist remains the authority.
- **Input-tap bar still applies.** All the previously stated concerns about the input tap
  (loading, ground loop, grounding practice, intercom-level degradation) still apply to
  the input side and are unchanged.
- **STC / careful field approval.** The interface now touches an aircraft communication
  system for **both receive and transmit**; plan for STC or carefully substantiated field
  approval, not a bare logbook entry (C.5).
- Audio-panel wiring practice: many panels **ground audio jacks only at the intercom** to
  avoid ground loops, so both the input tap point and the output injection point, and their
  shield grounding, must be coordinated with the specific panel's installation manual.

**VOX (voice-activation) certification note.** Replacing push-to-talk with VOX as the
primary trigger introduces a **false-activation human-factors mode** (reading an unrequested
checklist on stray speech/ATC audio). Mitigations carried into the design: bounded
wake-word + trigger grammar (not open-vocabulary), tunable VAD sensitivity and hangover
(Config Card, B.2), the **retained PTT override**, and the standing limitation that the
required checklist remains the authority. The ACO will want this mode addressed in the
safety/human-factors evaluation. *[Source: PS-AIR-21.8-1602 §1.4; FAA AC 25-11B human-factors
conventions.]*

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
| §18 AF Conducted Susceptibility | Cat — | As applicable to the supply; **also relevant to the audio-panel input** — verify recognition is not corrupted by AF conducted noise |
| §19 Induced Signal Susceptibility | Cat ZC | Cockpit; **audio-input cabling** routed/shielded per the panel's installation practice |
| §20 RF Susceptibility | Cat — | Aluminum case + grounded shield |
| §21 RF Emission | **Cat M** (or better) | **Wi-Fi/BT disabled in firmware** materially helps emissions |
| §22 Lightning Induced Transient | as installed | Behind-panel mounting reduces exposure |
| §25 ESD | per §25 | Bond exposed metal; recessed connectors |
| §26 Flammability | UL94 **V-0** materials | Required if not aluminum |

> The deliberate choice to **disable Wi-Fi and Bluetooth in firmware** is both a security
> decision and an emissions-qualification advantage (§21).

> **Audio-interface-specific evidence (beyond the table):** because the unit now has both a
> receive tap and an isolated output into the audio panel, qualification should additionally
> demonstrate — across all DO-160G conditions and **including a failed/unpowered device** —
> that (a) the **input tap** does not degrade audio-panel performance (intercom level,
> sidetone, the panel's own VOX/hot-mic behavior), and (b) the **isolated output** cannot
> key, jam, load, or back-feed the panel's COM channels under any failure mode, and the
> injected advisory audio level does not mask or interfere with required ATC/aircraft audio.
> The isolation transformers on both paths (C.3a) and the high-impedance receive-only input
> topology are the design basis for those demonstrations.

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

> **The audio-panel interface raises the install classification — the output channel raises
> it further.** Because the device now wires into an **aircraft communication system** for
> both receive and transmit, step 4 should be approached assuming the interface makes the
> alteration **more than minor** on most airframes — i.e. plan for an **STC or a field
> approval that specifically substantiates both the receive-only input tap and the isolated
> COM3-style audio output** (isolated, no degradation of comm audio, no keying/jamming of
> required channels per C.3a/C.4), not a bare logbook entry. The earlier power-only/
> independent design could credibly claim a minor alteration; this one generally cannot.

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
| **Audio-panel interface — INPUT tap** | Receive-only + galvanic isolation; no comm-audio degradation (C.3a, C.4 §18/§19) | Architecture defined; substantiation/test pending |
| **Audio-panel interface — OUTPUT (COM3 channel)** | Galvanically-isolated line-level TX to dedicated COM3-style channel; isolation transformer on TX line; cannot key/jam/load panel or required COMs; advisory audio cannot mask required ATC audio (C.3a) | **Architecture defined; this is the most significant new interface-risk item — isolation design + safety assessment required before productization** |
| **VOX false-activation** | Bounded grammar + tunable VAD + retained PTT override (C.3a, D.3.2) | Mitigations defined; ACO human-factors concurrence pending |
| Installation | **STC / substantiated field approval** (audio tap is more than minor); minor-alteration unlikely | Per-aircraft; none performed |
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
| Speech stack | Espressif **ESP-SR**: AFE (NS/**VAD → VOX**) → WakeNet "Hi ESP" → MultiNet English |
| **Crew audio input** | **From the aircraft audio panel** on **I2S_NUM_0**, selectable per install: **analog** (isolated line tap → I2S codec ADC) or **digital** (I2S codec ADC fed from a buffered tap). Onboard MEMS mic = bench-test only |
| Activation | **VOX** (AFE VAD) primary, hands-free; **PTT** retained as manual override |
| Audio output | **I2S_NUM_1** DAC → isolated line-level output stage (isolation transformer + line driver on the TX line) → **dedicated COM3-style audio-panel input channel**; crew hears checklist read-aloud in-headset. **Onboard speaker/amplifier removed.** A bench-test-only speaker output may optionally be provided in the development unit (not the installed configuration). |
| Config storage | **two microSD slots** — slot 1 **Config Card**, slot 2 **Data Card** (Part B), FAT32 |
| Annunciation | Applied Avionics split-legend switch (dark-cockpit, AC 25-11B) |

Two build paths: **Integrated** (ESP32-S3-Korvo-2 dev board — ES8311/ES7210 codec, microSD
slot; line-in repurposed for the audio-panel receive feed; output stage wired to COM3
isolation transformer) or **DIY** (ESP32-S3 DevKitC-1 N16R8 + audio-panel input stage
[isolation transformer + I2S codec ADC] + isolated audio output stage [I2S DAC → isolation
transformer → line-level TX to COM3 channel] + **two** microSD breakouts + the annunciator
switch). The earlier INMP441 MEMS mic and MAX98357A speaker-amp remain available only as
bench-test items; neither is used in the installed configuration.

## D.2 Master pin map

| Function | Macro | GPIO | Dir | Notes |
|---|---|---|---|---|
| PTT **override** | `PTT_GPIO` | 0 | in (PU) | BOOT button; active-low; **force-listen** override of VOX |
| SELECT switch | `SELECT_GPIO` | 10 | in (PU) | IN = GPIO→GND (active-low) |
| Legend OFF (white) | `LEGEND_OFF_GPIO` | 21 | out | top legend half (via driver) |
| Legend FAULT (amber) | `LEGEND_FAULT_GPIO` | 14 | out | bottom legend half (via driver) |
| Status LED | `STATUS_LED_GPIO` | 48 | out | on-board RGB on most S3 devkits |
| Audio-in bit clock | `AIN_BCLK_GPIO` | 4 | out | I2S0 BCLK → codec/mic SCK |
| Audio-in word select | `AIN_LRCLK_GPIO` | 5 | out | I2S0 WS → codec/mic WS |
| Audio-in data | `AIN_DIN_GPIO` | 6 | in | codec ADC / mic SD → ESP DIN |
| Audio-in master clock | `AIN_MCLK_GPIO` | 3 | out | **MCLK to the codec** (ES8388/ES7210 need it; INMP441/PCM1808 do not) |
| Codec I2C SDA | `CODEC_SDA_GPIO` | 1 | i/o | ES-series codec control bus (digital path) |
| Codec I2C SCL | `CODEC_SCL_GPIO` | 2 | out | ES-series codec control bus (digital path) |
| SD clock | `SD_CLK_GPIO` | 7 | out | SDMMC CLK (**shared** by both card slots) |
| SD command | `SD_CMD_GPIO` | 9 | i/o | SDMMC CMD (needs pull-up) |
| SD data 0 | `SD_D0_GPIO` | 8 | i/o | SDMMC DAT0 (needs pull-up) |
| Config-card detect | `SD_CFG_CD_GPIO` | 47 | in (PU) | slot-1 card-detect (Config Card) |
| Data-card detect | `SD_DAT_CD_GPIO` | 38 | in (PU) | slot-2 card-detect (Data Card) |
| Audio-out bit clock | `AOUT_BCLK_GPIO` | 15 | out | I2S1 BCLK → isolated output stage BCLK |
| Audio-out word select | `AOUT_LRCLK_GPIO` | 16 | out | I2S1 WS → isolated output stage LRC |
| Audio-out data | `AOUT_DOUT_GPIO` | 17 | out | I2S1 DOUT → isolated output stage DIN; DAC → isolation transformer → line-level TX to COM3-style audio-panel channel. **Bench-test note:** a speaker-amp (e.g. MAX98357A) may be substituted here for bench testing only; not the installed output. |

**Polarity macros:** `PTT_ACTIVE_LOW=1`, `SELECT_ACTIVE_LOW=1`, `LEGEND_OFF_ACTIVE_HIGH=1`,
`LEGEND_FAULT_ACTIVE_HIGH=1`, `STATUS_LED_ACTIVE_HIGH=1`, `LAMP_TEST_MS=2000`. Set any
unused output to `-1` to disable it cleanly.

**Two-slot SD note:** the demo shares one SDMMC 1-bit bus (CLK/CMD/DAT0) across both card
slots, distinguished by per-slot **card-detect** lines and by mounting each at its own path
(`/sdcard-config`, `/sdcard-data`). A production unit may instead give each slot its own SPI
or SDMMC bus to remove any contention; the firmware reads Config first, then Data (B.4).

**Reserved / avoid pins (N16R8):** GPIO33–37 (octal PSRAM/flash bus — do not use),
GPIO19/20 (USB D-/D+), GPIO0/45/46 (strapping — must boot in the right state),
GPIO26–32 (SPI flash on some modules). GPIO0 here is only the BOOT/PTT button, so it is
safe. GPIO1/2/3 are used here for the codec I2C + MCLK; on the Korvo-2 use that board's BSP
assignments instead.

## D.3 Per-device wiring

**D.3.1 Audio-panel input stage (the crew-audio source, I2S_NUM_0).** Crew speech comes from
the **aircraft audio panel**, not an onboard mic. The source is chosen by the Config Card
(`audio_source`); both paths terminate as an **I2S input** to the ESP32-S3 and feed the
ESP-SR AFE.

- **Analog path (`analog`).** Tap a headphone/intercom/line output from the panel
  (aviation audio is typically ~150–600 Ω, ~1–5 V RMS). Feed it through a **600 Ω audio
  ground-loop isolation transformer** (e.g. Allen Avionics AGL series) for galvanic
  isolation, then through a **~220–470 Ω series resistor + simple RC anti-alias** into the
  **line-in of an I2S codec ADC** (ES8388/ES7210 with MCLK on GPIO3, I2C control on
  GPIO1/2; or PCM1808/CS5343 which self-clock). The tap is **high-impedance and parallel**
  so the panel sees a negligible load; the device cannot back-feed the panel. Scale the
  divider so panel line level maps to the codec's full-scale input without clipping.
- **Digital path (`digital`).** Where the codec sits closer to the source, take a buffered,
  **receive-only** I2S/line feed into the same codec ADC. There is **no I2S output toward
  the panel** — BCLK/WS/MCLK are generated by the ESP32 for the ADC only, and no data line
  is driven back toward any aircraft bus.
- **Codec wiring:** SCK→GPIO4, WS→GPIO5, ADC_DATA→GPIO6, MCLK→GPIO3, I2C SDA/SCL→GPIO1/2;
  supply per the codec (1.8–3.3 V analog/digital rails); decouple each rail 0.1 µF.
- **Bench-test option only:** an **INMP441** MEMS mic may be wired in place of the codec for
  desk testing (VDD→3V3, SCK→GPIO4, WS→GPIO5, SD→GPIO6, L/R→GND, 100 kΩ pulldown on SD,
  never clock with VDD off). **This is not the installed audio source** and must not be used
  in an aircraft (it does not hear the panel and breaks the receive-from-panel model).

**D.3.2 VOX & PTT override.** Recognition is gated by the AFE **VAD** (VOX): the device
listens whenever speech is detected on the panel feed, tuned by the Config Card
(`vox.vad_sensitivity`, `vox.hangover_ms`). The **PTT** button (GPIO0, active-low) is a
**force-listen override** — holding it opens recognition regardless of VAD, and with
`vox.mode = ptt_only` it becomes the sole trigger (VOX disabled). PTT is debounced in
software. There is **no PTT/keying line toward the aircraft** — this button only tells the
device's own recognizer to listen.

**D.3.3a Isolated audio output stage → COM3-style audio-panel channel (I2S_NUM_1).**
Checklist read-aloud audio is delivered **out to the aircraft audio panel** via a dedicated
galvanically-isolated, line-level output stage on I2S_NUM_1 (GPIO15 BCLK, GPIO16 LRC,
GPIO17 DOUT). The output chain is: ESP32-S3 I2S DAC → I2S-to-analog DAC/line driver → a
**line-level isolation transformer** on the TX output line → line-level output (600 Ω
nominal or per the panel's COM3 input impedance) → dedicated COM3-style audio-panel input
channel. The isolation transformer on the TX line provides galvanic isolation; a device
fault (short, open, supply failure, output-stage failure) **cannot key, jam, load, or
back-feed the panel's other channels or required COM radios**. Output level should be set
conservatively so the injected advisory audio is clearly audible but does not mask required
ATC/aircraft audio.

*Judgment call / open item:* The exact I2S DAC part and isolation transformer type for the
output stage must be confirmed by the bench engineer. Options include a small I2S DAC IC
(e.g. PCM5102A class) followed by a 600Ω:600Ω aviation audio isolation transformer (Allen
Avionics AGL series or equivalent), or a combined line-driver/transformer module. The
`AOUT_BCLK/LRCLK/DOUT` macros (GPIO15/16/17) match the former speaker-amp I2S assignments;
the firmware I2S_NUM_1 driver is retained — only the physical output hardware changes.

**D.3.3b Bench-test speaker output (development/test only — not the installed output).** For
bench verification of audio content before the isolated output stage is fitted, a MAX98357A
Class-D amp may be substituted on GPIO15/16/17 (I2S_NUM_1). Supply 2.5–5.5 V; ~2.4 mA
quiescent; peak ~650 mA at 5 V/4 Ω; BCLK→GPIO15, LRC→GPIO16, DIN→GPIO17, GAIN NC = 9 dB,
SD/mode float = mono. **OUT+/OUT− are bridge-tied — never to GND. This bench speaker is
not routed to the aircraft audio panel and is NOT the installed audio output.**

**D.3.4 Two microSD card slots → SDMMC 1-bit.** 3.3 V cards. Shared bus CLK→GPIO7, CMD→GPIO9
(10 kΩ→3V3), DAT0→GPIO8 (10 kΩ→3V3), VDD→3V3, VSS→GND. **Slot 1 = Config Card** (detect on
GPIO47, mount `/sdcard-config`), **slot 2 = Data Card** (detect on GPIO38, mount
`/sdcard-data`). FAT32; layouts per Part B. (Production option: separate bus per slot.)

**D.3.5 Discrete inputs.** SELECT (GPIO10): LOW = selected IN; pull-up HIGH = OUT. PTT
(GPIO0): LOW = pressed (override). Each is a simple SPST to GND; debounce in software.

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
| **3.3 V** | ESP32-S3 (Wi-Fi off) + audio codec + audio output DAC/line driver + **two** microSD slots | ~90–180 mA | ~290 mA (SD init / SR burst) |
| **5 V** | Audio output line driver (if used; typically low-current line-level stage) | a few mA | ~50 mA (varies by line driver; **not the ~650 mA speaker-amp figure** — speaker amp removed) |
| **Lamp rail** | up to 2 legend halves | 0 (dark) | per lamp spec (e.g. 28 V incand.) |

The audio-input codec and the second microSD slot add a little to the 3.3 V rail; both
isolation transformers (input and output) are passive. Power from **USB 5 V ≥ 1 A** (the
removed MAX98357A was the dominant load; the new output stage is much lower current).
Keep a 28 V legend supply separate from logic 5 V (grounds common only). The audio-panel
input tap draws **no power from the aircraft** and is isolated through the transformer;
the audio-panel output stage is similarly isolated. Bulk decoupling ≥ 100 µF near the
line-driver VIN; 0.1 µF per device.

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
| Components | `esp-sr`, `esp_spiffs`, `driver`, `json` (cJSON), `fatfs`, `sdmmc`, `esp_driver_sdmmc`, `esp_codec_dev` (codec init for the digital/analog path) |
| Speech models | WakeNet `WN9_HIESP`; MultiNet English `mn6_en`/`mn7_en` (S3 only) |
| Partitions | factory app 3 MB + model 5 MB + storage 2 MB → needs **16 MB** flash (N16R8) |
| Audio input | ESP-SR AFE fed from I2S0 (codec ADC); **VAD→VOX** gating, PTT override; codec init from Config Card `audio.codec` |
| Audio output | I2S1 DAC to isolated output stage (isolation transformer → COM3-style audio-panel channel); **no onboard speaker in the installed build** (bench-test speaker-amp optionally substituted during development only) |
| Two-card load | Config Card first (`/sdcard-config/config.json`) → init audio source + VOX → then matching Data Card folder (`/sdcard-data/<aircraft>/`) |
| Grammar rules | lowercase + single spaces; spell numbers ("v one"); ~200-cmd cap |
| Fault behavior | any card/config fault → `ST_FAULT`, amber legend, **no checklist shown** (B.4) |

## D.9 Bill of materials (DIY build)

| Qty | Part | Spec / example |
|---|---|---|
| 1 | ESP32-S3 DevKit | DevKitC-1 **N16R8** (PSRAM) |
| 1 | **Audio-panel input codec** | I2S codec ADC with line-in: **ES8388 / ES7210** (need MCLK+I2C) or **PCM1808 / CS5343** (self-clocking) |
| 1 | **Audio isolation transformer** | 600 Ω:600 Ω aviation audio ground-loop isolator (**Allen Avionics AGL** series) |
| 1 | Input network | ~220–470 Ω series resistor + RC anti-alias for the analog tap |
| 1 | **Audio output isolation transformer** | 600 Ω:600 Ω line-level isolation transformer for the TX output stage (e.g. **Allen Avionics AGL series** or equivalent) — galvanic barrier on the COM3 output line |
| 1 | **Audio output DAC / line driver** | I2S DAC IC (e.g. PCM5102A class) or I2S-in line driver for the COM3 output stage; select based on output impedance and level requirements for the panel's COM3 input |
| *(bench only)* | I2S amp (bench test) | MAX98357A breakout — bench-test use only; not installed |
| *(bench only)* | Speaker (bench test) | 4–8 Ω, ≥ 2 W — bench-test use only; not installed |
| **2** | microSD card + breakout | FAT32 — **Config Card** (slot 1) + **Data Card** (slot 2) |
| 1 | Annunciator switch | Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench) |
| 2 | Lamp driver | logic-level N-MOSFET (2N7002/AO3400) or NPN (2N2222) |
| 4 | Resistors | 1 kΩ ×2 (gate), 10 kΩ ×2 (pulldown) |
| 2–4 | Pull-ups | 10 kΩ on SD CMD/DAT0; codec I2C pull-ups if needed |
| — | Caps | 0.1 µF per device/rail, 100 µF bulk near output line driver (if applicable) |
| 1 | PTT button | momentary SPST (or use BOOT) — **VOX override** |
| (opt.) | INMP441 MEMS mic | **bench-test input only**, not the installed source |

Integrated alternative: **ESP32-S3-Korvo-2** (~$45–55) provides codec/SD on-board; use
its BSP pin map and codec (ES8311/ES7210) init, repurpose its line-in for the audio-panel
receive feed, and add the isolated COM3 output stage externally (DAC/line driver +
output isolation transformer). A production unit adds the second card slot.

---

# PART E — ENCLOSURE SPECIFICATION (for the fabricating engineer)

The housing is **generic** — it is sized for the electronics and the panel interface, not
for a specific airframe. The only airframe-specific item is the **mounting variant**
(DZUS slot vs. round instrument hole) chosen for the target panel, and the card inside it.

## E.1 Two-piece architecture

| Piece | Contents | Where | Why |
|---|---|---|---|
| **A. Panel bezel** | Split-legend annunciator switch, **PTT override** button | Front panel / pedestal, on the **DZUS rail** | Crew must see/reach it; dark-cockpit annunciator in the normal scan. Speaker grille removed (no onboard speaker in the installed design). |
| **B. Remote processor box** | ESP32-S3, audio-input stage (isolation transformer + codec), **audio output stage** (DAC/line driver + isolation transformer for COM3 TX output), **two microSD card slots**, lamp-driver, power conditioning | Avionics bay / behind-panel, blind | Keeps heat, the card slots, and wiring out of the panel; close to the audio-panel tap and COM3 output point |

A single all-in-one box is acceptable for a pure bench demo, but the two-piece split mirrors
real remote-mount avionics and keeps the audio-input stage near the panel tap.

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
  OFF` white, bottom `VOICE CHKLST FAULT` amber, upright when installed); optional
  guarded/recessed PTT. **No speaker grille** — the onboard speaker is removed; checklist
  audio plays through the crew headsets via the COM3 output channel. The bezel height may
  be reduced from the prior 4-unit to 3-unit (28.575 mm) since the speaker cone space is
  freed (confirm against the chosen switch datasheet).
- **Material/finish:** 6061-T6 aluminum 2.0–3.0 mm (or ABS/PC for a non-structural demo);
  **matte black, low-gloss (≤ 10 gloss units)** to suppress glare; legend by the switch's
  internal engraving (preferred) or laser-etch + white/amber paint-fill; edges chamfered
  0.5 mm.

## E.3 Piece B — remote processor box

- **Envelope:** sized around the ESP32-S3 DevKitC-1 (≈ 70×26 mm) plus the audio-input stage
  (codec + input isolation transformer), the audio output stage (DAC/line driver + output
  isolation transformer), **two** microSD breakouts, and the 2-channel lamp-driver; practical
  outer **≈ 120 × 85 × 45 mm** (unchanged — the output stage is compact; confirm against the
  actual stacked board set with both transformers). Note: without the speaker-amp the box is
  no longer the largest dissipator; thermal path is simplified.
- **Mounting:** internal standoffs / M2.5 brass inserts — boards screwed down, not floating
  (vibration). Keep the audio-input stage and its shielded cabling away from the amp and the
  switching DC-DC; the isolation transformer mounts solidly (it is a magnetic part).
- **Card slots:** **two externally-swappable microSD carriers**, clearly and distinctly
  labeled **`CONFIG CARD — FAT32`** (slot 1) and **`DATA CARD — FAT32`** (slot 2), keyed or
  spaced so they cannot be confused/swapped; both swappable without opening the box. The
  Config Card carrier should accept a **write-protect-locked** card.
- **Access & connectors:** covered/recessed **USB-C** service port (bench use only); one
  keyed, positive-latching main connector (small MIL-circular or D-sub) carrying SELECT,
  both legend drives, PTT, power/ground (pinout from `board_pins.h`); **plus a separate,
  shielded, clearly-labeled `AUDIO IN (ISOLATED, RX ONLY)` connector** for the audio-panel
  receive tap — kept on its own keyed connector so it cannot be mis-mated; isolation
  transformer **inside** the box on the panel side of the codec; **plus a second separate,
  shielded, clearly-labeled `AUDIO OUT (ISOLATED, COM3)` connector** for the isolated
  TX output to the audio-panel COM3-style channel — on its own keyed connector, physically
  distinct from the input connector, with the output isolation transformer inside the box
  on the panel side of the output stage. The two audio connectors must be clearly distinct
  and impossible to swap (different keyings or physical separation). Accept USB 5 V ≥ 1 A;
  optional internal **28 V→5 V DC-DC** (≥ 1 A, reduced from prior ≥2 A now that the
  speaker-amp is removed) with TVS + fuse if a 28 V bus mock-up is wanted (mark as demo
  regulator, not DO-160 qualified).
- **Material/EMI:** aluminum preferred (doubles as EMI shield + heatsink); if plastic, add a
  grounded conductive shield liner/coating; single-point chassis ground stud bonded to the
  connector shell and ESP32 ground. Route the audio-in shield per the panel's grounding
  practice (often **grounded only at the intercom** — see C.3a).

## E.4 Audio, thermal, environmental, labeling

- **Audio:** No onboard speaker in the installed design — speaker/grille removed from both
  pieces. Checklist read-aloud audio is delivered in-headset via the isolated COM3 output
  channel. If a bench-test speaker output is optionally fitted on the development unit (see
  D.3.3b), it may be wired to a header on the processor box only; no speaker cutout on
  the panel bezel.
- **Thermal:** ESP32-S3 + ESP-SR is low-power (a few hundred mW) — **no fan.** Passive
  convection (vent slots low/high) or conduction (thermal pad to the aluminum wall). If
  sealed, verify internal rise < 20 °C above 55 °C ambient. DC-DC (if fitted) on its own
  thermal path.
- **Environmental:** design toward the DO-160G categories in **C.4** (Cat A2 temp, Cat S
  vibration, etc.) — design guidance for the prototype, formal test for a productized unit.
- **Labeling:** placard `DEMO / TRAINING ONLY — NOT FOR FLIGHT`; box exterior carries unit
  name, serial/asset field, the **two card-slot labels** (`CONFIG CARD` / `DATA CARD`,
  FAT32), the `AUDIO IN — ISOLATED, RX ONLY` connector marking (receive-only input tap),
  the `AUDIO OUT — ISOLATED, COM3` connector marking (TX output to audio-panel COM3 channel),
  and the USB "bench use only" note; annunciator legends `VOICE CHKLST OFF` (white) /
  `VOICE CHKLST FAULT` (amber); amber = caution, white = status per AC 25-11B.

## E.5 Deliverables & open items for the engineer

**Deliverables:** STEP + native 3D CAD of both pieces (boards + switch modeled in place);
fully-dimensioned 2D drawings (DZUS pattern, switch cutout from the chosen datasheet, grille,
connector cutouts; GD&T on the switch cutout and DZUS holes); connector pinout mapped to
`board_pins.h`; an FDM/SLA printable prototype for fit-check; a mechanical BOM; tolerances
(switch cutout ±0.1 mm, DZUS holes ±0.1 mm on the 9.525 mm pitch, general ±0.25 mm).

**Open items (confirm before CAD):** the **exact Applied Avionics switch part number** — the
single most critical dimension; nothing finalizes until it is fixed. Also: DZUS slot vs.
3-1/8 in round hole in the target panel; the **audio-panel input tap point, level, and
grounding** for the target installation (sets the input isolation-transformer + divider
design); the **audio-panel COM3-style output channel injection point, impedance, and level
requirements** (sets the output isolation transformer and line driver design — this is a
new open item from this revision); the **codec part** for the digital input path (sets the
I2C/MCLK init); the **output DAC/line driver part** (sets the COM3 output stage component
choice); and whether a 28 V input is wanted. **Speaker model is no longer an open item**
— the speaker is removed.

**Reference dimensions:** DZUS pitch 9.525 mm · DZUS hole 6.48 mm · backplate 1.6 mm · first
fastener offset 14.29 mm · pedestal panel width ≈ 146 mm · round instrument hole 79.4 mm ·
remote box ≈ 120 × 85 × 45 mm · two microSD slots · isolated `AUDIO IN (RX ONLY)` connector
(input tap) · isolated `AUDIO OUT (COM3)` connector (TX output to audio-panel COM3 channel)
· no onboard speaker in the installed design.

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
- Allen Avionics **AGL audio ground-loop isolation transformers** (analog audio-panel tap) — https://www.allenavionics.com/categories/agl-audio-ground-loop-isolation-transformers
- Everest-Semi **ES8388** audio codec (line-in I2S ADC, MCLK + I2C) — https://dl.radxa.com/rock2/docs/hw/datasheet/ES8388%20user%20Guide.pdf
- **ES7210** multichannel audio ADC (Espressif-supported codec) — https://docs.espressif.com/projects/esp-adf/en/latest/design-guide/dev-boards/board-esp32-s3-korvo-2.html
- TI **PCM1808** stereo audio ADC (self-clocking I2S input) — https://www.ti.com/lit/ds/symlink/pcm1808.pdf
- Espressif **ESP-SR** AFE / VAD (voice-activity detection for VOX) — https://github.com/espressif/esp-sr
- INMP441 microphone datasheet (bench-test option only) — https://www.farnell.com/datasheets/1824785.pdf
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
