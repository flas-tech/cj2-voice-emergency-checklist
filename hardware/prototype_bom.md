# CJ2 Voice Emergency Checklist — Prototype Bill of Materials

**DEMO/TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**

This BOM is for a **bench/development prototype**. Per design intent it favors
**developer boards and breakouts** wherever possible so the prototype can be
assembled, flashed, and validated quickly without surface-mount rework. Items
flagged **(bench only)** are not part of the installed architecture — they exist
purely to verify audio paths on the bench.

The custom 2-layer baseboard (`PCB1`, see `gerbers/`) is the integration board:
the ESP32-S3 DevKitC and the codec / DAC breakouts plug into it via 2.54mm
header sockets, while the custom analog circuitry — isolation transformers,
line driver, lamp-driver MOSFETs, connectors, and power conditioning — lives on
the PCB itself.

## Architecture mapping (dev board → production)

| Function | Prototype (this BOM) | Production direction |
|---|---|---|
| Compute | ESP32-S3-DevKitC-1 N16R8 module on header sockets | ESP32-S3 module soldered to board (WROOM-1 N16R8) |
| Audio **input** (RX tap) | PCM1808 I2S ADC breakout | Same codec, on-board; aviation-grade isolation xfmr |
| Audio **output** (COM3 TX) | PCM5102A I2S DAC breakout | On-board DAC/line-driver; aviation-grade isolation xfmr |
| Isolation transformers | Generic 600:600 (Bourns/Xicon class) | Allen Avionics AGL-600 (aviation-grade, ~$60+ ea) |
| Annunciator legend | White + amber LEDs (stand-in) | Applied Avionics VIVISUN / Korry split-legend |
| Connectors | D-sub / mini-XLR keyed | MIL-circular keyed, per install |

## Key sourcing notes (verified)

- **ESP32-S3-DevKitC-1 N16R8** (~$18): the **N16R8 variant is required** — 8MB
  PSRAM is needed for ESP-SR voice processing. Available from Mouser, DigiKey,
  and Espressif direct.
- **PCM5102A DAC breakout** (~$4.95): Adafruit #6250 — I2S in, line-level analog
  out, no MCLK required. Used for the COM3 TX output path.
- **PCM1808 ADC breakout** (~$6): self-clocking I2S ADC, no MCLK/I2C needed,
  which is the simplest input option. (ES8388/ES7210 are alternatives but need
  MCLK on GPIO3 + I2C on GPIO1/2.)
- **Isolation transformers**: prototype uses generic 600:600 line-level audio
  transformers. **For production, the aviation-grade Allen Avionics AGL-600**
  (~$60+ each) is the intended part on both the isolated RX tap and the isolated
  COM3 TX line.
- **Custom PCB** (~$2 for 5 pcs): 2-layer, ~100×80mm, fabricable at JLCPCB /
  PCBWay from the Gerber set in `gerbers/`.

## Audio path summary (per MASTER_SPEC Part D)

- **INPUT (I2S_NUM_0, RX only):** analog tap → 600Ω isolation transformer →
  220–470Ω series + RC anti-alias → codec ADC line-in. High-Z, receive-only,
  **cannot back-feed** the panel.
- **OUTPUT (I2S_NUM_1, COM3 TX):** ESP I2S → DAC/line driver → 600:600
  isolation transformer → line-level out to a dedicated COM3-style audio-panel
  channel. Galvanically isolated; **cannot key or back-drive** the panel. The
  onboard speaker has been **removed** from the installed architecture.

## Lamp driver / dark-cockpit integrity

Each legend half (OFF/white on GPIO21, FAULT/amber on GPIO14) is driven by a
low-side logic-level N-MOSFET (2N7002 / AO3400) with a 1kΩ gate resistor and
10kΩ gate pulldown so both lamps are **defined-OFF at boot**. Lamp current runs
on a separate +V rail (5V or 28V), not the logic rail.

## Cost summary

Installed prototype line items total roughly **$70–75** (excluding the bench-only
amp/speaker/mic, which are $0 in the installed column). The aviation-grade
production transformers and VIVISUN legend are the dominant cost step-ups for a
real installation.

---

*Caveat: prices are indicative street prices at time of writing and vary by
distributor and quantity. This is engineering guidance, not a certified parts
list.*
