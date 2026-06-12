# Change Notes — COM3 TX Output Architecture Revision

**Date:** June 2026  
**Change:** Add dedicated galvanically-isolated COM3-style audio output channel; remove onboard speaker/amplifier.  
**Status:** Source files edited (Markdown + Python). No PDFs rebuilt. No git commit. DEMO/TRAINING ONLY framing preserved throughout.

---

## Summary of the architectural change

| Was | Now |
|---|---|
| Receive-only on a single audio tap; output via onboard speaker/amplifier (not fed back to panel) | Receive-only isolated INPUT tap (unchanged) + separate, dedicated, galvanically-isolated OUTPUT into a COM3-style audio-panel aux channel; onboard speaker/amplifier removed from installed design |
| "Cannot transmit, inject into, or back-feed the panel" (absolute) | "Cannot transmit, inject into, or back-feed via the INPUT tap" (scoped); OUTPUT is an intentional, isolated, advisory audio injection into one dedicated aux channel only |
| NORSEE posture: receive-only isolated tap as cert crux | NORSEE posture maintained; isolated COM3 output is flagged as the most significant new interface-risk item; isolation design + safety assessment required |

---

## File 1: `firmware/docs/MASTER_SPEC.md`

### Intro paragraph (~line 18–34)
Added: checklist audio now plays out to audio panel via isolated COM3-style output channel; onboard speaker removed; INPUT and OUTPUT are separate paths on separate connectors; COM3 output is the most significant interface-risk change in this revision.

### Document map row C (~line 47)
Updated: added reference to both the INPUT tap and the isolated COM3-style OUTPUT injection channel and the added cert risk.

### A.1 "is / is not" table (~line 61)
Updated "Receive-only" cell: now reads "Receive-only on the audio-panel INPUT tap… plus a separate, galvanically-isolated OUTPUT into a dedicated COM3-style channel." Updated "is not" cell: still not a transmitter on aircraft COM radios, but acknowledges the advisory audio injection into the dedicated aux channel via isolated output.

### A.1 paragraph (~line 66–80)
Rewrote: two electrically separate, galvanically-isolated channels (isolated INPUT tap + isolated COM3-style OUTPUT); INPUT receive-only language preserved for INPUT side; COM3 output described as most significant cert/interface-risk item in this revision (supersedes prior "audio-panel tap" note).

### A.2 architecture table (~line 88)
Replaced "Speaker + amplifier (I2S)" row with "Audio-panel output stage (isolated TX to COM3-style channel)" — describes isolated line-level output stage, removed speaker, separate connector from input tap, isolation transformer on TX line.

### A.3 safety model, rule 3 (~line 118–135)
Rewrote rule 3: now "Dual-isolated-channel interface" — describes both channels explicitly: receive-only INPUT tap (cannot back-feed via this path) and isolated OUTPUT into dedicated COM3-style channel (isolation transformer ensures cannot key/jam/load required channels). COM3 output is flagged as the most significant cert/interface-risk item.

### C.3 DO-178C-avoidance argument, leg 3 (~line 359–371)
Rewrote: "Bounded dual-isolated interface" — two ties to aircraft system, both isolated; output injection is more invasive than receive-only tap; argument now rests on isolation + directionality + channel separation.

### C.3 honest caveats (~line 382–393)
Updated: "receive-only isolated interface" → "dual-isolated-channel interface"; updated installation-bar bullet to note output channel raises bar further.

### C.3a Audio-panel interface impact (~line 401–452)
Major rewrite: section now covers BOTH interfaces. New two-column table distinguishes INPUT tap vs. OUTPUT channel properties (directionality, isolation, fault containment, channel separation, operational credit). Added "Why the output channel raises the bar" subsection with three explicit risk items: (a) isolation/failure modes — fault must not key/jam/back-feed; (b) interference with required COM audio; (c) masking/intelligibility human-factors. All prior INPUT-tap concerns retained.

### C.4 DO-160G audio-interface note (~line 489–497)
Updated: now addresses both paths — input tap degradation check and output isolation/keying/masking check.

### C.5 installation path note (~line 519–526)
Updated: output channel raises install classification further; approval must substantiate both input tap and isolated COM3 output.

### C.7 compliance matrix (~line 565–566)
Replaced single "Audio-panel interface" row with two rows: one for INPUT tap (substantiation pending) and one for OUTPUT (COM3 channel) flagged explicitly as most significant new interface-risk item — isolation design + safety assessment required.

### D.1 system overview table (~line 588)
Updated "Audio output" row: describes I2S_NUM_1 → isolated line-level output stage → COM3-style audio-panel channel; speaker removed; bench-test-only speaker noted. Updated build paths paragraph: removed MAX98357A from installed path, added isolated output stage description.

### D.2 Master pin map (~line 620–622)
Renamed macros: `SPK_BCLK_GPIO` → `AOUT_BCLK_GPIO`, `SPK_LRCLK_GPIO` → `AOUT_LRCLK_GPIO`, `SPK_DOUT_GPIO` → `AOUT_DOUT_GPIO`. Updated notes: now describe isolated output stage DIN; bench-test note added.

**Judgment call on pins:** GPIO15/16/17 retained for audio output (same as former speaker-amp I2S assignments). This keeps the firmware I2S_NUM_1 driver unchanged; only the physical output hardware changes (DAC + isolation transformer instead of speaker-amp). Parent should verify this assignment is acceptable in `board_pins.h`.

### D.3.3 (section renamed and split)
Old D.3.3 (MAX98357A amp) replaced by:
- **D.3.3a** — Isolated audio output stage → COM3-style channel (the installed output). Describes I2S DAC → isolation transformer → line-level TX → COM3 audio-panel channel. Flags open item: exact I2S DAC part and output isolation transformer must be confirmed by bench engineer. Suggested options: PCM5102A-class DAC + Allen Avionics AGL transformer.
- **D.3.3b** — Bench-test speaker output (MAX98357A, GPIO15/16/17 — bench only, not installed). Retains the full MAX98357A wiring note for bench use.

### D.6 Power budget (~line 748–758)
Updated: 5V rail now shows low-current output line driver instead of 650 mA speaker-amp; note that removed MAX98357A was dominant load.

### D.8 Firmware build notes
Added "Audio output" row: I2S1 DAC to isolated output stage; no onboard speaker in installed build.

### D.9 BOM (~line 803–806)
Removed: `I2S amp (MAX98357A)` and `Speaker` as installed items. Added: `Audio output isolation transformer` (600Ω:600Ω, e.g. Allen Avionics AGL series) and `Audio output DAC / line driver` (e.g. PCM5102A class). Both former items retained as `(bench only)` line items.

**Judgment call on BOM:** PCM5102A suggested as example I2S DAC for output stage. The exact part and output isolation transformer must be confirmed by bench engineer against the specific audio panel's COM3 input impedance and level requirements.

### Part E — Enclosure
- **E.1 table:** Piece A no longer lists speaker+grille. Piece B now includes "audio output stage (DAC/line driver + isolation transformer for COM3 TX output)."
- **E.2 bezel face layout:** Speaker grille removed. Note added that bezel height may be reduced from 4-unit to 3-unit (28.575 mm) now that speaker cone space is freed (confirm against switch datasheet).
- **E.3 processor box:** Envelope note updated (output stage is compact, no change to ~120×85×45 mm estimate). Mounting note: route input and output audio cables separately, both shielded. Connector section: added second `AUDIO OUT — ISOLATED, COM3` connector (separate, keyed, distinct from input connector); DC-DC requirement reduced from ≥2A to ≥1A (speaker-amp removed).
- **E.4 audio:** Speaker paragraph replaced — no onboard speaker in installed design; bench-test speaker optional on development unit only, no speaker cutout on panel bezel.
- **E.4 labeling:** Added `AUDIO OUT — ISOLATED, COM3` connector marking.
- **E.5 open items:** Speaker model removed as open item; two new open items added: (1) audio-panel COM3 output channel injection point, impedance, and level requirements; (2) output DAC/line driver part selection.
- **Reference dimensions:** Updated — removed "speaker 4–8 Ω ≥ 2 W"; added both `AUDIO IN (RX ONLY)` and `AUDIO OUT (COM3)` connectors; "no onboard speaker in the installed design."

---

## File 2: `ip/provisional_patent_application.md`

### Title
Changed from "...Receive-Only, Galvanically-Isolated Aircraft Audio-Panel Tap..." to "...Galvanically-Isolated Receive-Only Audio-Panel Tap and a Dedicated Galvanically-Isolated Audio-Panel Output Channel..."

### Field of the Invention
Updated: now mentions both the receive-only isolated INPUT tap and the separate dedicated galvanically-isolated OUTPUT channel (COM3-style); notes the two are on separate paths; notes no onboard speaker in installed configuration.

### Summary — audio-input stage bullet
Narrowed the "cannot transmit/inject" language to the INPUT TAP path specifically: "via this INPUT path the apparatus cannot transmit on, key, mute, inject into, or back-feed the audio panel."

### Summary — NEW audio OUTPUT stage bullet (inserted between existing bullets)
New bullet added: describes the dedicated galvanically-isolated OUTPUT stage — I2S DAC + isolation transformer → COM3-type aux channel; OUTPUT on separate path and separate connector from INPUT; fault cannot key/jam/load/back-feed required channels; advisory injection only; dual-isolated-channel architecture noted as potentially novel.

### Summary — read-aloud playback bullet
Changed from "through the apparatus's own speaker/amplifier (not fed back into the aircraft audio panel)" to "through the dedicated, galvanically-isolated audio-panel OUTPUT channel (COM3-type)." Onboard speaker removed; bench-test-only exception noted.

### Summary combination paragraph
Updated to include COM3 isolated OUTPUT channel and the dual-isolated-channel architecture (electrically separate, independent isolation barriers) as potentially novel.

### FIG. 1 caption
Updated: "amplifier/speaker" → "isolated audio output stage → audio-panel COM3-style channel."

### Detailed Description §1 overall architecture
Updated: device now connects through two electrically separate channels; no onboard speaker in installed configuration.

### Detailed Description §2 input stage
Narrowed "cannot inject" to INPUT path only. Added pointer to new §2a.

### Detailed Description — NEW §2a (inserted)
New section: audio-panel output stage (dedicated isolated COM3-style channel). Describes output chain, isolation transformer on TX line, fault containment, channel separation from INPUT, dual-isolated-channel architecture framing.

### Detailed Description §4 playback
Changed from "device's own amplifier and speaker" and "never routed back into the audio panel" to playback through "dedicated, galvanically-isolated COM3-style audio-panel OUTPUT channel."

### Detailed Description §7 hardware
Replaced "Class-D amplifier driving a 4–8 ohm speaker" with "I2S DAC / line driver followed by a second isolation transformer for the COM3 audio output path."

### Detailed Description §8 certification posture
Updated: device now has two isolated channels; COM3 output flagged as most significant interface-risk item; isolation design + safety assessment required.

### Claims 1, 2, 10
Claim 1: Rewritten to include dedicated isolated audio-output stage (COM3-type) and dual-isolated-channel architecture. Removed "speaker separate from the audio panel" language.
Claim 2: Narrowed to "via the input path."
Claim 10 (method): Changed "reading aloud through a separate speaker" to "playing through a separate, dedicated, galvanically-isolated OUTPUT channel of the audio panel."

### Claims 13, 14 (NEW)
Two new claim-style statements directed to the dual-isolated-channel architecture:
- Claim 13: Both input and output stages have independent isolation barriers; no shared conductive path; enables receive + in-headset delivery while maintaining electrical separation on both paths.
- Claim 14: Output stage isolation barrier is a line-level isolation transformer between I2S DAC output and COM3 channel input; fault cannot key/jam required COM channels.

### Abstract
Rewritten to describe both channels (receive-only INPUT tap + dedicated isolated COM3 OUTPUT) and the dual-isolated-channel architecture.

### Prosecution notes
Major additions:
- Narrowed "cannot inject" claim to INPUT tap only; flagged architecture change.
- Added: prior-art search did NOT cover audio-panel audio injection; attorney must refresh search before nonprovisional filing.
- Added: potential new novelty — dual-isolated-channel architecture (claims 13/14).
- Updated strongest claims ranking: dual-isolated-channel architecture is new anchor.
- FIG. 1 update flagged.

---

## File 3: `ip/IP_Research_Report_and_Filing_Roadmap.md`

### Section 2 feature table — Feature 2
Revised: INPUT tap white space (established) + new OUTPUT channel (prior-art search not yet run); dual-isolated-channel architecture flagged as new potential novelty; absolute "cannot inject" claim narrowed to INPUT tap.

### Section 3 white-space conclusion
Added:
- OUTPUT feature is outside original search scope — freedom-to-operate/patentability for output path unverified; attorney must run additional search.
- Dual-isolated-channel architecture identified as candidate new novelty angle, no search conducted.
- All other white-space findings (Features 4, 5) unchanged and standing.

Updated patentability assessment: output channel and dual-channel architecture may add independent novelty; requires additional prior-art search.

### Section 7 honest caveats
Added bullet: architecture changed after original prior-art search (speaker removed, isolated COM3 output added); prior-art search scope for the output feature is missing; attorney must refresh before relying on white-space conclusions for the output path; receive-tap findings unaffected.

---

## File 4: `firmware/docs/wiring_diagram.py`

### Subtitle text
Updated to include both input (isolated I2S codec, RX-only) and output (isolated TX to COM3 channel).

### Net color comment for C_I2S_S
Updated: "speaker I2S" → "audio-out I2S to COM3 isolated output stage."

### ESP32-S3 right-side pin labels (G15/G16/G17)
Updated: `G15 BCLK` → `G15 AOUT BCLK`, `G16 LRC` → `G16 AOUT LRC`, `G17 DIN` → `G17 AOUT DOUT`.

### SPEAKER AMP block — replaced entirely
New block: `AUDIO-PANEL OUTPUT (COM3) — ISOLATED TX to dedicated aux channel`. Contains:
- Title and description labels (I2S DAC + isolation xfmr + line-level out; cannot key/jam/back-feed; separate connector from AUDIO IN)
- Three I2S input pins (BCLK/LRC/DIN) on left side
- Output description: "Line-level out → 600 ohm isolation xfmr → COM3-style audio-panel input"
- Bench note: MAX98357A substitutable on GPIO15/16/17 for bench testing only
- Arrow symbol pointing right, labeled "to audio panel / COM3 in"

Block repositioned: `ax=1170` (was 1230), `aw=380` (was 300), `ah=250` (was 210) — wider and taller to accommodate added descriptive text.

### Speaker symbol — removed
The speaker cone SVG path, the "4–8 Ω" label, and the decorative 5V wire to the speaker are removed.

### I2S wire routing to the COM3 output block
Updated: three wires from ESP right-side pins G15/G16/G17 now route to the new AUDIO-PANEL OUTPUT block's BCLK/LRC/DIN pins at updated coordinates. The old decorative 5V → amp VIN and GND → amp GND wires are removed (output stage is lower-current; no separate amp VIN wire drawn).

### Power rail box
Updated: "amp VIN (best output)" → "output line driver (low-current)"; budget note changed from "amp adds up to ~650 mA peak" to "output line driver is low-current (~50 mA max); speaker amp removed."

### Net key
Updated: "Speaker I2S" → "Audio-out I2S (RX)" / "Audio-out I2S (COM3 TX)" for the two I2S net colors. Input I2S labeled "Audio-in I2S (RX)."

---

## Judgment calls and open items for parent to double-check

1. **GPIO15/16/17 for audio output (D.2 pin map, wiring diagram).** Retained as `AOUT_BCLK/LRCLK/DOUT` macros, matching the former speaker-amp I2S assignments. This keeps the firmware I2S_NUM_1 driver unchanged. **Parent should verify `board_pins.h` macro names are updated to match** (`SPK_BCLK_GPIO` → `AOUT_BCLK_GPIO` etc.) and that no other firmware source file hard-codes the old `SPK_*` macro names.

2. **Output DAC / line driver part unspecified (D.9 BOM, D.3.3a).** PCM5102A-class suggested as an example I2S DAC. The bench engineer must confirm the specific part, output impedance, level, and whether it can drive a 600Ω isolation transformer directly or needs a buffer stage. This is flagged as an open item in E.5.

3. **Output isolation transformer type (D.9 BOM, D.3.3a).** Allen Avionics AGL series suggested (same family as input transformer). Exact part must be confirmed against the audio panel's COM3 input impedance and the required injection level. The cert posture assumes a 600Ω:600Ω line-level transformer; confirm this is appropriate for the target panel's COM3 input.

4. **Wiring diagram coordinate layout.** The AUDIO-PANEL OUTPUT block was repositioned to `ax=1170` (wider, 380 px) to fit the new descriptive text. The annunciator block (`gx=1150, gy=540`) now sits below and slightly overlapping the right edge of the output block. Parent should render the SVG and check for visual overlap between the top-right output block and the annunciator block header; a small vertical offset on the annunciator may be needed.

5. **IP prosecution (important — for attorney).** The prior absolute "receive-only/cannot back-feed" novelty framing has been re-scoped. The receive INPUT tap remains receive-only. The new OUTPUT path is an intentional, isolated, advisory audio injection. The attorney must run an additional prior-art search covering intercom/audio-panel audio injection before filing the nonprovisional. The dual-isolated-channel architecture (claims 13/14) is a new potential novelty anchor that has not been searched.

6. **Part C certification — FAA ACO pre-application.** The COM3 output is the most significant new interface-risk item. The ACO pre-application meeting must now explicitly cover: (a) output isolation failure modes; (b) non-interference with required COM channels; (c) masking/intelligibility human factors. The NORSEE posture is maintained but the certification argument is weaker for the output path — see C.3a.

---

> DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS. This change note describes design and IP documentation changes only; no approvals have been obtained.

---

## build_master.py + TECH_DATA.md alignment

**Files edited:**
- `/home/user/workspace/cj2-checklist/firmware/docs/build_master.py`
- `/home/user/workspace/cj2-checklist/firmware/docs/TECH_DATA.md`

**Validation:** `python3 -c "import ast; ast.parse(...)"` → **OK**. Zero SPK_ hits in all three files. All receive-only references correctly scoped to INPUT tap. All MAX98357A/speaker/650 mA references marked bench-only.

---

### build_master.py changes (section by section)

#### A.1 is/is-not table (~L233)
- **Was:** `"Receive-only on a single audio tap; no command/data to any aircraft system"` / `"A transmitter, a panel control, or an interface to avionics/engines/controls"`
- **Now:** Dual-channel: receive-only on the INPUT tap + separate galvanically-isolated OUTPUT into dedicated COM3-style channel; "is not" cell updated to acknowledge advisory audio injection into one dedicated aux channel via isolated output (not required COM radios).

#### A.1 paragraph (~L243–248)
- **Was:** "galvanically-isolated, receive-only audio tap" as the sole cert foundation; "electrically independent" language traded for "receive-only, isolated".
- **Now:** Two electrically separate, galvanically-isolated channels (receive-only INPUT tap + isolated COM3-style OUTPUT); INPUT receive-only language preserved for INPUT path; OUTPUT flagged as most significant cert/interface-risk change; dual-isolated-channel architecture named as the cert foundation.

#### A.2 architecture table (~L256)
- **Was:** `"Speaker + amplifier (I2S)"` → `"Reads checklist items aloud (own speaker; not fed back to the panel)"`
- **Now:** `"Audio-panel output stage (isolated TX to COM3-style channel)"` → describes isolated line-level output stage, isolation transformer on TX line, crew hears in-headset, onboard speaker/amplifier removed, separate channel and connector from INPUT tap.

#### A.3 safety rule 3 (~L286–292)
- **Was:** `"Receive-only, isolated interface"` — single INPUT tap, unit cannot transmit/key/mute/back-feed the panel.
- **Now:** `"Dual-isolated-channel interface"` — describes both channels: (a) receive-only isolated INPUT tap (cannot transmit/key/mute/back-feed via this path); (b) isolated OUTPUT into COM3-style channel (isolation transformer; cannot key/jam/load/back-feed panel's other channels or required COM radios). COM3 output flagged as most significant cert/interface-risk item.

#### C.3 DO-178C-avoidance leg 3 (~L538–544)
- **Was:** `"Bounded interface (not full independence)"` — one tie, receive-only isolated audio tap.
- **Now:** `"Bounded dual-isolated interface"` — two ties, both isolated; output injection is more invasive than receive-only tap; argument rests on isolation + directionality + channel separation rather than total receive-only.

#### C.3 caveats box — "receive-only isolated interface" and installation-bar bullet
- Updated "receive-only isolated interface" → "dual-isolated-channel interface (receive-only input tap + isolated output into a dedicated COM3-style channel)".
- Updated installation-bar bullet: now says output channel raises the bar further, wires into aircraft communication system for both receive and transmit.

#### C.3a intro paragraph
- **Was:** "Tapping the aircraft audio panel is the single biggest certification change..."
- **Now:** Two interfaces (INPUT tap + COM3 OUTPUT); both must be argued; output path is the more significant of the two.

#### C.3a directionality/isolation table (~L579–590)
- **Was:** Single-column "Design commitment" table; Directionality = "Receive-only. No DAC, line-driver, or PTT line going to the panel."
- **Now:** Two-column table: `INPUT tap (receive-only)` vs `OUTPUT channel (isolated TX to COM3)` across all properties (Directionality, Isolation, Fault containment, Channel separation, No operational credit). The old blanket "no DAC/line-driver/inject" claim is replaced with a dual-path truth.

#### C.3a "Why it nonetheless raises the bar" bullets
- **Was:** Three INPUT-only bullets (STC path, comm audio degradation, grounding).
- **Now:** Three output-specific bullets matching MASTER_SPEC C.3a: (a) isolation/failure modes — fault must not key/jam/back-feed; (b) non-interference with required COM audio; (c) masking/intelligibility human factors; plus STC/approval bullet for both channels.

#### C.4 audio-interface callout box (~L657)
- Updated to cover both paths: receive tap (existing check) + output channel (isolation, keying/jamming, masking checks).

#### C.5 installation-path callout box (~L679–684)
- Updated: "audio tap" → "audio-panel interface for both receive and transmit"; approval must substantiate both the receive-only input tap and the isolated COM3-style audio output.

#### C.7 compliance matrix (~L724)
- **Was:** Single `"Audio-panel interface"` row — receive-only + galvanic isolation.
- **Now:** Two rows:
  - `Audio-panel interface — INPUT tap` (receive-only + galvanic isolation; cannot key/jam/back-feed via input path)
  - **`Audio-panel interface — OUTPUT channel (COM3)`** (galvanically-isolated line-level TX; isolation transformer; flagged as most significant new interface-risk item; isolation design + safety assessment required before productization)
- `Installation` row: updated wording to "both input tap and isolated COM3 output".

#### D.1 system overview table (~L760)
- **Was:** `"I2S Class-D amplifier on I2S_NUM_1 → 4–8 Ω speaker (own speaker; not fed to the panel)"`
- **Now:** `"I2S_NUM_1 DAC → isolated line-level output stage (isolation transformer + line driver) → dedicated COM3-style audio-panel input channel; crew hears checklist read-aloud in-headset. Onboard speaker/amplifier removed."`

#### D.1 build-path paragraph (~L769)
- **Was:** `"+ MAX98357A amp + two microSD breakouts"`
- **Now:** `"+ isolated audio output stage [I2S DAC → isolation transformer → line-level TX to COM3 channel] + two microSD breakouts"`. MAX98357A and INMP441 named as bench-test-only items.

#### D.2 pin map (~L792–794)
- **Was:** `"Speaker bit clock / word select / data out"` with `SPK_BCLK_GPIO / SPK_LRCLK_GPIO / SPK_DOUT_GPIO` on GPIO15/16/17 `"→ amp BCLK/LRC/DIN"`
- **Now:** `"Audio-out bit clock / word select / data"` with `AOUT_BCLK_GPIO / AOUT_LRCLK_GPIO / AOUT_DOUT_GPIO` on GPIO15/16/17 (same pins) `"→ isolated audio-out (COM3) line driver/DAC"`. Bench-test note for MAX98357A added to DOUT row.

**Judgment call:** GPIO15/16/17 retained for audio output — same as former speaker-amp I2S assignments, keeps firmware I2S_NUM_1 driver unchanged; only physical output hardware changes.

#### D.3.1 digital path note (~L835)
- Updated: "no I2S output toward the panel" scoped to "no data line driven back via this input path"; added pointer to D.3.3a for the separate I2S_NUM_1 output.

#### D.3.3 → split into D.3.3a + D.3.3b (~L855–858)
- **Was:** `"D.3.3 MAX98357A Class-D amp"` — the installed output, drives own speaker, never routed back to panel.
- **Now:**
  - **D.3.3a** — Installed isolated audio output stage → COM3-style channel (I2S_NUM_1, GPIO15/16/17). Describes output chain, isolation transformer on TX line, fault cannot key/jam/back-feed. Flags open item: exact I2S DAC and isolation transformer must be confirmed. Suggests PCM5102A-class DAC + Allen Avionics AGL series transformer.
  - **D.3.3b** — Bench-test speaker output (MAX98357A, not installed). Full wiring retained; explicitly NOT the installed output.

#### D.6 power budget (~L914)
- **Was:** `"5V: MAX98357A output → ~650 mA peak"`
- **Now:** `"5V: Audio output line driver (installed; low-current) → ~50 mA peak (not the ~650 mA speaker-amp figure — speaker amp removed)"`. 3.3V row updated to include audio output DAC/line driver.
- Power paragraph: removed MAX98357A was dominant load note; bulk decoupling moved from "near amp VIN" to "near output line driver"; output isolation transformer noted as passive.

#### D.9 BOM (~L972–973)
- **Was:** `"I2S amp: MAX98357A breakout"` and `"Speaker: 4–8 Ω ≥ 2 W"` as installed items.
- **Now:** Both moved to `(bench only)` rows. Added installed items:
  - `Audio output isolation transformer` (600Ω:600Ω, e.g. Allen Avionics AGL series)
  - `Audio output DAC / line driver` (e.g. PCM5102A class)
- Caps row: "bulk near amp" → "bulk near output line driver (if applicable)".
- Korvo-2 paragraph updated: repurpose line-in for receive feed; add isolated COM3 output stage externally.

#### Part E enclosure

**E.1 two-piece table (~L1017–1018):**
- Piece A: removed "speaker + grille" from contents. Added "Speaker grille removed" note.
- Piece B: renamed to "Remote processor box"; added "audio output stage (DAC/line driver + isolation transformer for COM3 TX output)"; updated "close to the audio-panel tap and COM3 output point".

**E.2 bezel (~L1030, L1037):**
- DZUS height note: removed "if the grille needs room"; noted speaker cone space freed so 3-unit height is now achievable (confirm against switch datasheet).
- Face layout: removed "speaker grille"; added "No speaker grille — onboard speaker removed; audio via COM3 output channel; bezel height may be reduced to 3-unit".

**E.3 processor box (~L1046–1064):**
- Envelope: replaced "amp" with "audio output stage (DAC/line driver + output isolation transformer)"; noted box likely lighter/cooler without speaker-amp.
- Mounting: updated to route input and output audio cables separately, both shielded.
- Access & connectors: removed "speaker +/−" from main connector pin list; added `AUDIO OUT — ISOLATED (COM3)` connector (separate, keyed, distinct from AUDIO IN connector, output isolation transformer inside box); DC-DC requirement reduced from ≥2A to ≥1A.

**E.4 audio (~L1074–1075):**
- **Was:** `"4–8 Ω ≥ 2 W speaker, sealed-back or small rear volume; grille ≥ 40% open"`
- **Now:** No onboard speaker in installed design; speaker/grille removed; audio in-headset via COM3 output; bench-test speaker optionally on processor box header only, no speaker cutout on bezel.

**E.4 labeling (~L1083–1084):**
- Added `AUDIO OUT — ISOLATED, COM3` connector marking.

**E.5 deliverables + open items (~L1092, L1099–1102):**
- Removed "grille" from 2D drawings deliverables.
- Open items: removed "speaker model (sets grille open area + rear-volume cavity)"; added two new open items: (1) audio-panel COM3 output injection point, impedance, and level requirements; (2) output DAC/line driver part.

**E.5 reference dimensions (~L1108):**
- Removed `"speaker 4–8 Ω ≥ 2 W"`; added `AUDIO IN (RX ONLY)` and `AUDIO OUT (COM3)` connector markings; added "no onboard speaker in the installed design".

#### Part F references (~L1141–1142)
- MAX98357A datasheet and breakout guide refs **retained** (bench-test amp is still documented); labels updated to append "(bench-test amp only)".
- No PCM5102A datasheet URL added (none in MASTER_SPEC references; DAC part is still an open item).

---

### TECH_DATA.md changes

**Section 1 system overview table:**
- Mic input row replaced with "Crew audio input — From the aircraft audio panel on I2S_NUM_0, analog/digital selectable; onboard MEMS mic bench-test only".
- Audio output row: I2S Class-D amplifier → speaker replaced with isolated line-level output stage → COM3-style channel; onboard speaker/amplifier removed; MAX98357A bench-test-only.

**Section 1 build paths:**
- Integrated path: removed NS4150 amp; added "add isolated COM3 output stage externally".
- DIY path: replaced INMP441 + MAX98357A with audio-panel input stage (isolation transformer + codec) + isolated audio output stage (I2S DAC → isolation transformer → COM3); INMP441 and MAX98357A noted as bench-test only.

**Section 2 pin map (~L50–52):**
- `SPK_BCLK_GPIO` / `SPK_LRCLK_GPIO` / `SPK_DOUT_GPIO` on GPIO15/16/17 → `AOUT_BCLK_GPIO` / `AOUT_LRCLK_GPIO` / `AOUT_DOUT_GPIO` on same pins. Net column: "spk I2S" → "audio-out I2S". Notes: "→ amp BCLK/LRC/DIN" → "→ isolated audio-out (COM3) line driver/DAC". Bench-test note for MAX98357A added to DOUT row.

**Section 3.2 header + body:**
- Header renamed from "MAX98357A Class-D amplifier" to "Isolated audio output stage → COM3-style audio-panel channel (I2S_NUM_1) — installed output".
- New opening paragraph describes installed output chain (I2S DAC → DAC/line driver → isolation transformer → COM3 channel) and fault containment.
- MAX98357A wiring retained under "Bench-test-only option" subheading with explicit "NOT the installed output" notice.

**Section 5 power budget:**
- 3.3V: added audio output DAC/line driver; typical/peak updated to ~90–180 mA / ~290 mA.
- 5V: MAX98357A → "Audio output line driver (installed; low-current)"; peak changed from ~650 mA to ~50 mA (not the speaker-amp figure; speaker amp removed).
- Paragraph: "Reserve headroom for the amp's peak" → removed MAX98357A note; bulk decoupling moved to "near output line driver".

**Section 6 BOM:**
- INMP441 row replaced with "Audio-panel input codec" (ES8388/ES7210 or PCM1808/CS5343).
- Added: `Audio isolation transformer (input)` (600Ω:600Ω Allen Avionics AGL), `Audio output isolation transformer`, `Audio output DAC / line driver` (e.g. PCM5102A class).
- MAX98357A and Speaker rows moved to `(bench only)`.
- Caps row: "near amp" → "near output line driver".
- Korvo-2 paragraph updated to match: repurpose line-in for receive feed; add isolated COM3 output stage externally.

**Section 7 Korvo-2 differences:**
- NS4150 amp noted as not used in installed configuration; isolated COM3 output stage added externally on AOUT_BCLK/LRCLK/DOUT lines.
- Dual mics noted as bench input; installed input is audio-panel tap.

---

### Judgment calls

1. **GPIO15/16/17 retained for AOUT macros.** Same pins as former SPK_ assignments. Firmware I2S_NUM_1 driver unchanged; only physical output hardware changes (DAC + isolation transformer instead of speaker-amp). Consistent across all three files.

2. **PCM5102A named as example output DAC.** MASTER_SPEC uses "PCM5102A class" as an example; no specific datasheet URL added to references (exact part must be confirmed by bench engineer — flagged in D.3.3a and E.5 open items). No PCM5102A reference row added to Part F because MASTER_SPEC does not add one.

3. **Allen Avionics AGL series suggested for output isolation transformer.** Same family as input transformer. Exact part must be confirmed against COM3 input impedance and injection level. Flagged as open item in D.3.3a and E.5.

4. **MAX98357A references retained in Part F.** MASTER_SPEC F/references section retains MAX98357A datasheet and Adafruit guide; labels updated to "(bench-test amp only)" to match honest framing.

5. **TECH_DATA.md is a legacy/superseded document.** Edits kept minimal and consistent with MASTER_SPEC. Section 3.1 (INMP441 mic) is retained as written (it is bench-test only per the existing doc); only the audio OUTPUT section (3.2) and the pin map, power, BOM, and system overview rows were updated. The existing Section 3.1 INMP441 content already includes "This is not the installed audio source" framing from prior edits.

---

> DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS. This change note describes design and documentation changes only; no approvals have been obtained.

## build_packet.py + build_enclosure.py alignment

### build_packet.py

**§1 System Overview table (L217–219)**
- `"Mic input"` row renamed to `"Audio input"`: now describes galvanically-isolated audio-panel tap on I2S_NUM_0 (codec ADC / analog line tap, selectable per install). INMP441 explicitly labelled bench-test only.
- `"Audio output"` row replaced: now describes isolated line driver / DAC (PCM5102A-class) on I2S_NUM_1 → output isolation transformer → line-level out to dedicated COM3-style audio-panel channel. MAX98357A speaker-amp labelled bench-test only; no onboard speaker in installed build.
- `"Config storage"` updated to two-slot model: Config Card (slot 1) + Data Card (slot 2).
- Added `"Audio I/O posture"`, `"Install input source"`, and `"Install output"` rows clarifying the dual-isolated-channel architecture and that this is NOT a COM-radio transceiver.

**§1 DIY build description (L228)**
- Replaced INMP441 + MAX98357A with: audio-panel input stage (isolation transformer + I2S codec ADC; INMP441 bench-only) + isolated audio output stage (PCM5102A-class DAC + output isolation transformer → COM3 channel; MAX98357A speaker-amp bench-only) + **two** microSD breakouts (Config Card slot 1 + Data Card slot 2).

**§2 Master Pin Map (L242–250) — macro rename: SPK_→AOUT_, MIC_→AIN_**
- Rows 242–244: `"Mic bit clock/word select/data in"` with `MIC_BCLK_GPIO / MIC_LRCLK_GPIO / MIC_DIN_GPIO` on GPIO 4/5/6 → renamed to `"Audio-in bit clock/word select/data"` with `AIN_BCLK_GPIO / AIN_LRCLK_GPIO / AIN_DIN_GPIO`; notes updated to "I2S0 BCLK/WS → audio-panel input codec ADC / tap (RX)".
- Rows 248–250: `"Speaker bit clock/word select/data out"` with `SPK_BCLK_GPIO / SPK_LRCLK_GPIO / SPK_DOUT_GPIO` on GPIO 15/16/17 → renamed to `"Audio-out bit clock/word select/data"` with `AOUT_BCLK_GPIO / AOUT_LRCLK_GPIO / AOUT_DOUT_GPIO`; notes updated to "I2S1 BCLK/WS/DOUT → isolated audio-out (COM3) line driver/DAC → isolation transformer → COM3-style audio-panel channel".
- Added two new card-detect rows: `SD_CFG_CD_GPIO` (GPIO47, Config Card) and `SD_DAT_CD_GPIO` (GPIO38, Data Card), mirroring MASTER_SPEC §D.4.

**§3.1 Per-Device Wiring — audio input section (was "INMP441 MEMS Microphone")**
- Reframed entirely: installed input is the galvanically-isolated audio-panel tap. Describes analog path (600Ω:600Ω isolation transformer → I2S codec ADC → GPIO4/5/6) and digital path (buffered receive-only I2S → GPIO4/5/6). Audio-panel tap provides already-mixed crew audio, avoiding cockpit acoustic noise.
- Added §3.1a bench-test sub-section with callout box clearly labelling INMP441 wiring as bench-only; pin table uses AIN_BCLK/LRCLK/DIN macro names throughout.

**§3.2 Per-Device Wiring — audio output section (was "MAX98357A Class-D Amplifier")**
- Split into two sub-sections mirroring MASTER_SPEC D.3.3a + D.3.3b:
  - **§3.2 (installed, D.3.3a):** isolated line driver / DAC (PCM5102A-class) on I2S_NUM_1; AOUT_BCLK/LRCLK/DOUT (GPIO15/16/17); 600Ω:600Ω line-level isolation transformer on TX output line; crew hears checklist in-headset via COM3 channel; no onboard speaker in installed config.
  - **§3.2a (bench-only, D.3.3b):** callout box clearly marks MAX98357A as bench-test only. 650 mA peak figure retained in bench context only. Pin table uses AOUT_BCLK/LRCLK/DOUT macro names.
- *Judgment call:* 650 mA figure removed from the installed power budget (§5) and from any installed-context sentence. Retained only in §3.2a bench-test callout and §3.2 footnote noting it is not the installed figure.

**§3.3 microSD (two-card model)**
- Renamed to "microSD Cards … Two-Card Model".
- Describes slot 1 = Config Card (/sdcard-config), slot 2 = Data Card (/sdcard-data). Boot sequence: Config Card first → init audio + VOX → load matching Data Card aircraft folder.
- Pin table extended with card-detect rows (GPIO47 / GPIO38).
- Added third bullet: distribute Config Card write-protected in production; swap only the relevant card to reconfigure.

**§5 Power Budget**
- 3.3 V rail: updated "mic" to "audio-panel input stage (codec) + two microSD".
- 5 V rail: replaced "MAX98357A speaker output / ~650 mA peak" with installed output stage (few mA, line-level); bench-only 650 mA figure noted in italics as not the installed figure.
- Power bullet: updated headroom note to reflect removed MAX98357A as former dominant load.

**§6 BOM**
- Replaced "I2S MEMS mic (INMP441)", "I2S amp (MAX98357A)", "Speaker", "1× microSD breakout" with:
  - Audio input stage (isolation transformer + I2S codec ADC)
  - Audio output stage installed (PCM5102A-class DAC + isolation transformer → COM3 channel)
  - 2× microSD (Config Card + Data Card)
  - Bench-only rows clearly labelled *(bench only)*: MAX98357A, speaker, INMP441 mic

**§10 microSD Configuration**
- Section renamed to include "(Two-Card Model)".
- Layout block updated: slot 1 (/sdcard-config/config.json) = Config Card; slot 2 (/sdcard-data/) = Data Card. FAULT_NO_CONFIG / FAULT_NO_CARD references added.

**§12 Wiring Diagram caption**
- Updated to name the new architecture: isolated audio-panel input stage (I2S_NUM_0 / AIN_*), isolated audio output stage (I2S_NUM_1 / AOUT_*), two microSD (Config + Data Card). INMP441 + MAX98357A noted as bench-test items.

---

### build_enclosure.py

**§1 Architecture table (L172, L176) — Piece A and Piece B contents**
- Piece A: "speaker + grille" removed; bezel now has annunciator switch + PTT (optional) only.
- Piece B: replaced "INMP441 mic, MAX98357A amp, microSD" with: isolated audio-input stage (isolation transformer + I2S codec ADC / analog tap), isolated audio-output stage (line driver/DAC + output isolation transformer → COM3-style channel), two microSD breakouts (Config Card slot 1 + Data Card slot 2). INMP441 + MAX98357A explicitly labelled bench-test only.

**§1 Rationale paragraph (L185)**
- Replaced "keeps the microphone away from cooling-fan and avionics noise" with: "routes audio-panel signals (receive tap + COM3 output) cleanly from the avionics bay."

**§1 ASCII layout diagram (L190–195) — redraw**
- *Judgment call on ASCII redraw:* Panel (Piece A) box reduced to two annunciator-switch rows + PTT; "(.) speaker grille" row replaced with blank/removed. Avionics bay (Piece B) box extended to show: ESP32-S3, isolated audio-IN stage, isolated audio-OUT stage, Config Card + Data Card (both front-accessible), lamp-driver board, power conditioning. Box heights differ deliberately (Piece B is taller than Piece A). All lines use consistent monospace column alignment verified visually. The diagram text has consistent column widths (Piece A box: 24 chars wide; Piece B box: 30 chars wide + surrounding border).

**§2.1 Bezel height (L208)**
- Removed "speaker grille needs more room" as justification for 4-unit height. Replaced with: "switch + PTT fit comfortably; no speaker/grille cutout required"; 4-unit variant now covers additional connector cutouts.

**§2.2 Bezel front-face layout (L227–228)**
- Removed "Speaker grille (see §4) — open area ≥ 40% over the speaker cone; offset from the switch" bullet entirely.
- Added explicit "No speaker grille" bullet explaining installed config has no onboard speaker; audio delivered in-headset via COM3 channel; no acoustic aperture required.

**§3.1 Internal layout (L250, L255–258)**
- Updated board list: INMP441 + MAX98357A removed; replaced with isolated audio-output stage board (line driver/DAC + isolation transformer), audio-input stage board, two microSD breakouts.
- Removed mic-placement / acoustic-port rationale. Replaced with: installed input is audio-panel tap (not onboard mic); audio-panel tap takes already-mixed crew audio; no acoustic port needed; no onboard speaker or grille in the installed build.

**§3.2 Access & connectors (L263–274)**
- microSD access updated: two front-accessible slots labelled CONFIG CARD (SLOT 1) and DATA CARD (SLOT 2).
- Main connector: removed "speaker +/−" from the signal list (speaker removed).
- Added two new audio connector bullets:
  - AUDIO IN — PANEL TAP (ISOLATED): galvanically-isolated receive-only audio-panel input tap connector.
  - AUDIO OUT — COM3 ISOLATED: galvanically-isolated line-level TX to dedicated COM3-style audio-panel channel; separate connector from the input tap, mirroring MASTER_SPEC Part E.

**§4 Audio section — complete rewrite**
- Title changed from "Audio (Speaker) Details" to "Audio Interface — Isolated Panel Connectors".
- Removed all speaker, grille, and MAX98357A content.
- Replaced with: installed config has no onboard speaker/grille; two isolated panel connectors (AUDIO IN — PANEL TAP ISOLATED and AUDIO OUT — COM3 ISOLATED) with 600Ω impedance specs, shielding notes, and safety language (isolation transformer as primary barrier, conservative output level to avoid masking ATC audio).
- Explicit statement: "No acoustic grille needed; remove grille-pattern cutouts from CAD model."
- Uses U+2126 (OHM) throughout — no U+03A9 introduced. GLYPH NOTE constraint maintained.

**§8.1 Open items**
- Removed "Where the mic lives" and "Speaker model" open items (no longer relevant).
- Added: audio-panel connection type (analog vs. digital path → drives AUDIO IN stage BOM and connector pin-out); COM3 channel input impedance confirmation.

**§8 Deliverables**
- 2D drawings bullet: removed "grille pattern"; added "AUDIO IN / AUDIO OUT connector cutouts"; added "No speaker-grille pattern required."
- Mechanical BOM bullet: removed "speaker, grille mesh"; replaced with "AUDIO IN / AUDIO OUT panel feedthroughs, gaskets, conformal-coat."

**§9 Reference dimensions table**
- Removed "Speaker / 4–8Ω ≥ 2W" row.
- Added two rows: "Audio IN connector (600Ω line level isolated or buffered I2S)" and "Audio OUT connector COM3 (600Ω line-level output isolated via transformer)".

---

### Consistency verification results
- **Zero SPK_ macros** in both files (grep confirmed).
- **Zero MIC_ macros** in both files (grep confirmed).
- **AIN_BCLK_GPIO / AIN_LRCLK_GPIO / AIN_DIN_GPIO on GPIO 4/5/6** consistent in build_packet.py pin table and section prose.
- **AOUT_BCLK_GPIO / AOUT_LRCLK_GPIO / AOUT_DOUT_GPIO on GPIO 15/16/17** consistent in build_packet.py pin table, §3.2 prose, and §3.2a bench-test pin table.
- **No U+03A9** introduced in either file; all ohm signs use U+2126 per existing GLYPH NOTE.
- **Both files pass `ast.parse`** — verified clean.
- All remaining MAX98357A and INMP441 references are in bench-only context (callout boxes, *(bench only)* BOM rows, or explicit "not the installed" / "bench-test only" qualifiers).
- "DEMO/TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS" framing preserved in all callout boxes and cover pages; not weakened.
