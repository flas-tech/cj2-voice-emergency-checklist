# PROVISIONAL APPLICATION FOR PATENT UNDER 37 C.F.R. § 1.53(c)

**DRAFT for inventor/attorney review — not yet filed. This is not legal advice.**

---

**Title of Invention:** Offline Voice-Driven Advisory Checklist Reader Using a Galvanically-Isolated Receive-Only Audio-Panel Tap and a Dedicated Galvanically-Isolated Audio-Panel Output Channel, with a Dual-Removable-Card Fail-Safe Configuration Architecture

**Inventor(s):** Michael Gravalec

**Applicant / Assignee (as elected):** Flite Line Aviation Services, LLC *(or Michael Gravalec, individual — to be finalized at filing)*

**Filing type:** U.S. Provisional Patent Application (35 U.S.C. § 111(b))

---

## Cross-Reference to Related Applications

None. This is the first filing for this subject matter and is intended to establish a priority date. A nonprovisional and/or PCT application claiming benefit of this provisional may be filed within twelve (12) months.

---

## Field of the Invention

The invention relates to flight-deck advisory and human-factors equipment, and more particularly to a standalone, offline electronic device that audibly reads aircraft checklist items and advances through them in response to recognized crew speech, wherein the crew speech is obtained from a passive, receive-only, galvanically-isolated INPUT tap of an aircraft audio panel, and wherein checklist read-aloud audio is delivered to the crew in-headset through a separate, dedicated, galvanically-isolated OUTPUT channel into the audio panel (a "COM3-style" auxiliary channel), and wherein all aircraft-specific behavior is supplied by removable media using a fail-safe dual-card configuration architecture. The audio-panel INPUT tap and the audio-panel OUTPUT channel are on separate galvanically-isolated paths; the apparatus includes no onboard speaker in the installed configuration.

---

## Background

Modern flight decks use both paper Quick Reference Handbooks (QRHs) and, in larger aircraft, integrated Electronic Checklist (ECL) systems. Integrated ECLs (e.g., systems embodied in Boeing, Honeywell, and Collins Aerospace avionics suites) are tightly coupled to the host aircraft's certified avionics and crew alerting systems. As a result they are expensive, aircraft-type-specific, require substantial software assurance (e.g., RTCA/DO-178C), and are impractical to add to the large installed base of general-aviation and light-business aircraft that still rely on paper checklists.

Voice-interactive checklist concepts are known in principle. Prior systems read checklist items aloud and advance on a spoken acknowledgment word, but they share one or more of the following limitations:

1. They depend on integration with the host avionics suite, on a dedicated onboard microphone, or on cloud / large-vocabulary speech-to-text services, making them connectivity-dependent, non-deterministic, costly to certify, or all three.
2. They use a dedicated microphone that re-captures cabin/cockpit acoustics — degraded by ambient noise, oxygen masks, and headset use — rather than the clean, already-mixed audio the crew actually hears.
3. They tie checklist content to firmware, so supporting a new aircraft type requires a software change and re-verification.
4. They lack a rigorous, testable fail-safe behavior that guarantees the crew is never shown partial, stale, or mismatched checklist content.

A device that (a) is electrically and functionally minimal, (b) attaches to the aircraft only through a one-way, isolated audio tap, (c) is fully offline and deterministic, and (d) is rendered aircraft-specific entirely by removable media would be far cheaper to build and substantially easier to qualify (e.g., suitable for a Non-Required Safety Enhancing Equipment, "NORSEE," approval path emphasizing environmental qualification rather than complex software assurance). No known device combines these attributes. The present invention addresses this need.

---

## Summary of the Invention

Disclosed is a standalone, offline electronic apparatus and corresponding method for advisory reading of aircraft checklists, comprising, in various aspects:

- **An audio-input stage that derives crew speech from a passive, receive-only tap of an aircraft audio panel.** The INPUT tap is galvanically isolated from the aircraft (for example, by a line-level isolation transformer in an analog embodiment, or by a buffered, receive-only digital feed in a digital embodiment) such that via this INPUT path the apparatus cannot transmit on, key, mute, inject into, or back-feed the audio panel, and a fault, short, open, or loss of power within the apparatus cannot load down or alter audio-panel function through this path. The tapped, already-mixed crew audio — rather than a dedicated onboard microphone — is the primary input to the speech recognizer.

- **A dedicated, galvanically-isolated audio OUTPUT stage that injects checklist read-aloud audio into a separate, dedicated aircraft audio-panel channel** (a "COM3-type" auxiliary audio channel). The OUTPUT stage (for example, an I2S DAC followed by a line-level isolation transformer on the TX output line) delivers checklist items to the crew in their headsets, replacing the apparatus's own onboard speaker. The OUTPUT channel is on a **separate, galvanically-isolated path and a separate connector** from the receive-only INPUT tap, such that a fault, short, open, power loss, or output-stage failure within the apparatus **cannot key, jam, load, or back-feed the audio panel's other channels or required COM radios**; the injected audio is advisory/informational only on one dedicated aux channel and does not constitute a keying, command, or control interface to the aircraft. This dual-isolated-channel architecture — a receive-only isolated INPUT tap and a separately isolated dedicated advisory-audio OUTPUT channel — may itself represent a novel combination.

- **An offline, deterministic, bounded-grammar speech subsystem** executing on an embedded microcontroller (e.g., a dual-core system-on-chip of the ESP32-S3 class) without any network, cloud, or wireless connectivity, comprising an acoustic front end with a voice-activity detector (VAD), a wake-word stage, and a fixed/bounded command-grammar recognizer. The bounded grammar is small (well under a few hundred commands) and is loaded from removable media, keeping recognition deterministic and within the capability of microcontroller-class hardware.

- **A voice-activated (VOX) interaction mode** in which the VAD gates recognition so the crew operates the device hands-free by speaking, with a push-to-talk (PTT) input retained as a manual force-listen override rather than as the primary trigger. The VOX behavior (sensitivity, hangover time, and whether PTT override is enabled) is configurable from removable media.

- **A read-aloud playback subsystem** that, upon recognizing a checklist-invocation phrase, plays a stored audio clip for each checklist item in sequence through the **dedicated, galvanically-isolated audio-panel OUTPUT channel** (the COM3-type auxiliary channel described above), so the crew hears checklist items in their headsets; advances to the next item upon recognizing a spoken completion/advance word. The apparatus's own onboard speaker is removed in the installed configuration (an onboard speaker output may optionally be retained as a bench-test-only output, clearly labeled as not for flight use).

- **A dual-removable-card configuration architecture** comprising two physically separate removable storage cards in two slots: a **configuration card** that defines the installation (an aircraft identifier, the selected audio-input source, VOX parameters, and fitted-hardware options) and is preferably write-protected/locked after installation to serve as a per-installation configuration-control record; and a **data card** that carries aircraft-specific checklist content (a checklist library, trigger and advance vocabulary, and read-aloud audio clips). The apparatus supports a new aircraft type by installing a new data card with no firmware change and no recompilation. Configuration authority (set by the installer) is thereby separated from content authority (authored from the aircraft flight manual), so a content revision cannot silently alter the installation's audio/VOX setup.

- **A fail-safe "revert-to-unopened" rule.** Before presenting any checklist, the apparatus validates both cards and requires that both are present, readable, schema-valid, internally complete (every referenced audio clip exists), and **mutually consistent** — specifically, that the aircraft identifier on the configuration card resolves to a matching content set on the data card. If any condition fails — a card is missing, unreadable, malformed, schema-invalid, references a missing audio clip, or the two cards disagree on the active aircraft — the apparatus **refuses to present any checklist** (its in-memory checklist store is held empty) and enters a clearly-annunciated fault state. The apparatus never presents partial, stale, or mismatched checklist content; the only failure mode exposed to the crew is loss of function, not misleading information.

- **A dark-cockpit fault annunciation** in which the apparatus displays nothing when selected-in and healthy, illuminates an amber fault legend on any fault, and, when deselected (selected-out), shows an "off" status while inhibiting the fault legend; a power-up lamp test verifies the annunciator before normal operation.

The combination of a receive-only isolated audio-panel INPUT tap as the speech-recognition source, a dedicated galvanically-isolated audio-panel OUTPUT channel for in-headset checklist delivery (the two channels being electrically separate with independent isolation barriers), an offline bounded-grammar VOX recognizer on microcontroller-class hardware, the dual-card configuration/content split with a cross-card consistency check, and the revert-to-unopened fail-safe with dark-cockpit annunciation provides an advisory checklist reader that is inexpensive, aircraft-agnostic, deterministic, and structured for a streamlined certification path. These aspects are individually and severally inventive and may be claimed alone or in combination. The dual-isolated-channel architecture (isolated receive-only INPUT tap + isolated dedicated advisory-audio OUTPUT channel, electrically separated) may itself be a novel combination.

---

## Brief Description of the Drawings

*(Figures to be supplied as informal drawings with the provisional; a system wiring diagram already exists in the project and may be adapted.)*

- **FIG. 1** — System block diagram: audio-panel receive tap → isolation stage → audio codec/ADC → microcontroller (AFE/VAD → wake word → bounded-grammar recognizer → playback sequencer) → isolated audio output stage → audio-panel COM3-style channel; plus the two card slots and the annunciator.
- **FIG. 2** — Analog audio-input embodiment: high-impedance line tap → isolation transformer → series/anti-alias network → codec line-in.
- **FIG. 3** — Digital audio-input embodiment: buffered, receive-only I²S/codec feed with clocks generated locally and no data driven toward any aircraft bus.
- **FIG. 4** — Dual-card architecture: configuration card (slot 1) and data card (slot 2), their respective schemas, and the cross-card aircraft-identity consistency check.
- **FIG. 5** — Boot/validation state machine implementing the revert-to-unopened rule, showing the healthy ("store OK") path and each fault status.
- **FIG. 6** — Dark-cockpit annunciator state table (selected-in healthy = dark; fault = amber; selected-out = white "off," fault inhibited) and the power-up lamp test.
- **FIG. 7** — Interaction flow: crew speaks checklist name → recognizer matches a trigger phrase → item clip plays → VAD/recognizer awaits an advance word → next item, with PTT as override.

---

## Detailed Description

### 1. Overall architecture

The apparatus is a self-contained advisory device that connects to an aircraft audio panel through two electrically separate, galvanically-isolated channels and otherwise draws power on its own protected rail. It comprises: an audio-input stage (receive-only isolated tap); a microcontroller running an offline speech-recognition and playback pipeline; an audio output stage (galvanically-isolated, line-level TX stage injecting advisory audio into a dedicated COM3-style audio-panel channel); two removable-card slots; and an annunciator with a select input and an optional push-to-talk input. The device is advisory and is not a required aircraft system; it does not interface with avionics, engine, or flight-control systems and takes no operational credit. The installed configuration has no onboard speaker; checklist audio reaches the crew via the audio-panel COM3-style output channel.

### 2. Audio-panel input stage (receive-only, galvanically isolated)

Crew speech is obtained from the aircraft audio panel rather than from an onboard microphone. The audio panel already presents the mixed audio the crew hears (intercom and received radio), at line/headphone levels typically on the order of 150–600 ohms and roughly 1–5 V RMS. Two interchangeable embodiments are disclosed and selectable per installation:

**(a) Analog embodiment.** A high-impedance tap is taken across a headphone/intercom/line output of the audio panel and passed through a 600-ohm-class audio isolation transformer (for example, an Allen Avionics AGL-series ground-loop isolation transformer), then through a series resistor (e.g., ~220–470 ohms) and a simple anti-alias network into the line-in of an audio codec/ADC (for example, an ES8388, ES7210, PCM1808, or CS5343). Because the tap is high-impedance and parallel, the panel sees a negligible load; because of the transformer, the device is galvanically isolated and cannot back-feed the panel.

**(b) Digital embodiment.** Where a codec sits closer to the source, a buffered, receive-only digital (e.g., I²S) feed enters the same codec/ADC. Bit clock, word-select, and master clock are generated by the device for the ADC only; no data line is driven back toward any aircraft bus.

In both embodiments the INPUT tap is strictly one-way (listen-only) on this path: via the INPUT stage alone, the device has no path to transmit, key a radio, mute, inject audio into, or otherwise alter the audio panel; and a short, open, power loss, or internal fault on the input side cannot load down, ground, or back-feed the panel on this path. This receive-only, isolated INPUT posture is a deliberate, testable safety property. The separate OUTPUT channel (Section 2a) injects advisory audio through its own isolated path and is described separately. An onboard MEMS microphone may optionally be provided **for bench testing only** and is expressly not the installed operational audio source.

### 2a. Audio-panel output stage (dedicated isolated COM3-style channel)

Checklist read-aloud audio is delivered to the crew in-headset via a dedicated, galvanically-isolated OUTPUT stage that injects audio into a separate, dedicated auxiliary audio-panel channel ("COM3-type" channel). In a representative embodiment, the microcontroller's I2S DAC output drives an I2S-to-analog DAC/line driver, followed by a line-level isolation transformer on the TX output line, followed by a line-level output to the audio panel's COM3-style input. The isolation transformer on the TX line provides galvanic isolation between the device and the panel's COM3 input, ensuring that a fault, short, open, power loss, or output-stage failure within the device **cannot key, jam, load, or back-feed the panel's other channels or required COM radios**.

The OUTPUT stage operates exclusively on the dedicated COM3-style auxiliary channel; it does not inject into, key, or otherwise affect the required COM1/COM2 channels or the crew intercom. The injected audio is advisory/informational only and does not constitute a keying, control, or command interface to the aircraft or its communications systems.

The INPUT tap (Section 2) and the OUTPUT stage (this section) are on **separate galvanically-isolated paths with separate connectors and independent isolation barriers**, so there is no conductive path between the two interfaces inside the apparatus. This "dual-isolated-channel" architecture is a deliberate design choice that permits the apparatus to listen to crew audio and speak back to the crew in-headset while maintaining electrical separation from the aircraft on both paths.

### 3. Offline bounded-grammar speech subsystem with VOX

The microcontroller (e.g., an ESP32-S3-class dual-core SoC with PSRAM) runs an entirely on-device speech pipeline (for example, the Espressif ESP-SR framework): an acoustic front end (AFE) providing noise suppression and a voice-activity detector (VAD); a wake-word stage; and a fixed/bounded-grammar command recognizer (for example, MultiNet) operating on a small, enumerated vocabulary loaded from the data card. There is no Wi-Fi, Bluetooth, cellular, or cloud dependency; recognition is deterministic and the wireless interfaces are disabled, which is both a security and an emissions-qualification advantage.

The grammar is intentionally small (well under the recognizer's command cap, e.g., on the order of a few tens of commands) and bounded — checklist trigger phrases plus universal advance words and item-specific advance words. Keeping the workload to fixed-grammar command recognition (not open-ended transcription) is what keeps a microcontroller-class part in scope and yields a small, well-understood failure surface.

In the default **VOX (voice-activated) mode**, the VAD gates recognition: the device listens whenever speech is detected on the tapped audio-panel feed, tuned by configurable VAD sensitivity and hangover time. The push-to-talk (PTT) input is retained only as a manual force-listen override; holding it opens recognition regardless of VAD, and a configuration setting may make PTT the sole trigger (disabling VOX) for installations that prefer the legacy behavior. Because the recognizer operates on the audio-panel feed, it hears precisely the audio the crew exchanges, improving robustness relative to a cabin microphone.

### 4. Read-aloud playback and interaction flow

Upon recognizing a checklist-invocation trigger phrase (e.g., a spoken emergency name), the device retrieves the corresponding checklist from the data card and reads its items aloud, one at a time, by playing a stored audio clip per item through the **dedicated, galvanically-isolated COM3-style audio-panel OUTPUT channel** (Section 2a), so the crew hears checklist items in their headsets. After reading an item, the device awaits a recognized completion/advance word (either a universal advance word such as "check," "checked," "complete," or "next," or an item-specific advance word) before advancing to the next item. The interaction is hands-free in VOX mode, with PTT available as override. There is no onboard speaker in the installed configuration; an onboard speaker output may optionally be provided as a bench-test-only feature.

### 5. Dual-removable-card configuration architecture

Two physically separate removable cards (e.g., microSD/FAT32) occupy two slots:

**Configuration card (slot 1).** Carries a single installation-configuration manifest defining: a schema version; an **aircraft identifier**; the **audio source** (analog or digital); audio parameters (input gain, codec part, sample rate); **VOX parameters** (mode, VAD sensitivity, hangover, PTT-override flag); fitted-hardware options; and installation provenance (shop, installer, date, work order). The configuration card is preferably write-protected/locked after installation so it serves as the per-tail configuration-control record and so configuration cannot drift in service.

**Data card (slot 2).** Carries aircraft-specific content: one folder per aircraft, each with a checklist manifest (aircraft identifier, title, universal advance words, and a checklist library of entries having stable identifiers, titles, trigger phrases, and ordered items) and a set of read-aloud audio clips, one per referenced item.

Because configuration (installation-controlled) and content (revision-controlled from the flight manual) are physically and logically separated, a content revision cannot silently change the installation's audio/VOX setup, and re-using a device on a different aircraft or wiring requires changing only the configuration card. Supporting a new aircraft type requires only authoring a new data card — **no firmware change and no recompilation.** A grammar validator enforces recognizer constraints on the data card (e.g., lowercase, single-spaced phrases; numbers spelled as words; command count under the recognizer cap; every referenced clip present), rejecting non-compliant cards.

### 6. Revert-to-unopened fail-safe and dark-cockpit annunciation

At boot, the device attempts a complete, valid load of **both** cards, reading the configuration card first (it names the aircraft and the audio source the input stage must initialize), then the matching data-card content. It returns exactly one status. The healthy status ("store OK") requires that both cards are mounted, both manifests parse and are schema-valid, every referenced audio clip is present, and the aircraft identifier is consistent across the two cards. Any of the following yields a fault and an **empty in-memory checklist store**, so no checklist can be presented even if requested: configuration card absent or unreadable; configuration manifest malformed or schema-invalid; data card absent or unmountable; data manifest missing, malformed, schema-invalid, or empty; a referenced audio clip absent; the cross-card aircraft identifier mismatched; or a memory-allocation failure during load. This is the literal "revert-to-unopened" rule: the device never presents partial, stale, or mismatched checklist content — the only crew-visible failure mode is loss of function.

Faults are annunciated using a dark-cockpit convention. When the device is selected-in and healthy, the annunciator shows nothing. On any fault, an amber fault legend illuminates. When the device is selected-out, a white "off" status shows and the fault legend is inhibited (a deliberately deselected device requires no crew action). A power-up lamp test illuminates the legend(s) briefly so a failed indicator cannot masquerade as a healthy/dark state. Recognition and fault monitoring are suspended while selected-out.

### 7. Representative hardware and power

A representative build uses an ESP32-S3-class module with PSRAM; an audio codec/ADC for the input path; an isolation transformer and input network for the analog input path; an I2S DAC / line driver followed by a second isolation transformer for the COM3 audio output path; two microSD slots; and a split-legend annunciator with low-side lamp drivers for the white "off" and amber "fault" legends. The device runs from a low-current supply (e.g., USB 5 V ≥ 1 A) on its own protected rail; neither the input tap nor the isolated output stage draws significant power from the aircraft; both are isolated from the device's grounds through their respective transformers.

### 8. Certification posture (advisory, non-required)

The device is advisory and non-required, fails to a clearly annunciated safe state, and connects to the aircraft through two galvanically-isolated channels: a receive-only INPUT tap and a dedicated isolated advisory-audio OUTPUT channel (COM3-style). This profile is intended to suit a NORSEE approval path emphasizing environmental qualification (e.g., RTCA/DO-160G) while avoiding complex software assurance (e.g., RTCA/DO-178C). The isolated audio OUTPUT into the COM3-style channel is the most significant interface-risk item: the isolation design must demonstrate that a device fault cannot key, jam, load, or back-feed the panel's required channels, and that the injected advisory audio cannot mask or be mistaken for required ATC/aircraft audio. These questions must be addressed in the isolation design and safety assessment. *(This posture is a design goal and roadmap; the prototype holds no approvals.)*

### 9. Alternatives and scope

The disclosure contemplates numerous alternatives, including: other microcontroller/SoC families and other speech frameworks; other isolation means (optical or capacitive isolation, transformer-coupled digital); other removable media (e.g., other flash card formats, or two partitions/namespaces on physically distinct media); cryptographic signing/checksums of either card; additional fault conditions and additional annunciator states; an optional visual display in lieu of or in addition to the dark-cockpit annunciator; and use in fixed-wing, rotorcraft, simulator, and training contexts. Features described together may be claimed separately. The invention is not limited to the specific parts, values, formats, or aircraft examples named herein, which are illustrative.

---

## Informal Claim-Style Statements (for drafting the later nonprovisional)

*A provisional does not require claims; these statements are included to anchor scope and aid the nonprovisional. They are not formal claims.*

1. An advisory aircraft checklist apparatus comprising: a receive-only, galvanically-isolated audio-input stage configured to derive crew speech from an INPUT tap of an aircraft audio panel, wherein the INPUT tap provides no capability to transmit on, key, mute, or back-feed the audio panel via that path; a dedicated, galvanically-isolated audio-output stage configured to inject checklist read-aloud audio into a separate, dedicated auxiliary channel of the audio panel (a "COM3-type" channel), the output stage including an isolation barrier such that a fault in the apparatus cannot key, jam, load, or back-feed the panel's other channels or required COM radios; wherein the INPUT stage and the OUTPUT stage are on separate galvanically-isolated paths with no shared conductive path therebetween; an offline microcontroller executing a bounded-grammar speech recognizer with a voice-activity detector; and a controller configured to play stored audio for each item of a checklist in sequence via the dedicated audio-output stage and to advance upon recognition of a spoken advance word.

2. The apparatus of statement 1, wherein the audio-input stage comprises an audio isolation transformer coupling a high-impedance analog tap of the audio panel to a codec, such that an internal fault or power loss cannot load down or back-feed the audio panel via the input path.

3. The apparatus of statement 1, wherein the audio-input stage comprises a buffered, receive-only digital feed to a codec, all clocks for which are generated locally with no data driven toward any aircraft bus, the analog and digital input paths being selectable per installation.

4. The apparatus of statement 1, wherein the speech recognizer operates in a voice-activated (VOX) mode gated by the voice-activity detector, with a push-to-talk input retained as a manual force-listen override.

5. The apparatus of statement 1, further comprising two physically separate removable-card slots receiving a configuration card defining an installation — including an aircraft identifier, a selected audio source, and voice-activation parameters — and a data card carrying aircraft-specific checklist content and read-aloud audio, whereby a new aircraft type is supported by a new data card without firmware change.

6. The apparatus of statement 5, wherein the configuration card is write-protected after installation and serves as a per-installation configuration-control record, separating installation authority from content authority.

7. The apparatus of statement 5, wherein the controller, before presenting any checklist, validates that both cards are present, readable, schema-valid, and that the aircraft identifier on the configuration card is consistent with the data card, and otherwise holds an empty checklist store and refuses to present any checklist.

8. The apparatus of statement 7, wherein refusal to present a checklist occurs upon any of: a missing or unreadable card; a malformed or schema-invalid manifest; a referenced audio clip being absent; or a cross-card aircraft-identifier mismatch — such that the apparatus never presents partial, stale, or mismatched checklist content.

9. The apparatus of statement 1, further comprising a dark-cockpit annunciator that shows nothing when selected-in and healthy, illuminates an amber fault legend on any fault, shows a white off-status and inhibits the fault legend when selected-out, and performs a power-up lamp test.

10. A method of advisory checklist reading comprising: tapping an aircraft audio panel through a receive-only, galvanically-isolated INPUT interface; recognizing, offline on a microcontroller using a bounded grammar gated by a voice-activity detector, a spoken checklist-invocation phrase in the tapped audio; playing an audio clip for each checklist item in sequence through a separate, dedicated, galvanically-isolated OUTPUT channel of the audio panel, such that crew hear checklist items in-headset; advancing upon recognizing a spoken advance word; and, prior to presenting any checklist, requiring a configuration card and a data card to be present, valid, and mutually consistent as to aircraft identity, and otherwise entering an annunciated fault state without presenting any checklist content.

11. The method of statement 10, wherein supporting an additional aircraft type comprises installing a data card carrying that aircraft's checklist content and audio without modifying device firmware.

12. The apparatus of statement 1, wherein the microcontroller has no network, wireless, or cloud connectivity and the speech recognition is deterministic and limited to a fixed enumerated vocabulary loaded from removable media.

13. The apparatus of statement 1, wherein the audio-input stage and the audio-output stage each comprise a galvanic isolation barrier (e.g., an audio isolation transformer) on their respective audio lines, the two barriers being independent such that the apparatus has no conductive path shared between the aircraft audio panel's input tap connection and the apparatus's COM3-type output connection — a dual-isolated-channel architecture enabling the apparatus to receive crew audio for recognition and to inject advisory audio in-headset while maintaining electrical separation on both paths.

14. The apparatus of statement 13, wherein the audio-output stage isolation barrier is a line-level isolation transformer interposed between an I2S DAC/line driver output of the apparatus and the audio panel's COM3-type channel input, such that a fault, short-circuit, power loss, or output-stage failure in the apparatus cannot assert a voltage, current, or keying signal on the audio panel's required COM or intercom channels.

---

## Abstract

An offline, standalone advisory device reads aircraft checklist items aloud and advances on recognized crew speech. The device connects to an aircraft audio panel through two electrically separate, galvanically-isolated channels: (1) a receive-only INPUT tap (isolation-transformer-coupled analog or buffered-receive-only digital feed, selectable per installation) used as the speech-recognition audio source, such that the device cannot back-feed the panel via the input path; and (2) a dedicated isolated OUTPUT stage that injects checklist read-aloud audio into a separate auxiliary audio-panel channel ("COM3-type"), so crew hear checklist items in-headset, with the isolation barrier ensuring a device fault cannot key, jam, or back-feed the panel's required channels. The two channels are on separate paths with independent isolation barriers. A microcontroller runs an entirely on-device, deterministic, bounded-grammar speech recognizer with a voice-activity detector enabling hands-free (VOX) operation, with push-to-talk retained as a manual override. The device is rendered aircraft-specific by two removable cards — a write-protected configuration card (installation parameters) and a data card (checklist content and audio) — and supports new aircraft types without firmware change. Before presenting any checklist, the device requires both cards to be present, valid, and consistent as to aircraft identity; otherwise it presents nothing and enters a dark-cockpit-annunciated fault state, never showing partial or stale content.

---

### Prosecution notes (internal — remove before filing)

- **Closest active art to distinguish:** US7289890B2 (Boeing Voice Checklist System) and US9550578B2 (Honeywell voice commands onboard aircraft). Neither claims the receive-only isolated audio-panel tap, the dedicated isolated output into an audio-panel aux channel, the dual-card config/content split with cross-card consistency, or the revert-to-unopened fail-safe.
- **Closest expired art (free to practice, but citable):** US7912592B2 (Garmin ASR for aircraft) covers the basic speak-name → TTS → "Check"-advance loop. Distinguish on offline/microcontroller, audio-panel tap, VOX-primary, dual-card, fail-safe, and dual-isolated-channel aspects.
- **Prior-art search scope re-scoping required (important).** The original provisional was built around the absolute claim that the device "cannot transmit/inject into/back-feed the audio panel." That absolute claim is now **re-scoped**: the INPUT tap remains receive-only and cannot back-feed, but the OUTPUT stage is a new, intentional audio injection into a dedicated aux channel. The prior-art search was conducted under the old scope and **did not search for prior art on injecting advisory audio into an audio panel / intercom audio injection** (e.g., audio injection for cockpit entertainment, audio panel aux-channel injection, COM3-style aux audio). The attorney **must conduct an additional prior-art search** covering intercom/audio-panel audio injection before relying on the white-space conclusions for the output feature. The receive-tap white space remains valid; the output injection white space is **unverified**.
- **Potential new novelty — dual-isolated-channel architecture.** The combination of a receive-only isolated INPUT tap AND a separately isolated dedicated advisory-audio OUTPUT channel (both galvanically isolated, electrically separate, on independent barriers) may itself be a novel combination not found in the prior art search. Claim statements 13 and 14 are directed to this architecture. Attorney should evaluate this as an independent claim anchor.
- **Strongest independent claims** likely lie in: (a) the dual-isolated-channel architecture (new claim 13/14); (b) the receive-only isolated INPUT tap as ASR source (Feature 2, carry forward); (c) dual-card cross-consistency (Feature 4); (d) revert-to-unopened (Feature 5). Treat Feature 1 (the loop) as background and claim it only in combination.
- **Architecture change note:** the prior design used an onboard speaker/amplifier ("not fed back to the panel"). That claim was the core novelty framing. The new design REMOVES the onboard speaker and instead USES a dedicated isolated output channel into the audio panel. This is a material change that (i) improves crew ergonomics (in-headset delivery), (ii) adds the output as a new potential novelty, and (iii) requires narrowing the absolute "cannot inject into the panel" language to apply only to the INPUT tap. Prior claim 1 (old) asserted the device had "no capability to inject into the panel" — that language now applies only to the INPUT tap path; the new OUTPUT stage is an intentional, isolated, advisory injection.
- Add formal figures before nonprovisional. Update FIG. 1 to show the dual-channel block diagram (audio-panel receive tap AND isolated COM3 output stage). The provisional can be filed with informal drawings.
