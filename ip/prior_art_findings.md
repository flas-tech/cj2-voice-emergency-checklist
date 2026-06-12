# Patent Prior-Art Search Findings
## Voice-Driven Advisory Emergency-Checklist Reader for Aircraft (ESP32-S3 Class, Offline, Single-Chip)
**Prepared for US Provisional Patent Filing**  
**Search Date:** June 2026  
**Scope:** Google Patents, USPTO, FreePatentsOnline, general web  

---

## Overview of the Invention Under Analysis

The invention is an offline, single-chip (ESP32-S3 class MCU) voice-driven advisory emergency-checklist reader for aircraft with five primary novel aspects:

1. **Fully offline, fixed-grammar voice-driven checklist:** Pilot speaks an emergency name → device reads each item aloud → waits for spoken completion word before advancing. No cloud, no Wi-Fi, deterministic bounded-grammar speech recognition (not large-vocabulary STT).
2. **Audio panel tap for speech input:** Crew audio is tapped from the aircraft audio panel (analog isolated line tap OR digital I2S), receive-only, galvanically isolated (isolation transformer). Speech recognition runs off this tap rather than the device's own microphone.
3. **VOX-gated recognition:** Voice-activity detector (VAD) enables hands-free operation; push-to-talk (PTT) retained as manual override only.
4. **Two-card aircraft-agnostic configuration:** Two separate removable microSD cards — a write-protected CONFIG card (installation: aircraft ID, audio source, VOX params, hardware options) and a DATA card (checklist library + read-aloud audio clips). No firmware change to support a new aircraft; a new data card suffices. The two-card split = installation-control vs. content-control separation.
5. **Revert-to-unopened safety rule:** If either card is missing, unreadable, malformed, schema-invalid, referenced audio clips are absent, or the two cards disagree on the active aircraft, the device REFUSES to present any checklist and enters a clearly-annunciated FAULT state (dark-cockpit: nothing shown when healthy; amber fault legend; OUT inhibits fault). Never partial or stale data.

---

## Search Angle (a): Voice/Speech Interactive Electronic Checklist Aviation

### Reference A-1: US7912592B2 / US20070288129A1 — Garmin International, Automatic Speech Recognition System and Method for Aircraft
- **Patent numbers:** US20070288129A1 (pub. 2007-12-13), US7912592B2 (granted)
- **Assignee:** Garmin International, Inc.
- **Filing date:** 2006-06-23; **Publication:** 2007-12-13; **Grant:** 2011-03-22
- **Status:** Expired (fee-related)
- **Source:** [Google Patents US20070288129A1](https://patents.google.com/patent/US20070288129A1/en)
- **Summary:** This is the most directly overlapping reference for Feature 1. The patent discloses an avionics ASR+TTS system (described as integrable into the Garmin G1000) that can automatically retrieve a checklist, read checklist items aloud via TTS, and advance to the next item when the pilot says "Check." The pilot can invoke checklists by saying "Emergency Checklist" or similar. A grammar definition stores known commands, and a voice command interpreter dynamically adjusts the grammar. Audio input is via cockpit microphones connected to the audio panel; the patent explicitly describes both push-to-talk (PTT) and push-to-control (PTC) triggering — not VOX. The system is deeply connected to the avionics suite (G1000), runs aircraft state-context filtering, and can automatically execute tasks (change frequencies, etc.). **Relation:** This patent covers the core loop of our Feature 1 (speak emergency name → TTS reads items → spoken "Check" advances). However, it requires avionics integration, uses PTT/PTC (not VOX-primary), is not described as offline in the portable/standalone sense, uses cockpit microphones (not an audio panel tap from outside the system), and does not describe a removable-card architecture. **The patent has expired**, so its core voice-checklist-loop is free to practice.

### Reference A-2: US8793139B1 — Voice Activated Cockpit Management System
- **Patent number:** US8793139B1
- **Assignee:** Individual (no large assignee)
- **Filing date:** 2013-11-06; **Grant:** 2014-07-29
- **Status:** Expired - Fee Related
- **Source:** [Google Patents US8793139B1](https://patents.google.com/patent/US8793139B1/en)
- **Summary:** A voice-activated cockpit management system using a "Next-Gen" voice recognition engine (modified Hidden-Markov-Model, cockpit-specific grammar, 98–100% claimed recognition rate). The pilot utters key words such as "ENGINE FIRE DURING FLIGHT" and the system audio-displays a multi-step emergency procedure step-by-step, with pilot interactive feedback at each step. Audio is output via Bluetooth to a headset. The system uses a Mini-PC with a local SD card, onboard processing, and a dedicated microphone. No cloud connection is described; it is arguably fully offline. **Relation:** Overlaps with Feature 1 (emergency name triggers step-by-step audio procedure with pilot feedback). Key differences: relies on its own dedicated microphone (not an audio-panel tap), uses Bluetooth audio (not direct speaker/intercom), no two-card safety architecture, no VOX/VAD, and is expired. The PTT/VOX topic is not specifically addressed. **Expired patent, free to practice.**

### Reference A-3: US20030025682A1 — Aural/Visual Checklist System for Avionics
- **Patent number:** US20030025682A1
- **Assignee:** Not stated in record; filed 2002-07-05
- **Status:** Abandoned
- **Source:** [Google Patents US20030025682A1](https://patents.google.com/patent/US20030025682A1/en)
- **Summary:** An avionics checklist system with both aural (pre-recorded audio files per checklist task) and visual display. Uses a stereo line-in amplifier to connect "in-line with the cockpit audio final mixed output or auxiliary audio input and output ports in the cockpit audio system" — this is a notable audio-panel-adjacent connection method. Also includes a microphone preamp for voice recognition input using commercially available speech recognition. **Relation:** The line-in connection is structurally closest to our Feature 2 (audio panel tap). However, the patent was **abandoned**, describes a two-way interface (also writes to cockpit audio output), and does not claim receive-only galvanic isolation. The voice recognition uses commercially available algorithms for navigation only, not for checklist advancement from a tapped signal. **No live claims; free to practice.**

### Reference A-4: US5454074A — Boeing Electronic Checklist System
- **Patent number:** US5454074A
- **Assignee:** Boeing Co.
- **Inventors:** Martin C. Hartel, Shu (Billy) C. Chou
- **Filing date:** 1994-05-17; **Grant:** 1995-09-26
- **Status:** **Expired - Lifetime** (priority date 1991-09-18)
- **Source:** [Google Patents US5454074A](https://patents.google.com/patent/US5454074A/en)
- **Summary:** The foundational Boeing ECL patent. A computer-based electronic checklist system interfaced with the crew alert system, providing normal and non-normal checklists, distinguishing open-loop (manual confirmation required) and closed-loop (auto-sensed from aircraft buses) items, status indicators, and operational notes. No voice/speech interaction described. **Relation:** Establishes electronic checklists with crew-acknowledgment gating — the structural predecessor to voiced checklist systems. No voice component. **Expired; fully free to practice.**

### Reference A-5: US5522026A — Boeing System for Creating a Single Electronic Checklist in Response to Multiple Faults
- **Patent number:** US5522026A
- **Assignee:** Boeing Co.
- **Filing date:** 1994-03-18; **Grant:** 1996-05-28
- **Status:** **Expired - Lifetime**
- **Source:** [Google Patents US5522026A](https://patents.google.com/patent/US5522026A/en)
- **Summary:** Covers the synthesis of a single prioritized checklist from multiple simultaneous fault triggers, preventing checklist duplication when faults share action items. No voice/speech component. **Relation:** Relevant to emergency checklist selection logic; no overlap with voice or audio-panel-tap features. **Expired.**

### Reference A-6: US7289890B2 — Boeing/Honeywell Voice Checklist System (Checklist System)
- **Patent number:** US7289890B2
- **Filing date:** 2004-11-24; **Grant:** 2007-10-30
- **Status:** Active (per Google Patents, "Active, expires")
- **Source:** [Google Patents US7289890B2](https://patents.google.com/patent/US7289890B2/en)
- **Summary:** An electronic Voice Checklist System (VCS) that can be activated manually or automatically by aircraft fault conditions. The VCS uses a synthetic or pre-recorded voice to audibly broadcast checklist items one at a time, with the pilot using an interface device (which may include voice recognition) to advance items. The VCS connects to flight deck speakers and the flight deck interphone system for audio output. The pilot-VCS interface may include voice recognition via a dedicated microphone. Checklist priority logic is described. An audio override command can interrupt pilot radio transmissions. **Relation:** This is a significant active reference that overlaps Feature 1 (audio checklist with voiced items and pilot voice acknowledgment). Key differences: it connects to the interphone *output* (not a passive tap of the panel receive bus), appears to require integration as an avionics function (not a standalone offline device), and does not describe receive-only isolation, VOX, dual removable cards, or the revert-to-fault safety rule. **ACTIVE; must be distinguished.**

### Reference A-7: US9550578B2 — Honeywell, Systems and Methods for Utilizing Voice Commands Onboard an Aircraft
- **Patent number:** US9550578B2
- **Assignee:** Honeywell International Inc.
- **Inventors:** Sue McCullough, Mahesh Sivaratri
- **Filing date:** 2014-02-04; **Grant:** 2017-01-24
- **Status:** Active, expires 2034-06-18
- **Source:** [Google Patents US9550578B2](https://patents.google.com/patent/US9550578B2/en)
- **Summary:** A system for using voice commands onboard an aircraft to program the flight management system. Audio input is via a cockpit microphone with push-to-talk activation. Speech recognition uses a filtered/constrained vocabulary (limited set of voice commands per flight phase), context-validated against FMS state, waypoints, and allowed operations. Not specifically about emergency checklists; focuses on FMS programming. **Relation:** Overlaps with voice-command grammar-based recognition in aviation (Feature 1 analogue). Key differences: not about checklist read-aloud and pilot acknowledgment, tightly coupled to FMS, uses its own microphone not a panel tap, uses PTT not VOX, and does not describe removable card architecture or fail-safe configuration rules. **ACTIVE; broad grammar-filtering speech recognition claims should be studied.**

### Reference A-8: WO2002035303A3 / ATE334434T1 — Aircraft Electronic Checklist System (Rockwell Collins area)
- **Patent numbers:** WO2002035303A3, EP family ATE334434T1
- **Priority date:** 2001-10-23
- **Status:** EP family expired; WO publication
- **Source:** [Google Patents WO2002035303A3](https://patents.google.com/patent/WO2002035303A3/en)
- **Summary:** An aircraft electronic checklist system covering crew alerting, checklist prioritization, and integration with avionics. References within this family cite voice checklist systems (the Boeing VCS). **Relation:** General ECL system; no novel voice interaction disclosed beyond the field.

### Reference A-9: US11829589B2 — Rockwell Collins, Electronic Checklist Command Sequencer
- **Patent number:** US11829589B2
- **Assignee:** Rockwell Collins, Inc.
- **Filing date:** 2022-04-22; **Grant:** 2023-11-28
- **Status:** Active
- **Source:** [Google Patents US11829589B2](https://patents.google.com/patent/US11829589B2/en)
- **Summary:** An electronic checklist system with a Command Control Sequencer (CCS) module that sequences automatable actions (e.g., actuating landing gear, sensing system states) based on checklist task items. The pilot provides initiation and confirmation inputs. The system transmits communications to aircraft actuators and displays completion status graphics and failure status graphics. Focus is on automated execution of physical actions, not voice interaction. **Relation:** Relevant to checklist sequencing and fail-state graphics (Feature 5 analogue for failure annunciation). Does not claim voice recognition, audio-panel tapping, VOX, removable-card architecture, or revert-to-fault safety. **ACTIVE; narrow claims around automated action sequencing.**

### Reference A-10: US20240339039A1 — AI Co-Pilot for Manned and Unmanned Aircraft
- **Patent number:** US20240339039A1
- **Filing date:** 2024-10-10
- **Status:** Pending
- **Source:** [Google Patents US20240339039A1](https://patents.google.com/patent/US20240339039A1/en)
- **Summary:** An AI co-pilot integrating NLP, voice recognition (via aviation-trained ChatGPT-4 model), and TTS in the cockpit. Specifically cloud-dependent/AI-dependent. Covers "checklist database" interaction via voice. **Relation:** Directly at odds with Feature 1 (fully offline, deterministic). Relies on large-vocabulary LLM; our invention is explicitly fixed-grammar, no LLM, offline. Well-distinguished.

---

## Search Angle (b): Cockpit Voice Annunciator and Aural Alerting Systems

### Reference B-1: GB2050979A — Texas Instruments, Automatic Voice Checklist System for Aircraft Cockpit
- **Patent number:** GB2050979A
- **Priority date:** 1979-05-29; **Publication:** 1981-01-14
- **Assignee:** Texas Instruments Inc.
- **Status:** **Expired** (well over 20 years)
- **Source:** Cited as prior art in [GB0523814D0 (Boeing, 2005)](https://patents.google.com/patent/GB0523814D0/en)
- **Summary:** This is arguably the earliest known patent on an automatic voice checklist system for aircraft cockpits. Texas Instruments filed this in 1979. While we could not fetch the full text from Google Patents directly, its title and citation in the Boeing checklist family confirm it covers automatically reading checklist items aloud in the cockpit. **Relation:** Foundational prior art for the aural checklist concept. Fully expired. The core concept of audio checklist broadcast is in the prior art. **Expired; free to practice.**

### Reference B-2: GB1356075A — System for Conducting Aircraft Checklists
- **Patent number:** GB1356075A
- **Priority date:** 1972-11-24; **Publication:** 1974-06-12
- **Assignee:** C.B. Dickinson
- **Status:** **Expired** (>50 years old)
- **Source:** Cited in [GB0523814D0 (Boeing, 2005)](https://patents.google.com/patent/GB0523814D0/en)
- **Summary:** The earliest known patent covering a system for conducting aircraft checklists (1972). No voice output described at this level of technology but the checklist conducting framework predates all modern systems. **Expired; fully free to practice.**

### Reference B-3: US6583733B2 — Honeywell, Helicopter Ground Proximity Warning System
- **Patent number:** US6583733B2
- **Assignee:** Honeywell International Inc.
- **Filing date:** 2001-05-25
- **Status:** **Expired - Lifetime**
- **Source:** [Google Patents US6583733B2](https://patents.google.com/patent/US6583733B2/en)
- **Summary:** A helicopter GPWS/EGPWS with voice warnings ("Caution Terrain, Caution Terrain," "Warning Terrain," altitude callouts). Demonstrates the well-established art of pre-recorded aural alert playback via aircraft speakers triggered by system conditions. **Relation:** Aural warning output via speaker is generic prior art. The invention's TTS/audio playback feature is in this space. Does not address voice recognition, checklist interaction, or removable media. **Expired.**

### Reference B-4: US6175314B1 — Voice Annunciation of Data Link ATC Messages
- **Patent number:** US6175314B1
- **Filing date:** 1999-02-25
- **Status:** Expired (priority date 1999; >20 years)
- **Source:** [Google Patents US6175314B1](https://patents.google.com/patent/US6175314B1/en)
- **Summary:** Voice annunciation of datalink ATC messages (CPDLC) to reduce pilot workload. Pre-recorded or synthesized voice reads incoming text messages. **Relation:** Audio advisory output to pilot. No checklist or voice recognition component. **Expired.**

### Reference B-5: US9710145B2 — Human Machine Interface Device for Aircraft
- **Patent number:** US9710145B2
- **Filing date:** 2015-08-31
- **Status:** Active, expires
- **Source:** [Google Patents US9710145B2](https://patents.google.com/patent/US9710145B2/en)
- **Summary:** An aircraft HMI device with touchscreen, voice recognition (activated by a dedicated button similar to PTT), and aural annunciations. Voice commands are input via a microphone in the headset or display unit. Aural annunciations (voice messages or warning chimes) are triggered by aircraft events. PTT button is used to activate voice recognition. **Relation:** PTT-activated voice recognition in cockpit. Does not cover VOX, audio-panel tap, removable-card configuration, or fail-safe rules. **ACTIVE; but broad claims are for touchscreen HMI, not checklist reading. Low overlap.**

---

## Search Angle (c): Speech Recognition Tapping Aircraft Audio Panel / Intercom / Radio Audio Bus

This is the most novel hardware angle of the invention. The search was specifically designed to find any patent that describes doing speech recognition from a *tap of the aircraft audio panel or intercom bus* rather than from a dedicated microphone.

**Finding: No direct hit was found** for "speech recognition performed by a device that passively taps the aircraft audio panel receive bus with galvanic isolation." The closest references are discussed below.

### Reference C-1: US20030025682A1 — Aural/Visual Checklist System (see also A-3)
- **Source:** [Google Patents US20030025682A1](https://patents.google.com/patent/US20030025682A1/en)
- **Relevance to Feature 2:** This abandoned application describes connecting a checklist device "in-line with the cockpit audio final mixed output or auxiliary audio input and output ports in the cockpit audio system" via a stereo line-in amplifier. This is the closest prior-art approach to a passive audio-panel connection for receiving cockpit audio. However: (1) the patent is **abandoned** and has no live claims; (2) the described connection is bidirectional (the device also outputs to the cockpit audio system); (3) no galvanic isolation / receive-only constraint is mentioned; and (4) the voice recognition microphone is a separate dedicated microphone preamp, not the line-in path. The line-in appears to be for environmental awareness, not as the primary voice-recognition audio source.

### Reference C-2: US9230549B1 — Multi-Modal Communications (MMC)
- **Patent number:** US9230549B1
- **Filing date:** 2011-05-18
- **Status:** Active
- **Source:** [Google Patents US9230549B1](https://patents.google.com/patent/US9230549B1/en)
- **Summary:** A multi-modal communications system for military/aviation contexts integrating voice and text-chat; includes ASR engine that captures radio channel audio. The system spatializes multiple radio channel audio streams and can transcribe voice transmissions. **Relation:** Captures radio channel audio for ASR, which is structurally related to tapping the audio panel receive bus. However, this system *is* the radio/intercom system (not a passive external tap), is not designed for emergency checklists, and does not address the galvanic-isolation/receive-only constraint. Medium indirect overlap.

### Reference C-3: US20230215278A1 — Systems and Methods for Adding Relevant Data to ATC Transcription Messages (Honeywell area)
- **Patent number:** US20230215278A1
- **Filing date:** 2022-03-17
- **Status:** Pending
- **Source:** [Google Patents US20230215278A1](https://patents.google.com/patent/US20230215278A1/en)
- **Summary:** Converts ATC voice radio communications to text messages by transcribing the receive path of the cockpit communications system (receiver → headset/speaker path). The system listens to the radio receive audio stream and applies ASR. **Relation:** Demonstrates the concept of tapping the radio receive audio path for ASR in aviation. However, this is a full avionics system (not a passive external tap device), is cloud/network dependent for transcription in its preferred embodiment, and is not used for checklist operations. **ACTIVE pending; represents a different application of the same underlying audio-path concept.**

### Reference C-4: US11289094B2 — System and Method for Assisting Pilot Through Clearance Playback
- **Patent number:** US11289094B2
- **Filing date:** 2020-05-20; **Grant:** 2022-03-29
- **Status:** Active
- **Source:** [Google Patents US11289094B2](https://patents.google.com/patent/US11289094B2/en)
- **Summary:** Records and plays back ATC radio clearances via the aircraft avionics radio receive path, using STT to transcribe them. The system processes inbound radio audio. **Relation:** Another avionics-integrated system that processes the radio receive path with ASR. Not about checklists or passive external hardware. Demonstrates industry recognition of the receive-audio-path as an ASR source.

### Summary for Angle (c):
The receive-only, galvanically-isolated audio-panel-tap as the exclusive/primary speech recognition input source for an emergency checklist device appears to be a genuine white space. Prior art processes the cockpit audio system's receive path (ATC transcription, radio monitoring) but always as an integrated avionics subsystem, not as a passive external tap hardware design. The specific architecture of: external hardware device → passive audio panel tap → galvanic isolation transformer → onboard microcontroller ASR → voice-driven checklist workflow was not found in any live patent.

---

## Search Angle (d): VOX Command Recognition in Cockpit; Push-to-Talk Speech Systems Aviation

### Reference D-1: US5774557A — Autotracking Microphone Squelch for Aircraft Intercom Systems
- **Patent number:** US5774557A
- **Assignee:** Northern Airborne Technology Ltd (assigned from individual inventor Robert Winston Slater)
- **Filing date:** 1995-07-24; **Grant:** 1998-06-30
- **Status:** **Expired - Fee Related**
- **Source:** [Google Patents US5774557A](https://patents.google.com/patent/US5774557A/en)
- **Summary:** A VOX (voice-operated transmission) squelch system for aircraft intercom that uses voice activity detection to automatically open/close the audio path without a PTT switch. The system tracks microphone noise floor to set the squelch threshold, enabling hands-free operation. **Relation:** Direct prior art for the VOX/VAD concept in cockpit audio (Feature 3). However: this patent covers the *intercom* VOX for communication gating, not for speech recognition triggering on a checklist device. The VAD is used to gate audio routing, not to trigger an ASR engine. The patent is **expired**. The general concept of aircraft VOX/VAD is in the prior art.

### Reference D-2: US20070288129A1 — Garmin ASR System (see also A-1)
- **Source:** [Google Patents US20070288129A1](https://patents.google.com/patent/US20070288129A1/en)
- **Relevance to Feature 3:** This patent describes PTT/PTC activation for ASR; VOX is not claimed. PTT as override retained in our invention is essentially described herein.

### Reference D-3: US9710145B2 — HMI Device for Aircraft (see also B-5)
- **Source:** [Google Patents US9710145B2](https://patents.google.com/patent/US9710145B2/en)
- **Relevance to Feature 3:** PTT used to activate voice recognition. VOX-primary not described.

### Reference D-4: US9550578B2 — Honeywell Voice Commands (see also A-7)
- **Source:** [Google Patents US9550578B2](https://patents.google.com/patent/US9550578B2/en)
- **Relevance:** Claims include an "activation element such as a button or switch" (i.e., PTT) on the audio input device. VOX/VAD operation is not explicitly claimed, though the patent's language for an "audio input device" may be broad enough to cover hands-free approaches if activation is not specifically claimed.

### Summary for Angle (d):
VOX/VAD as an intercom-audio gating mechanism is established prior art (US5774557A, expired). Using PTT to trigger ASR in the cockpit is well-established art (Garmin US7912592B2, Honeywell US9550578B2). However, the **specific combination** of (a) VAD-gated ASR operating on a passively-tapped audio-panel signal, (b) with PTT retained only as manual override, (c) for emergency checklist advancement purposes appears to be in white space. No live patent claims this exact combination.

---

## Search Angle (e): Removable Card / SD Card / Memory Card Configurable Avionics or Checklist Devices

### Reference E-1: US9284045B1 — Garmin, Connected Cockpit System and Method
- **Patent number:** US9284045B1
- **Assignee:** Garmin (context)
- **Filing date:** 2014-03-28
- **Status:** Active
- **Source:** [Google Patents US9284045B1](https://patents.google.com/patent/US9284045B1/en)
- **Summary:** An avionics unit (e.g., Garmin GTN 650/750 type) with an SD card reader slot that receives a wireless-transceiver-equipped memory card. The card communicates avionics data wirelessly between the certified avionics unit and a mobile device. The memory may include SD card, micro-SD, MMC, USB flash drive for storing avionics applications, flight plans, weather data, etc. **Relation:** Demonstrates removable memory card use in certified avionics for configuration and data delivery. However, this is about wireless data bridging (the memory card contains a Wi-Fi/Bluetooth transceiver), not about a write-protected configuration card vs. a separate data card architecture with a safety lockout. **ACTIVE; narrow claims focused on wireless memory card transceiver.**

### Reference E-2: US20050026609A1 — Methods and Apparatus for Wireless Upload and Download of Aircraft Data
- **Patent number:** US20050026609A1
- **Filing date:** 2004-06-30
- **Status:** Abandoned
- **Source:** [Google Patents US20050026609A1](https://patents.google.com/patent/US20050026609A1/en)
- **Summary:** Wireless transfer of aircraft data (databases, software) to avionics units via portable memory devices. SD cards and PCMCIA cards are described as data transport media. **Relation:** General removable card for avionics data upload. No dual-card safety architecture, no write-protect enforcement, no revert-to-fault. **Abandoned.**

### Reference E-3: US5270931A — Software Controlled Aircraft Component Configuration System
- **Patent number:** US5270931A
- **Filing date:** (original priority, granted 1993)
- **Status:** **Expired** (>20 years)
- **Source:** [Google Patents US5270931A](https://patents.google.com/patent/US5270931A/en)
- **Summary:** A software-controlled system for configuring aircraft components by loading configuration data from a removable medium. Covers the idea of a software-driven, removable-medium-configured avionics system. **Relation:** Generic prior art for removable-medium configuration of avionics. Does not address dual-card architecture, write protection, or fail-safe lockout. **Expired.**

### Reference E-4: US7103456B2 / US20050228559A1 — PCMCIA Card for Aircraft Condition Monitoring Systems
- **Patent number:** US7103456B2
- **Filing date:** 2004-04-12
- **Status:** Expired - Lifetime
- **Source:** [Google Patents US7103456B2](https://patents.google.com/patent/US7103456B2/en)
- **Summary:** A PCMCIA card interface that communicates with aircraft condition monitoring systems to access flight performance data. The card bridges the ACMS to external devices. **Relation:** Removable card as interface to aircraft systems; no checklist function, no dual-card safety architecture. **Expired.**

### Summary for Angle (e):
Removable memory cards (SD, PCMCIA, flash) as data and configuration delivery mechanisms for avionics devices are well-established prior art. However, the **specific two-card split** — (a) a physically separate write-protected CONFIG card defining installation parameters versus (b) a DATA card containing checklist content and audio, with (c) the device refusing to operate if either card is missing or if they disagree on aircraft identity — does not appear in any found patent. This architectural pattern is distinct from generic "update database via SD card."

---

## Search Angle (f): Fail-Safe Revert-to-Safe-State / Lock-Out on Invalid Configuration Data in Avionics

### Reference F-1: US5493497A — Multiaxis Redundant Fly-By-Wire Primary Flight Control System
- **Patent number:** US5493497A
- **Filing date:** 1996-02-20
- **Status:** Expired
- **Source:** [Google Patents US5493497A](https://patents.google.com/patent/US5493497A/en)
- **Summary:** A fly-by-wire system with redundant channels and fail-safe logic that reconfigures upon channel failure. Demonstrates the general principle of fail-safe state reversion in avionics. **Relation:** General fail-safe avionics architecture; not specific to configuration data validation. **Expired.**

### Reference F-2: US5161158A — Failure Analysis System
- **Patent number:** US5161158A
- **Status:** Expired
- **Source:** [Google Patents US5161158A](https://patents.google.com/patent/US5161158A/en)
- **Summary:** An avionics failure analysis system detecting and responding to system faults. General fault detection prior art. **Relation:** Generic; no connection to removable media validation or checklist lockout. **Expired.**

### Reference F-3: EP0987562A1 — Integrated Hazard Avoidance System
- **Patent number:** EP0987562A1
- **Filing date:** 1997-04-23
- **Status:** **Expired - Lifetime**
- **Source:** [Google Patents EP0987562A1](https://patents.google.com/patent/EP0987562A1/en)
- **Summary:** A fault-tolerant data bus architecture for integrated hazard alert prioritization. Demonstrates fault-tolerant, fail-safe concepts in avionics alerting. **Relation:** Fail-safe architecture in avionics; no specific checklist or removable-media validation. **Expired.**

### Reference F-4: US9583008B2 — Managing Data Exchange Between Avionic Core and Open World Device
- **Patent number:** US9583008B2
- **Filing date:** 2016-06-09
- **Status:** Active
- **Source:** [Google Patents US9583008B2](https://patents.google.com/patent/US9583008B2/en)
- **Summary:** Manages data exchange between a safety-critical avionics core and an "open world" (non-certified) device. Includes validation and sandboxing to prevent invalid or untrusted data from affecting safety-critical functions. **Relation:** Closest prior art to Feature 5's concept of rejecting invalid configuration data to protect safety-critical function. However, this is about inter-system data trust boundaries (avionics core vs. EFB), not about refusing to present stale or mismatched checklist data from removable media. **ACTIVE.**

### Summary for Angle (f):
The general concept of fail-safe states upon fault detection is thoroughly covered in aviation prior art. The specific concept of "refuse to present any checklist and enter a clearly annunciated FAULT state if removable media is missing, malformed, schema-invalid, audio clips absent, or the two cards disagree on aircraft identity" (the 'revert-to-unopened' rule) was not found in any live patent. The combination of (a) multi-condition validation triggers (missing card, schema validation failure, audio clip check, cross-card aircraft ID agreement) with (b) complete refusal to show any partial data and (c) a specific dark-cockpit annunciation pattern is a novel safety architecture.

---

## Search Angle (g): Major Incumbents — Honeywell, Garmin, Collins/Rockwell Collins, Thales, Gulfstream, Boeing, Astronautics

### Honeywell International
Key patents found: US9550578B2 (voice commands, active to 2034), US6583733B2 (GPWS aural alerts, expired), US20070288128A1 / US7912592B2 (ASR for aircraft, Garmin-filed but Honeywell cited extensively). Honeywell holds the [US7912592B2](https://patents.google.com/patent/US20070288129A1/en) patent (Garmin, now expired). Honeywell's active ECL products (Pro Line Fusion, etc.) appear to operate as integrated avionics rather than standalone units.

### Garmin International
Key patents: US7912592B2 / US20070288129A1 (Automatic Speech Recognition System and Method for Aircraft — the most directly relevant reference for Feature 1, **expired**). Garmin's G1000/G3000 avionics include voice-interaction features but all patent references found are either expired or describe integrated avionics suites.

### Rockwell Collins / Collins Aerospace
Key patents: [US11829589B2](https://patents.google.com/patent/US11829589B2/en) (Electronic Checklist Command Sequencer, active, filed 2022). The Boeing VCS (US7289890B2) is cited in the Rockwell Collins product ecosystem. Collins' ECL products are embedded in aircraft avionics platforms (e.g., Pro Line 21, Fusion).

### Boeing
Key patents: US5454074A (ECL system, **expired 2012**), US5522026A (single ECL from multiple faults, **expired**), US7289890B2 (Voice Checklist System, **active** though exact expiry unclear). Boeing's ECL technology is aircraft-integrated; their standalone portable standalone checklist device is not evident in patent searches.

### Thales
Thales SA has patents including FR2940482B1 and FR2954847B1 (cockpit task management systems, French applications). [GB0523814D0](https://patents.google.com/patent/GB0523814D0/en) cites these. Thales ECL products are integrated avionics (Airbus A380-class). No Thales patent directly addresses portable standalone voice-driven emergency checklists.

### Astronautics Corporation of America
Astronautics is cited in prior art ([US20100262318A1](https://patents.google.com/patent/US20100262318A1)) for offering an EFB with dual processors. No specific voice-checklist patent from Astronautics was found in this search.

### Gulfstream
No distinct Gulfstream-assigned voice-checklist patent was found; Gulfstream aircraft use integrated Honeywell/Collins avionics with ECL functions.

### Non-Patent Commercial Products Found

**Microkit Audio Checklist (Landing Height / Microkit Solutions):**
- Product: $435 USD, FAA NORSEE certified for minor alteration
- Features: Digital device playing pre-stored MP3 audio checklist files through aircraft intercom/audio panel. Up to 9 normal + 6 emergency checklists. Remote control or panel push-buttons to select and step through items. Accepts user-uploaded MP3s via built-in Wi-Fi. Step-by-step operation with configurable pause. **No voice recognition; no VOX; no two-card architecture.**
- Source: [landingheight.com](https://landingheight.com/product/audio-checklist/)
- **Relation:** Closest commercial product to our invention's audio-output function, but is entirely push-button controlled (no voice recognition whatsoever). Connects to audio panel for output. Does not recognize pilot speech. This product confirms market demand for audio checklist devices but demonstrates zero overlap with the voice-recognition features of the invention.

---

## Consolidated Reference Table

| Ref | Patent No. | Title (Short) | Assignee | Filing Date | Status | Key Overlap |
|-----|-----------|---------------|----------|-------------|--------|-------------|
| A-1 | US7912592B2 / US20070288129A1 | ASR System for Aircraft | Garmin International | 2006-06-23 | **Expired** | Feature 1 (voice name → TTS checklist → "Check" advances) |
| A-2 | US8793139B1 | Voice Activated Cockpit Mgmt System | Individual | 2013-11-06 | **Expired** | Feature 1 (voice name → audio procedure steps) |
| A-3 | US20030025682A1 | Aural/Visual Checklist System | Unknown | 2002-07-05 | **Abandoned** | Features 1+2 partial (audio checklist + line-in from cockpit audio) |
| A-4 | US5454074A | Electronic Checklist System | Boeing | 1994-05-17 | **Expired** | Feature 1 precursor (ECL framework, no voice) |
| A-5 | US5522026A | Single ECL from Multiple Faults | Boeing | 1994-03-18 | **Expired** | Emergency checklist selection logic |
| A-6 | US7289890B2 | Voice Checklist System (VCS) | Boeing (likely) | 2004-11-24 | **Active** | Feature 1 (VCS reads items aloud, voice recognition interface) |
| A-7 | US9550578B2 | Voice Commands Onboard Aircraft | Honeywell | 2014-02-04 | **Active (to 2034)** | Feature 1/3 (grammar-based voice commands, PTT activation) |
| A-8 | WO2002035303A3 | Aircraft ECL System | Rockwell Collins area | 2001-10-23 | Expired/published | General ECL |
| A-9 | US11829589B2 | ECL Command Sequencer | Rockwell Collins | 2022-04-22 | **Active** | Feature 5 (failure annunciation); automated action sequencing |
| A-10 | US20240339039A1 | AI Co-Pilot | Individual | 2024-10-10 | Pending | Feature 1 (but cloud/LLM-dependent; well-distinguished) |
| B-1 | GB2050979A | Automatic Voice Checklist System | Texas Instruments | 1979-05-29 | **Expired (>40 yr)** | Feature 1 precursor (earliest voice checklist) |
| B-2 | GB1356075A | System for Aircraft Checklists | C.B. Dickinson | 1972-11-24 | **Expired (>50 yr)** | Feature 1 precursor |
| B-3 | US6583733B2 | Helicopter GPWS | Honeywell | 2001-05-25 | **Expired** | Feature 1/B (aural alerts via speaker) |
| B-4 | US6175314B1 | Voice Annunciation of ATC Messages | Unknown | 1999-02-25 | **Expired** | Feature 1/B (TTS audio output) |
| B-5 | US9710145B2 | Aircraft HMI Device | Unknown | 2015-08-31 | Active | Feature 3 (PTT-activated voice recognition) |
| C-1 | US20030025682A1 | Aural/Visual Checklist (see A-3) | — | — | Abandoned | Feature 2 (line-in from cockpit audio) |
| C-2 | US9230549B1 | Multi-Modal Communications | Individual | 2011-05-18 | Active | Feature 2/3 partial (radio audio ASR) |
| C-3 | US20230215278A1 | ATC Transcription Messages | Honeywell area | 2022-03-17 | Pending | Feature 2 (tapping radio receive path for ASR) |
| C-4 | US11289094B2 | Clearance Playback System | Unknown | 2020-05-20 | Active | Feature 2 analogue (processing radio receive audio) |
| D-1 | US5774557A | Autotracking Microphone Squelch | N. Airborne Tech | 1995-07-24 | **Expired** | Feature 3 (VOX/VAD in aircraft intercom) |
| E-1 | US9284045B1 | Connected Cockpit System | Garmin | 2014-03-28 | Active | Feature 4 (SD card in avionics) |
| E-2 | US20050026609A1 | Wireless Upload Aircraft Data | Unknown | 2004-06-30 | Abandoned | Feature 4 (removable card for avionics data) |
| E-3 | US5270931A | Software Config Aircraft System | Unknown | ~1993 | **Expired** | Feature 4 (software config via removable medium) |
| F-1 | US5493497A | Fly-By-Wire Fail-Safe | Unknown | 1996-02-20 | **Expired** | Feature 5 (general fail-safe avionics) |
| F-4 | US9583008B2 | Avionic Core/Open World Data | Unknown | 2016-06-09 | Active | Feature 5 (reject invalid data to protect safety function) |

---

## White Space Analysis

### Feature 1: Fully Offline, Fixed-Grammar, Voice-Driven Emergency-Checklist Loop

**Coverage by Prior Art:** MODERATE-TO-HIGH for the basic concept; LOW for the specific implementation.

- The core loop — pilot speaks emergency name → TTS reads checklist items aloud one at a time → pilot speaks a completion word → system advances — is covered in principle by **[US7912592B2 (Garmin, expired)](https://patents.google.com/patent/US20070288129A1/en)** and **[US8793139B1 (expired)](https://patents.google.com/patent/US8793139B1/en)** and structurally suggested by **[US7289890B2 (active)](https://patents.google.com/patent/US7289890B2/en)** and the ancient GB2050979A (Texas Instruments, 1979, expired).
- The **fully offline** constraint (no Wi-Fi, no cloud, deterministic operation on ESP32-S3 class hardware) is **not specifically claimed** in any found live patent. Prior art descriptions either assume avionics-suite connectivity or do not address connectivity constraints.
- The **deterministic fixed/bounded grammar** (not large-vocabulary STT, not NLP) approach on a microcontroller is **not found as a specific avionics claim** in any live patent. The closest is Garmin (expired) and Honeywell US9550578B2 (which uses context-filtered vocabulary but does not specifically claim a bounded/deterministic grammar on embedded hardware).
- **White space identified:** Offline, single-chip (ESP32-S3 class), deterministic, fixed-grammar speech recognition driving an emergency checklist loop. The "offline + deterministic grammar + microcontroller" combination is unclaimed in any live patent found.

### Feature 2: Audio Panel Tap (Receive-Only, Galvanically Isolated) as the Speech Recognition Input Source

**Coverage by Prior Art:** LOW. This is the most novel hardware angle.

- No live patent was found that specifically claims: (a) a passive, receive-only tap of an aircraft audio panel or intercom bus, (b) with galvanic isolation via an isolation transformer, (c) as the primary audio input for a speech recognition system, (d) on an external device that connects to but cannot modify the aircraft audio panel.
- **[US20030025682A1 (abandoned)](https://patents.google.com/patent/US20030025682A1/en)** describes connecting in-line with the cockpit audio system via a stereo line amplifier for audio awareness. This is the closest structurally, but the patent is abandoned, the connection is bidirectional, no isolation is claimed, and voice recognition operates from a separate dedicated microphone.
- **[US20230215278A1 (pending)](https://patents.google.com/patent/US20230215278A1/en)** and **[US11289094B2 (active)](https://patents.google.com/patent/US11289094B2/en)** demonstrate that the industry recognizes the radio/intercom *receive* path as an ASR input — but always within integrated avionics systems, never via an external passive tap with hardware isolation.
- **White space identified:** The specific architecture of: external passive hardware tap on the aircraft audio panel receive bus → galvanic isolation transformer → onboard MCU ASR → checklist advancement is apparently unclaimed. The galvanic isolation + receive-only constraint is safety-critical (cannot interfere with aircraft radio/intercom) and distinguishes this from any bidirectional or integrated system.

### Feature 3: VOX (VAD-Gated) Recognition with PTT as Manual Override Only

**Coverage by Prior Art:** MODERATE for VOX in aviation audio; LOW for VOX-primary ASR for checklist advancement.

- VOX/VAD for aircraft intercom audio gating is clearly established prior art: **[US5774557A (expired)](https://patents.google.com/patent/US5774557A/en)**.
- PTT as the primary trigger for cockpit ASR is well-established prior art: Garmin expired patents, Honeywell US9550578B2 (active), and US9710145B2 (active).
- **White space identified:** Using VOX/VAD as the *primary* and *default* trigger for speech recognition on a checklist device (with PTT retained only as manual override), operating on a tapped audio-panel signal rather than a dedicated microphone, appears to be unclaimed. No live patent claims this combination. Note: the individual elements (VOX, PTT, checklist ASR) are all in prior art; the combination in this architecture is the novel aspect.

### Feature 4: Two-Card Aircraft-Agnostic Configuration (CONFIG Card + DATA Card with Cross-Card Agreement Check)

**Coverage by Prior Art:** LOW. This is a novel architecture.

- Removable SD/PCMCIA/flash cards for delivering configuration data or database updates to avionics are well-established: **[US9284045B1 (active)](https://patents.google.com/patent/US9284045B1/en)**, US20050026609A1 (abandoned), US5270931A (expired).
- However, the **specific two-card split** — one write-protected CONFIG card (defines the installation) and one DATA card (carries content), with the device verifying that both cards agree on the active aircraft identity before operating — was not found in any patent, live or expired.
- This architectural separation serves a specific safety function (installation authority vs. content authority, preventing data-card content from running on the wrong aircraft configuration) that does not appear to have been patented.
- **White space identified:** The dual-removable-card architecture with write-protected CONFIG card, separate DATA card carrying audio content, and a cross-card aircraft identity agreement check as a pre-condition to any checklist presentation is apparently novel and unclaimed.

### Feature 5: Revert-to-Unopened / Complete Fault-State Lockout on Any Configuration Defect

**Coverage by Prior Art:** LOW for the specific combination; MODERATE for the general concept.

- General fail-safe state reversion in avionics is thoroughly established (US5493497A, EP0987562A1, etc., all expired). The concept of refusing to operate on invalid data exists in software architecture.
- **[US9583008B2 (active)](https://patents.google.com/patent/US9583008B2/en)** covers rejecting data from an untrusted source (open world) to protect the certified avionics core — related in spirit but focused on trust boundaries between systems, not on configuration media validation.
- **[US11829589B2 (active)](https://patents.google.com/patent/US11829589B2/en)** covers displaying failure status graphics when automatable checklist actions fail — analogous to fault annunciation but for execution failures, not configuration defects.
- **White space identified:** The specific combination of: (a) exhaustive pre-flight validation of both removable cards (presence, readability, schema validity, audio clip completeness, cross-card aircraft ID agreement), (b) resulting in a **complete refusal to display any checklist** if any condition fails (no partial or stale data), (c) with a dark-cockpit annunciation design (healthy = blank; fault = amber legend; OUT inhibits fault), was not found as a specific patent claim. The dark-cockpit fail-safe design (showing nothing when healthy, only lighting when faulted) combined with the OUT-pin inhibit is a specific safety design pattern not found in the prior art.

---

## Summary: White Space vs. Covered Territory

| Feature | Prior Art Density | White Space Available | Key Live Patents to Distinguish |
|---------|------------------|-----------------------|--------------------------------|
| 1. Offline fixed-grammar voice-driven checklist loop | Moderate | Offline + deterministic grammar + microcontroller combination | US7289890B2, US9550578B2 |
| 2. Audio panel tap, receive-only, galvanically isolated | **Very Low — most novel** | Passive external tap with isolation transformer as primary ASR input | None found; US20030025682A1 (abandoned) closest |
| 3. VOX/VAD primary with PTT manual override | Moderate | VOX-primary on tapped audio-panel signal for checklist ASR | US9550578B2, US9710145B2 (PTT focus) |
| 4. Two-card CONFIG+DATA split with cross-card aircraft agreement | **Low — novel architecture** | Dual write-protected/data card split with cross-card agreement check | None found |
| 5. Revert-to-unopened / dark-cockpit fault lockout on any config defect | Low | Exhaustive pre-flight card validation + complete non-presentation of any data + dark-cockpit design | US9583008B2 (closest in spirit) |

### Key Conclusions for Filing

1. **Claim broadly on Feature 2 first:** The audio-panel-tap architecture (receive-only, galvanically isolated, external passive device) appears to be the most novel and unclaimed aspect. Claims should specifically recite: passive tap, receive-only, galvanic isolation transformer, cannot key/mute/back-feed the audio panel.

2. **Feature 4 (two-card split) is independently claimable:** The CONFIG/DATA card split with cross-card aircraft identity agreement is not found in prior art. This is a safety architecture claim, not just "uses an SD card."

3. **Feature 5 (revert-to-unopened) should be claimed specifically:** The complete non-presentation of any checklist data (rather than degraded or partial presentation) upon any configuration failure, combined with the dark-cockpit annunciation pattern, is apparently novel.

4. **Feature 1 (voice-driven checklist loop) has the most prior art** and the basic loop should be treated as likely disclosed (though not claimed in a live patent for the offline/microcontroller-specific embodiment). Claims for Feature 1 should emphasize the **offline** nature and the **deterministic fixed/bounded grammar** constraint.

5. **Feature 3 (VOX-primary)** is well-supported as individual elements but the combination with the audio-panel tap is in white space.

6. **The Garmin US7912592B2 (now expired)** is the most relevant expired reference for Feature 1. Its expiry means the basic checklist-loop concept is free to practice, but it can be cited as prior art by an examiner. Applicant should proactively distinguish on the offline/microcontroller/audio-tap aspects.

7. **US7289890B2 (Boeing VCS) and US9550578B2 (Honeywell) are the most significant ACTIVE patents to distinguish.** Neither covers the audio-panel-tap architecture or dual-card safety system, but both have live claims on voice-commanded checklist systems and aviation voice commands respectively.

---

## Important Caveats and Limitations of This Search

1. This search was conducted using publicly available patent databases (Google Patents) and general web search. A full professional patent search would also include USPTO full-text search (PAIR), Derwent Innovation, and potentially hire a patent search firm.
2. Patent applications that were filed but not yet published (typically within 18 months of filing) are not searchable and cannot be excluded as prior art.
3. The Texas Instruments GB2050979A (1979) was identified only by citation, not by full text review. Its full scope is not confirmed.
4. Expiration status for some patents is noted as Google Patents reports it; actual expiration should be confirmed through maintenance fee records.
5. Non-US jurisdictions (particularly EU, China, Japan) were not exhaustively searched beyond what appeared in Google Patents' cross-filing results.
6. This document is a research aid for the inventors and their counsel. It is not a freedom-to-operate opinion and should not be treated as legal advice.

---

*Search completed June 2026. All Google Patents URLs valid at time of research.*
