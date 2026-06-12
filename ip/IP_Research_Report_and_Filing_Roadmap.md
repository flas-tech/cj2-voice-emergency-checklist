# IP Research Report & Filing Roadmap
## Voice-Driven Emergency Checklist Reader for Aircraft

**Prepared:** June 2026 · **Jurisdiction:** United States (USPTO) · **Applicant (to elect):** Flite Line Aviation Services, LLC *or* Michael Gravalec (individual)

> **Not legal advice.** This report is engineering/IP research to inform your strategy. Before filing anything, have a USPTO-registered patent attorney (for the patent) and a trademark attorney (for the mark) review and run formal clearance. The provisional draft is a starting point, not a filing-ready document a non-attorney should submit blind.

---

## 1. Executive Summary

You have a genuinely defensible invention. The voice-interactive checklist *concept* is old (Boeing, Honeywell, Collins, Garmin all hold or held patents), so a broad "voice checklist" claim is dead on arrival. But your **specific architecture** has real white space — three features in particular appear to be unclaimed by any live patent. The recommended path is a **US provisional patent** (cheap, fast, locks a priority date) plus a **trademark** on a coined name.

**Bottom-line recommendations:**
- **Patent:** File the provisional now to establish priority. Claim the **combination** of your novel features, not the generic voice-checklist idea. Draft is ready for attorney review.
- **Trademark:** Lead with **AviVox** (coined, clean across all classes). Avoid **VoxPilot** — it would almost certainly be refused.
- **Certification note unchanged:** the device's DO-160 / NORSEE-friendly, DO-178-avoiding posture is also your strongest *patent* story (it's what makes the architecture novel), so the two efforts reinforce each other.

---

## 2. The Invention (as defined for IP purposes)

A standalone, **offline** electronic device that audibly reads aircraft checklists and advances on recognized crew speech, with these distinguishing attributes:

| # | Feature | Role in claims |
|---|---------|----------------|
| 1 | Fully offline, deterministic, bounded-grammar speech recognition on an ESP32-S3-class MCU (no cloud, no network) | Supporting (moderate prior art) |
| 2 | **Galvanically-isolated receive-only INPUT tap of the aircraft audio panel** as the ASR source (cannot transmit/key/back-feed via this path); PLUS (revised) a **separate, galvanically-isolated dedicated OUTPUT channel** (COM3-style aux channel) for checklist read-aloud delivery to crew headsets — the two forming a **dual-isolated-channel architecture** (electrically separate, independent isolation barriers). The absolute "cannot inject into the panel" claim is narrowed to the INPUT tap only; the OUTPUT is an intentional, isolated, advisory audio injection into a dedicated aux channel. | **Lead novelty** (receive-only INPUT tap is established; dedicated isolated OUTPUT + dual-channel architecture is **new** and prior-art search not yet run for output feature — see Section 7) |
| 3 | VOX-primary hands-free operation with PTT retained as manual override | Supporting (moderate prior art) |
| 4 | **Dual-removable-card architecture** — Config card (installation authority) + Data card (content authority) with cross-card aircraft-ID consistency check | **Lead novelty** |
| 5 | **Fail-safe "revert-to-unopened" lockout** + dark-cockpit amber fault annunciation (never shows partial/stale/mismatched content) | **Lead novelty** |

DEMO/TRAINING ONLY positioning is maintained; the device is advisory, not a required system.

---

## 3. Patent Prior-Art Findings

26 references reviewed across 7 search angles (voice/speech emergency checklist, cockpit voice annunciator, audio-panel-tapped recognition, SD-card-configurable avionics, fail-safe checklist content, offline embedded ASR, VOX cockpit interaction). Full detail in `prior_art_findings.md`.

### Closest ACTIVE patents — these you must distinguish around

| Patent | Owner | What it covers | How you differ |
|--------|-------|----------------|----------------|
| [US7289890B2](https://patents.google.com/patent/US7289890B2/en) | Boeing | Voice checklist system integrated with avionics | You are standalone, not avionics-integrated; audio-panel tap, not system bus |
| [US9550578B2](https://patents.google.com/patent/US9550578B2/en) (expires ~2034) | Honeywell | Voice commands onboard aircraft | You use receive-only isolated tap + bounded offline grammar; no command authority over aircraft |
| [US11829589B2](https://patents.google.com/patent/US11829589B2/en) | Collins Aerospace | ECL command sequencer | You are not an ECL, not integrated, and add the dual-card + revert-to-unopened architecture |

### Closest EXPIRED patents — free to practice, but examiner may cite

| Patent | Owner | Note |
|--------|-------|------|
| [US20070288129A1 / US7912592B2](https://patents.google.com/patent/US20070288129A1/en) | Garmin | Basic speak-name → TTS → "Check"-advance loop. This is the generic loop you should NOT claim alone. |
| [US8793139B1](https://patents.google.com/patent/US8793139B1/en) | — | Related ASR-for-aircraft prior art |

### Closest commercial product
**Microkit Audio Checklist** (landingheight.com, ~$435, NORSEE-certified) — button-controlled, **no voice recognition**. Validates the NORSEE path and the market, but does not anticipate your voice/audio-panel/dual-card claims.

### White-space conclusion
- **No live patent** was found for a **receive-only galvanically-isolated audio-panel tap** used as the ASR input source (Feature 2, INPUT tap). This white-space finding stands.
- **No prior-art search has been run** for the **dedicated isolated audio-panel OUTPUT channel** (COM3-style advisory audio injection) component of Feature 2. **The output feature is outside the original search scope.** Freedom-to-operate and patentability for this specific feature must be assessed by the attorney with an additional search before relying on any white-space conclusion for the output path. See Section 7.
- **The dual-isolated-channel architecture** (isolated INPUT tap + isolated dedicated OUTPUT channel, electrically separate) is a candidate new novelty angle. No prior-art search has been conducted for this combination specifically.
- **None** found for the **dual-card Config/Data split with cross-card aircraft-ID consistency** (Feature 4). This white-space finding stands.
- **None** found specifically for the **revert-to-unopened complete fault lockout + dark-cockpit annunciation** (Feature 5). This white-space finding stands.
- Features 1 and 3 have moderate prior-art density → **claim them only as part of the combination**, never standalone.

**Patentability assessment:** Favorable for a *combination* claim built around Features 2 + 4 + 5. Low/unfavorable for any broad "voice-advances-checklist" claim. The new OUTPUT channel and dual-isolated-channel architecture may add independent novelty, but require an additional prior-art search. Strategy: claim narrow and specific; the architecture is where the novelty and non-obviousness live.

---

## 4. Trademark Findings

USPTO wordmark screening across the relevant classes — **IC 009** (devices / downloadable software) and **IC 042** (software services). Full detail in `trademark_findings.md`.

| Name | Risk | Verdict |
|------|------|---------|
| **AviVox** | Clear (0 conflicts, all classes) | **★ Lead recommendation** |
| **VoxCheck** | Clear | Strong backup |
| **CheckCall** | Clear | Strong backup |
| AeroVox | Moderate (live Class 9 — capacitors) | Consult attorney |
| AeroCheck | Moderate (live Class 7 — valves) | Consult attorney |
| Litany | Clear but weak (common word) | Viable, low distinctiveness |
| Wingman | Moderate-High (crowded Class 9) | Caution |
| **VoxPilot** | **High** | **✗ AVOID** |

**VoxPilot — avoid.** Identical wordmark, LIVE/REGISTERED in Class 9 for speech-recognition software (Reg. No. 4551726). Directly analogous goods → near-certain refusal and opposition risk.

**Recommendation:** Adopt **AviVox** (coined: aviation + voice; inherently distinctive; clean everywhere). Hold **VoxCheck** / **CheckCall** as backups. Before adoption, confirm common-law use and domain/social-handle availability (a quick web + domain-registrar check), then a registered TM attorney runs full clearance (state + common-law + design-mark).

---

## 5. Provisional Patent Application — Status

A complete US provisional draft is ready in `provisional_patent_application.md`:
- Title, field, background, summary
- Drawings list (FIG. 1–7)
- Detailed description of all embodiments (analog + digital audio-panel taps, both card slots, fail-safe logic, annunciation)
- 12 informal claim-style statements (provisionals don't require formal claims, but these frame the eventual nonprovisional)
- Abstract + internal prosecution notes

**Before filing, you'll need:** inventor declaration, the actual figures (you have the wiring diagram; FIG. 1–7 should be drafted to match), the USPTO cover sheet (form SB/16), and the fee.

---

## 6. Filing Roadmap & Costs

### Patent path (provisional → nonprovisional)
1. **Now — File the provisional.** Establishes priority date. USPTO micro/small-entity fee is modest (roughly low-hundreds of dollars; you likely qualify as a micro or small entity). Attorney review of the draft strongly recommended before filing.
2. **Within 12 months — Decide on the nonprovisional.** The provisional expires after 12 months and cannot be extended. To keep the priority date you must file a nonprovisional (with formal claims) or a PCT within that window. This is the expensive step (attorney drafting + USPTO fees).
3. **Use the 12 months wisely:** finalize the design, gather any test/market data, and decide whether the commercial case justifies the nonprovisional spend.

### Trademark path
1. Confirm AviVox common-law/domain availability (quick check).
2. Decide intent-to-use (1(b)) vs. in-use (1(a)) basis. File in **IC 009** (device + downloadable software) and consider **IC 042** if you'll offer it as a service.
3. TM attorney runs full clearance, then files. USPTO filing fee is per-class.

### Sequencing
File the **provisional first** (priority is time-sensitive and prior art accrues daily). Trademark can follow in parallel — it's lower-urgency but cheap to lock once the name is confirmed.

---

## 7. Honest Caveats

- I am **not a patent or trademark attorney.** This is research, not legal advice. Get the draft reviewed before filing.
- The prior-art search is thorough but **not exhaustive** — a professional patentability search (and especially a freedom-to-operate analysis if you plan to sell) goes deeper, including foreign and non-patent literature.
- The **broad "voice checklist" idea is not patentable** for you — it's well-trodden. Your protectable invention is the specific combination. Keep claims narrow and architecture-focused.
- Trademark screening covers USPTO federal marks only; **common-law and state marks** still need checking before you commit to a name and spend on branding.
- **Architecture change after original prior-art search (important — act before nonprovisional filing).** After the original prior-art search was conducted, the device architecture changed: the onboard speaker/amplifier was removed and replaced with a **dedicated, galvanically-isolated audio OUTPUT channel** (COM3-style aux channel) that injects checklist read-aloud audio into the aircraft audio panel. This output feature was **not in scope** for the original prior-art search. Before relying on the white-space conclusions for the Feature 2 output path, or before filing the nonprovisional, the attorney must refresh the search to cover: intercom/audio-panel audio injection; cockpit advisory audio injection into COM or aux channels; and any existing patents on injecting audio into aircraft audio panels via isolated output stages. The receive-tap (INPUT) white-space findings are unaffected and stand. The potential novelty of the dual-isolated-channel architecture (isolated INPUT tap + isolated dedicated advisory-audio OUTPUT, electrically separated) should also be evaluated in the refreshed search.

---

*Source files: `ip/prior_art_findings.md` (full prior-art report, 26 refs), `ip/trademark_findings.md` (8-name screen), `ip/provisional_patent_application.md` (provisional draft).*
