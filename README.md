# CJ2 Voice Emergency Checklist — Web Demo

A browser-based proof-of-concept for a **single-pilot voice emergency checklist** assistant,
modeled on the **Cessna Citation CJ2 (CE 525A)** emergency checklist card.

The pilot speaks an emergency by name (as if over the intercom); the system selects the
matching checklist, **reads each item aloud**, and **waits for a spoken completion word**
before advancing to the next item — hands-free, with a **push-to-talk** button.

> ⚠️ **DEMO / TRAINING USE ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**
> Always fly the published checklists and procedures for your aircraft.

---

## ✈️ Live demo

Open **`index.html`** in **Google Chrome** or **Microsoft Edge** on desktop.
No build step, no server, no internet, and no login required — it's plain HTML/CSS/JS.

If your host serves it over **HTTPS** (e.g. GitHub Pages), the microphone works directly.
Opening the raw `file://` will load the UI but the browser will block microphone access
(see Troubleshooting).

---

## ESP32-S3 firmware

An offline, on-device version that runs on real hardware (ESP32-S3 + ESP-SR
WakeNet/MultiNet) lives in **[`firmware/`](firmware/)** — including all 12 checklists,
the full speech pipeline, a hardware shopping list, wiring, and flashing instructions.

## How it works

1. **Hold the PUSH-TO-TALK button** (or hold the **Spacebar**) and say the emergency name,
   e.g. *"engine fire"*. Release to submit.
2. The system **reads the matching checklist** aloud, one item at a time.
3. After each item, **hold push-to-talk** and say the item's **completion word**
   (shown under each step), or a universal word: **"check" / "complete" / "next" / "done"**.
4. It advances and reads the next item. Repeat until the checklist is complete.
5. Say **"reset"** (or tap **Reset**) to return to the home screen.

Push-to-talk is used deliberately so the microphone is only open while you're speaking —
this prevents the app from "hearing" its own spoken readout, mirroring a real intercom PTT.

### Why push-to-talk + on-screen buttons
- **Push-to-talk** = the mic listens only while held — accurate and intercom-like.
- **Mark Complete / Repeat / Reset** buttons are always available as a fallback if voice misfires.

---

## Checklists included

Transcribed from the CJ2 emergency card:

- Engine Failure / Fire During Takeoff — Speed Below V1 (Takeoff Rejected)
- Engine Failure / Fire During Takeoff — Speed Above V1 (Takeoff Continued)
- Engine Failure During Final Approach
- **Engine Fire** (LH/RH fire warning light)
- Emergency Restart — Two Engines
- Electrical Fire / Smoke / Smoke Removal
- Cabin Altitude (CABIN ALT)
- Emergency Descent
- Battery Overtemperature (BATT O'TEMP)
- Autopilot Malfunction
- Electric Elevator Trim Runaway
- **Emergency Evacuation** (with a branch: cabin door vs. emergency exit)

Each item defines its own **completion word(s)** derived from the item's target state
(e.g. an "...IDLE" item advances on *"idle"*, a "...PUSH" item on *"push"*).

---

## Editing the checklists

All checklist content lives in **`checklists.js`** as a simple array. Each item:

```js
{ read: "Throttle, affected engine — idle",   // spoken + displayed
  action: "IDLE",                              // bold target state (display only)
  advance: ["idle"] }                          // words that advance this step
```

Branching checklists (like Emergency Evacuation) use a `branch` item plus a `branches` map.
Universal advance words live in `UNIVERSAL_ADVANCE` at the bottom of the file.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| **Push-to-talk does nothing / no mic** | Use **Chrome** or **Edge** on desktop and **allow microphone access** when prompted. Safari/Firefox support for the Web Speech API is limited. |
| **Mic blocked** | The mic only works over **HTTPS** or on **localhost**. A raw `file://` page can't get mic access — serve it (see below) or host on GitHub Pages. |
| **Nothing is recognized** | Speak clearly *after* the button turns red, and keep holding until you finish the phrase. |
| **No voice / silent readout** | Check system + tab volume. Click any button once first to satisfy the browser's audio-autoplay policy. |
| **Wrong checklist matched** | Use the exact emergency name, or tap its chip on the home screen. |
| **Voice keeps misfiring** | Use the on-screen **Mark Complete / Repeat / Reset** buttons as a fallback. |

### Run a local server (recommended for mic access)
```bash
# from the project folder
python3 -m http.server 8000
# then open http://localhost:8000 in Chrome
```

---

## How this maps to the ESP32 hardware target

This web demo intentionally mirrors how the concept would run on an **ESP32-S3**:

| Web demo | ESP32-S3 equivalent |
|---|---|
| Web Speech API recognition | **ESP-SR** (WakeNet wake word + **MultiNet** offline command recognition, English) |
| Push-to-talk button | Physical PTT button / intercom keying |
| `checklists.js` command lists | MultiNet command set (defined per checklist) |
| `speechSynthesis` readout | On-device TTS or pre-recorded audio clips over I2S |
| Browser mic | I2S MEMS mic (e.g. INMP441 / ICS-43434, or ESP32-S3-Korvo-2 mic array) |
| State machine in `app.js` | Same checklist state machine in firmware (C/ESP-IDF) |

On hardware, keep completion phrases **short and acoustically distinct** for best
on-device recognition accuracy.

---

## Project structure

```
index.html       UI markup + how-to + troubleshooting panels
style.css         styling (push-to-talk, panels, checklist items)
app.js            speech recognition + TTS + checklist state machine
checklists.js     all CJ2 emergency checklists (editable data)
```

## Tech

Vanilla HTML/CSS/JavaScript. Uses the browser **Web Speech API**
(`SpeechRecognition` + `speechSynthesis`). No dependencies, no build.

## License

MIT — see `LICENSE`. Checklist text is reproduced for demonstration/training only.
