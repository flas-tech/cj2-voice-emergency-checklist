#!/usr/bin/env python3
"""
make_audio.py — render the spoken checklist clips the firmware plays.

The ESP32 has no built-in TTS, so we pre-render every checklist item (and a few
UI prompts) to 16-bit / 16 kHz / mono WAV files. The firmware plays them by
basename from the SPIFFS 'storage' partition.

Two TTS backends (pick one):
  A) macOS 'say'         : --engine say     (no install)
  B) piper (offline)     : --engine piper --voice /path/to/en_US-*.onnx
  C) espeak-ng           : --engine espeak  (apt install espeak-ng)

Output: ../audio/<basename>.wav   (then `idf.py build flash` embeds them)

Basenames come straight from checklists.c (read_clip) plus UI clips.
Edit the TEXT map below if you change wording.
"""
import argparse, os, subprocess, sys, wave, audioop

OUT = os.path.join(os.path.dirname(__file__), "..", "audio")

# basename -> spoken text. Keep in sync with checklists.c read_clip values.
TEXT = {
    # UI
    "ready":    "State the emergency.",
    "complete": "Checklist complete.",
    # Engine fire
    "engine_fire_1": "Throttle, affected engine, idle.",
    "engine_fire_2": "Engine fire button, lift cover and push.",
    "engine_fire_3": "Either illuminated bottle armed button, push.",
    # Takeoff rejected
    "rej_1": "Brakes, as required.",
    "rej_2": "Throttles, idle.",
    "rej_3": "Speed brakes, extend.",
    # Takeoff continued
    "cont_1": "Maintain directional control.",
    "cont_2": "Accelerate to V R.",
    "cont_3": "Rotate at V R, climb at V two.",
    "cont_4": "Landing gear up, after positive rate of climb.",
    "cont_5": "At fifteen hundred feet, retract flaps, then accelerate.",
    # Final approach
    "fin_1": "Thrust, operating engine, increase as required.",
    "fin_2": "Airspeed, V approach.",
    "fin_3": "Flaps, takeoff and approach.",
    # Emergency restart
    "res_1": "Ignition switches, both on.",
    "res_2": "Left and right fuel boost switches, both on.",
    "res_3": "Throttles, idle.",
    "res_4": "If altitude allows, increase airspeed to two hundred knots.",
    # Electrical fire
    "elec_1": "Oxygen masks, don and emergency.",
    "elec_2": "Microphone select switches, mic oxygen mask.",
    # Cabin altitude
    "cab_1": "Oxygen masks, don and one hundred percent oxygen.",
    "cab_2": "Microphone select switches, mic oxygen mask.",
    "cab_3": "Emergency descent, as required.",
    "cab_4": "Passenger oxygen, make sure passengers are receiving oxygen.",
    # Emergency descent
    "des_1": "Autopilot trim disconnect button, press and release.",
    "des_2": "Throttles, idle.",
    "des_3": "Speed brakes, extend.",
    "des_4": "Airplane pitch attitude, approximately twenty degrees nose down.",
    # Battery overtemp
    "bat_1": "Volt amp, note.",
    "bat_2": "Battery switch, emergency.",
    "bat_3": "Volt amp, note decrease.",
    # Autopilot malfunction
    "ap_1": "Autopilot trim disconnect button, press and release.",
    # Trim runaway
    "trim_1": "Autopilot trim disconnect button, press and release.",
    "trim_2": "Throttles, as required.",
    "trim_3": "Speed brakes, as required.",
    "trim_4": "Manual elevator trim, as required.",
    "trim_5": "Pitch trim circuit breaker, left panel, pull.",
    # Emergency evacuation
    "evac_1": "Parking brake, set.",
    "evac_2": "Throttles, both off.",
    "evac_3": "Left and right engine fire buttons, both press.",
    "evac_4": "Illuminated bottle armed buttons, both press, if fire suspected.",
    "evac_5": "Battery switch, off.",
    "evac_6": "Emergency locator transmitter, make sure the system is activated.",
    "evac_7": "Airplane and immediate area, check for the best escape route.",
    "evac_8": "If exiting through the cabin door, open it. If exiting through the emergency exit, remove and throw the door clear.",
    "evac_9": "Move away from the airplane. Procedure complete.",
}

def to_pcm16_16k_mono(src, dst):
    """Normalise any WAV to 16-bit / 16 kHz / mono for the firmware."""
    with wave.open(src, "rb") as w:
        ch, width, rate = w.getnchannels(), w.getsampwidth(), w.getframerate()
        frames = w.readframes(w.getnframes())
    if width != 2:
        frames = audioop.lin2lin(frames, width, 2); width = 2
    if ch == 2:
        frames = audioop.tomono(frames, width, 0.5, 0.5); ch = 1
    if rate != 16000:
        frames, _ = audioop.ratecv(frames, width, ch, rate, 16000, None); rate = 16000
    with wave.open(dst, "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(16000)
        o.writeframes(frames)

def synth(engine, voice, text, dst):
    tmp = dst + ".raw.wav"
    if engine == "say":                      # macOS
        subprocess.run(["say", "-o", tmp, "--data-format=LEI16@22050", text], check=True)
    elif engine == "espeak":
        subprocess.run(["espeak-ng", "-w", tmp, text], check=True)
    elif engine == "piper":
        if not voice: sys.exit("--voice required for piper")
        with open(tmp, "wb") as f:
            subprocess.run(["piper", "--model", voice, "--output_file", tmp],
                           input=text.encode(), check=True)
    else:
        sys.exit("unknown engine")
    to_pcm16_16k_mono(tmp, dst); os.remove(tmp)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="say", choices=["say", "espeak", "piper"])
    ap.add_argument("--voice", help="piper .onnx voice model path")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for base, text in TEXT.items():
        dst = os.path.join(OUT, base + ".wav")
        print("•", base)
        synth(a.engine, a.voice, text, dst)
    print(f"\nDone. {len(TEXT)} clips written to {os.path.abspath(OUT)}")
    print("Now run:  idf.py build flash monitor")

if __name__ == "__main__":
    main()
