#!/usr/bin/env python3
"""
build_aircraft.py — generate an SD-card aircraft package from a checklist spec.

Produces, for one aircraft:
    <out>/<TAIL>/checklists.json     the data the firmware reads at boot
    <out>/<TAIL>/audio/*.wav         the spoken readout clips

The JSON schema (also documented in firmware/README.md):

{
  "aircraft": "CJ2",
  "title": "Cessna Citation CJ2 (CE 525A)",
  "universal_advance": ["check", "checked", "complete", "next"],
  "checklists": [
    {
      "id": "engine_fire",
      "title": "Engine Fire",
      "type": "emergency",                       // emergency | normal | abnormal
      "triggers": ["engine fire", "fire warning"],
      "items": [
        { "clip": "engine_fire_1",
          "text": "Throttle, affected engine, idle.",
          "advance": ["idle"] }
      ]
    }
  ]
}

VOICE RULES (MultiNet, enforced by validate()):
  - triggers / advance / universal phrases: lowercase letters + single spaces only.
  - NO digits or punctuation. Spell numbers ("v one", "two hundred").
  - "text" (read aloud) is free-form; it only feeds the TTS clip.

This file is the single source of truth: it contains the CJ2 data inline, emits the
JSON, and (optionally) renders the audio with the same engines as make_audio.py.
"""
import argparse, json, os, re, subprocess, sys, wave, audioop

# ----------------------------------------------------------------------------
# CJ2 data (mirrors the compiled checklists; edit here or hand-write JSON later)
# Each item: (clip, read_aloud_text, [advance words])
# ----------------------------------------------------------------------------
CJ2 = {
  "aircraft": "CJ2",
  "title": "Cessna Citation CJ2 (CE 525A)",
  "universal_advance": ["check", "checked", "complete", "next"],
  "checklists": [
    ("engine_fire", "Engine Fire", "emergency",
     ["engine fire", "fire warning"], [
        ("engine_fire_1", "Throttle, affected engine, idle.", ["idle"]),
        ("engine_fire_2", "Engine fire button, lift cover and push.", ["push", "pushed"]),
        ("engine_fire_3", "Either illuminated bottle armed button, push.", ["push", "pushed", "armed"]),
     ]),
    ("takeoff_rejected", "Takeoff Rejected — Below V1", "emergency",
     ["takeoff rejected", "abort takeoff", "speed below v one"], [
        ("rej_1", "Brakes, as required.", ["as required", "required"]),
        ("rej_2", "Throttles, idle.", ["idle"]),
        ("rej_3", "Speed brakes, extend.", ["extend", "extended"]),
     ]),
    ("takeoff_continued", "Takeoff Continued — Above V1", "emergency",
     ["takeoff continued", "speed above v one"], [
        ("cont_1", "Maintain directional control.", ["control", "maintained"]),
        ("cont_2", "Accelerate to V R.", ["accelerating", "rotate speed"]),
        ("cont_3", "Rotate at V R, climb at V two.", ["rotate", "climbing"]),
        ("cont_4", "Landing gear up, after positive rate of climb.", ["up", "gear up"]),
        ("cont_5", "At fifteen hundred feet, retract flaps, then accelerate.", ["flaps up", "accelerating"]),
     ]),
    ("engine_fail_final", "Engine Failure During Final Approach", "emergency",
     ["engine failure final approach", "engine failure approach"], [
        ("fin_1", "Thrust, operating engine, increase as required.", ["increased", "as required"]),
        ("fin_2", "Airspeed, V approach.", ["v approach", "set"]),
        ("fin_3", "Flaps, takeoff and approach.", ["set", "flaps set"]),
     ]),
    ("emergency_restart", "Emergency Restart — Two Engines", "emergency",
     ["emergency restart", "engine restart", "restart engines"], [
        ("res_1", "Ignition switches, both on.", ["both on", "on"]),
        ("res_2", "Left and right fuel boost switches, both on.", ["both on", "on"]),
        ("res_3", "Throttles, idle.", ["idle"]),
        ("res_4", "If altitude allows, increase airspeed to two hundred knots.", ["increased", "set"]),
     ]),
    ("electrical_fire", "Electrical Fire or Smoke", "emergency",
     ["electrical fire", "electrical smoke", "smoke removal", "cabin smoke"], [
        ("elec_1", "Oxygen masks, don and emergency.", ["on", "donned", "emergency"]),
        ("elec_2", "Microphone select switches, mic oxygen mask.", ["set", "selected"]),
     ]),
    ("cabin_altitude", "Cabin Altitude", "emergency",
     ["cabin altitude", "cabin alt", "depressurization"], [
        ("cab_1", "Oxygen masks, don and one hundred percent oxygen.", ["on", "donned"]),
        ("cab_2", "Microphone select switches, mic oxygen mask.", ["set", "selected"]),
        ("cab_3", "Emergency descent, as required.", ["as required", "descending"]),
        ("cab_4", "Passenger oxygen, make sure passengers are receiving oxygen.", ["confirmed", "receiving"]),
     ]),
    ("emergency_descent", "Emergency Descent", "emergency",
     ["emergency descent", "rapid descent"], [
        ("des_1", "Autopilot trim disconnect button, press and release.", ["pressed", "released"]),
        ("des_2", "Throttles, idle.", ["idle"]),
        ("des_3", "Speed brakes, extend.", ["extend", "extended"]),
        ("des_4", "Airplane pitch attitude, approximately twenty degrees nose down.", ["nose down", "set"]),
     ]),
    ("battery_overtemp", "Battery Overtemperature", "emergency",
     ["battery overtemp", "battery overtemperature", "batt o temp"], [
        ("bat_1", "Volt amp, note.", ["noted", "note"]),
        ("bat_2", "Battery switch, emergency.", ["emergency", "set"]),
        ("bat_3", "Volt amp, note decrease.", ["noted", "decreasing"]),
     ]),
    ("autopilot_malfunction", "Autopilot Malfunction", "emergency",
     ["autopilot malfunction", "autopilot failure"], [
        ("ap_1", "Autopilot trim disconnect button, press and release.", ["pressed", "released"]),
     ]),
    ("trim_runaway", "Electric Elevator Trim Runaway", "emergency",
     ["trim runaway", "elevator trim runaway", "elevator trim"], [
        ("trim_1", "Autopilot trim disconnect button, press and release.", ["pressed", "released"]),
        ("trim_2", "Throttles, as required.", ["as required", "set"]),
        ("trim_3", "Speed brakes, as required.", ["as required", "set"]),
        ("trim_4", "Manual elevator trim, as required.", ["as required", "set"]),
        ("trim_5", "Pitch trim circuit breaker, left panel, pull.", ["pull", "pulled"]),
     ]),
    ("emergency_evacuation", "Emergency Evacuation", "emergency",
     ["emergency evacuation", "evacuate", "evacuation"], [
        ("evac_1", "Parking brake, set.", ["set"]),
        ("evac_2", "Throttles, both off.", ["both off", "off"]),
        ("evac_3", "Left and right engine fire buttons, both press.", ["both press", "pressed"]),
        ("evac_4", "Illuminated bottle armed buttons, both press, if fire suspected.", ["both press", "pressed"]),
        ("evac_5", "Battery switch, off.", ["off"]),
        ("evac_6", "Emergency locator transmitter, make sure the system is activated.", ["activated", "confirmed"]),
        ("evac_7", "Airplane and immediate area, check for the best escape route.", ["checked", "confirmed"]),
        ("evac_8", "If exiting through the cabin door, open it. If through the emergency exit, remove and throw the door clear.", ["cabin door", "emergency exit"]),
        ("evac_9", "Move away from the airplane. Procedure complete.", ["clear", "complete"]),
     ]),
    # ---- Example NORMAL checklist (extend with your own) ----
    ("before_start", "Before Start", "normal",
     ["before start", "before engine start"], [
        ("bs_1", "Parking brake, set.", ["set"]),
        ("bs_2", "Seat belts, fasten.", ["fastened", "set"]),
        ("bs_3", "Battery switch, on.", ["on"]),
        ("bs_4", "Fuel quantity, check.", ["checked", "check"]),
        ("bs_5", "Flight controls, free and correct.", ["free and correct", "checked"]),
     ]),
  ],
}

PHRASE_RE = re.compile(r"^[a-z]+( [a-z]+)*$")

def to_json(spec):
    out = {"aircraft": spec["aircraft"], "title": spec["title"],
           "universal_advance": spec["universal_advance"], "checklists": []}
    for cid, title, ctype, triggers, items in spec["checklists"]:
        out["checklists"].append({
            "id": cid, "title": title, "type": ctype, "triggers": triggers,
            "items": [{"clip": c, "text": t, "advance": a} for (c, t, a) in items],
        })
    return out

def validate(doc):
    errs = []
    def chk(phrase, where):
        if not PHRASE_RE.match(phrase):
            errs.append(f"{where}: '{phrase}' must be lowercase letters + spaces only "
                        f"(no digits/punctuation; spell numbers out)")
    for p in doc["universal_advance"]:
        chk(p, "universal_advance")
    ids = set()
    for cl in doc["checklists"]:
        if cl["id"] in ids: errs.append(f"duplicate checklist id '{cl['id']}'")
        ids.add(cl["id"])
        if not cl["triggers"]: errs.append(f"{cl['id']}: needs at least one trigger")
        for t in cl["triggers"]: chk(t, f"{cl['id']} trigger")
        if not cl["items"]: errs.append(f"{cl['id']}: needs at least one item")
        for it in cl["items"]:
            if not it["clip"]: errs.append(f"{cl['id']}: item missing clip name")
            for a in it["advance"]: chk(a, f"{cl['id']}/{it['clip']} advance")
    # MultiNet ~200 active-command headroom note (per-state in firmware, so just warn on totals)
    return errs

# ---- audio rendering (same engines as make_audio.py) ----
def to_pcm16_16k_mono(src, dst):
    with wave.open(src, "rb") as w:
        ch, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        frames = w.readframes(w.getnframes())
    if width != 2: frames = audioop.lin2lin(frames, width, 2); width = 2
    if ch == 2:    frames = audioop.tomono(frames, width, 0.5, 0.5)
    if rate != 16000:
        frames, _ = audioop.ratecv(frames, width, 1, rate, 16000, None)
    with wave.open(dst, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(16000); o.writeframes(frames)

def synth(engine, voice, text, dst):
    tmp = dst + ".raw.wav"
    if engine == "say":
        subprocess.run(["say", "-o", tmp, "--data-format=LEI16@22050", text], check=True)
    elif engine == "espeak":
        subprocess.run(["espeak-ng", "-w", tmp, text], check=True)
    elif engine == "piper":
        if not voice: sys.exit("--voice required for piper")
        subprocess.run(["piper", "--model", voice, "--output_file", tmp],
                       input=text.encode(), check=True)
    else: sys.exit("unknown engine")
    to_pcm16_16k_mono(tmp, dst); os.remove(tmp)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../sdcard_template", help="SD root to write into")
    ap.add_argument("--audio", action="store_true", help="also render WAV clips")
    ap.add_argument("--engine", default="say", choices=["say", "espeak", "piper"])
    ap.add_argument("--voice")
    a = ap.parse_args()

    doc = to_json(CJ2)
    errs = validate(doc)
    if errs:
        print("VALIDATION FAILED:"); [print("  -", e) for e in errs]; sys.exit(1)

    base = os.path.join(os.path.dirname(__file__), a.out, doc["aircraft"])
    os.makedirs(os.path.join(base, "audio"), exist_ok=True)
    with open(os.path.join(base, "checklists.json"), "w") as f:
        json.dump(doc, f, indent=2)
    n_items = sum(len(c["items"]) for c in doc["checklists"])
    print(f"Wrote {base}/checklists.json  "
          f"({len(doc['checklists'])} checklists, {n_items} items)")

    if a.audio:
        ui = {"ready": "State the emergency.", "complete": "Checklist complete."}
        for name, text in ui.items():
            synth(a.engine, a.voice, text, os.path.join(base, "audio", name + ".wav"))
        for c in doc["checklists"]:
            for it in c["items"]:
                synth(a.engine, a.voice, it["text"],
                      os.path.join(base, "audio", it["clip"] + ".wav"))
                print("  •", it["clip"])
        print("Audio rendered.")
    else:
        print("Skipped audio (pass --audio to render WAVs).")

if __name__ == "__main__":
    main()
