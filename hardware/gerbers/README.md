# CJ2 Voice Emergency Checklist — Prototype Baseboard Gerbers

**DEMO/TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**

Fab-ready Gerber layer set + Excellon drill for the **Rev A** prototype
baseboard. Generated programmatically (`../gen_gerber.py`), RS-274X, metric,
absolute, 4.6 number format. Board is **2-layer, 100 × 80 mm**.

## Layer files (KiCad / JLCPCB naming)

| File | Layer |
|---|---|
| `cj2_voice_checklist_proto-Edge_Cuts.gbr` | Board outline |
| `cj2_voice_checklist_proto-F_Cu.gbr` | Top copper |
| `cj2_voice_checklist_proto-B_Cu.gbr` | Bottom copper (ground ring + jumpers) |
| `cj2_voice_checklist_proto-F_Mask.gbr` | Top soldermask |
| `cj2_voice_checklist_proto-B_Mask.gbr` | Bottom soldermask |
| `cj2_voice_checklist_proto-F_Silkscreen.gbr` | Top silkscreen |
| `cj2_voice_checklist_proto-B_Silkscreen.gbr` | Bottom silkscreen |
| `cj2_voice_checklist_proto.drl` | Excellon drill (PTH) |
| `cj2_voice_checklist_proto_preview.png` | Rendered composite preview |

## What's on the board

This is an **integration baseboard**: the ESP32-S3-DevKitC-1 (N16R8) and the
codec/DAC breakouts plug into 2.54mm header **sockets**, while the custom analog
front/back end is on the PCB itself.

- **U1** — ESP32-S3-DevKitC-1 socket (two 1×22 rows, 0.9" apart)
- **Audio IN (RX, isolated):** J2 → T1 (600:600 iso xfmr) → R1 + RC1 anti-alias → U2 (PCM1808 ADC) → I2S in
- **Audio OUT (COM3 TX, isolated):** I2S out → U3 (PCM5102A DAC) → T2 (600:600 iso xfmr) → J3
- **SD1/SD2** — dual microSD (config + data), shared 1-bit SDMMC with R6/R7 pull-ups
- **Q1/Q2** — low-side lamp-driver MOSFETs (OFF/white on G21, FAULT/amber on G14) with R2/R3 gate + R4/R5 pulldown
- **SW1** — annunciator/legend header; **D1/D2** bench legend LEDs
- **SW2** — PTT override; **J1** — main I/O (SELECT / legends / PTT / power)
- **PWR1** — 5V input; **C9** bulk + **C1–C8** decoupling

## Pin map (per MASTER_SPEC Part D.2)

PTT=G0, SELECT=G10, LEGEND_OFF/white=G21, LEGEND_FAULT/amber=G14, STATUS=G48;
AIN BCLK=4 LRCLK=5 DIN=6 MCLK=3; CODEC I2C SDA=1 SCL=2; SD CLK=7 CMD=9 D0=8,
CD=47/38; AOUT BCLK=15 LRCLK=16 DOUT=17.

## Important caveats

- **Routing is a prototype-grade illustrative integration**, not a
  manufacturing-signed-off layout. It has **not** been through formal DRC,
  impedance control, or net-by-net continuity verification. Before ordering,
  import into KiCad/Altium, run DRC, and verify every net against
  `MASTER_SPEC.md` Part D.
- Footprints for the codec/DAC are simplified dual-row land patterns sized for
  the breakout headers; confirm against the exact breakout you buy.
- Isolation transformers shown as generic 600:600 6-pin footprints; the
  aviation-grade Allen Avionics AGL-600 (production) has a different footprint.
- Fabricate at JLCPCB / PCBWay (2-layer, 1.6mm, HASL). ~$2 for 5 pcs.
