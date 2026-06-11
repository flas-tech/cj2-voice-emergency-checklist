# Enclosure Specification — CJ2 Voice Emergency Checklist Unit

> **DEMO / TRAINING USE ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**
> This enclosure is for a bench / training prototype. It is **not** a certified
> avionics installation. Nothing here constitutes an STC, TSO, or field-approval
> package. Any installation in or near an actual aircraft requires a licensed A&P/IA
> and the appropriate FAA approval (Form 337 / STC / TSO-authorization). This document
> intentionally borrows airworthiness *conventions* (DZUS rail, DO-160 categories) so
> the prototype "looks and fits right," but it is a mock-up.

**Audience:** the mechanical / industrial-design engineer who will model, prototype,
and fabricate the housing. It assumes the electronics, pinout, and behavior are fixed
(see `TECH_DATA.md` and `wiring_diagram.png` in this folder).

---

## 1. Design intent & architecture

The unit splits into **two physical pieces** connected by a short harness, because the
pilot-facing controls and the processor have very different placement needs:

| Piece | Contents | Where it lives | Why |
|---|---|---|---|
| **A. Panel bezel** (pilot-facing) | Applied Avionics split-legend annunciator switch, speaker + grille, optional PTT button | Front instrument panel / pedestal, on the **DZUS rail** | Must be seen and reached by the crew; dark-cockpit annunciator must sit in the pilot's normal scan |
| **B. Remote processor box** (blind) | ESP32-S3 board, INMP441 mic, MAX98357A amp, microSD, lamp-driver board, power conditioning | Avionics bay / behind-panel shelf, blind-mounted | Keeps heat, the SD slot, and wiring out of the panel; only the bezel needs panel real estate |

A **single all-in-one panel box** is acceptable for a pure bench demo, but the two-piece
split is the recommended target because it mirrors how real remote-mount avionics are
installed and keeps the microphone away from cooling-fan / avionics noise.

```
   PANEL (crew side)                          AVIONICS BAY (blind)
 +----------------------+                  +--------------------------+
 |  [VOICE CHKLST OFF]  |   bezel harness  |   ESP32-S3 + amp + mic   |
 |  [VOICE CHKLST FALT] |<================>|   microSD (front access) |
 |   (.) speaker grille |   (D-sub or      |   lamp-driver board      |
 |    o  PTT (optional) |    circular conn) |   power conditioning     |
 +----------------------+                  +--------------------------+
        Piece A                                     Piece B
```

---

## 2. Piece A — Panel bezel

### 2.1 Form factor & mounting
- **Mounting standard:** DZUS rail (the CJ2 pedestal and most of its panel use DZUS).
  - DZUS fastener pitch (hole-to-hole) = **3/8 in (9.525 mm)**; fastener clearance hole
    **0.255 in (6.48 mm)**.
  - Bezel **height must be a whole multiple of 3/8 in** ("the DZUS rhythm"). Target a
    **3-unit panel = 1.125 in (28.575 mm)** tall, or **4-unit = 1.5 in (38.1 mm)** if the
    speaker grille needs more room.
  - Standard pedestal panel **width = 5.75 in (146.05 mm)** nominal aluminum
    (≈ 144.45 mm usable face). Use this width so the bezel drops into a standard slot.
  - Backplate: **1/16 in (1.6 mm) aluminum** (6061-T6) per DZUS convention; first/last
    fastener centers **1.5 × 3/8 in = 14.29 mm** from each end.
- **Alternative (round-hole) mount:** if a DZUS slot is unavailable, provide a variant that
  fits a **standard 3-1/8 in (79.4 mm) instrument cutout** with four 6-32 screws on the
  standard bolt circle, so it can replace a blanking plate.

### 2.2 Front-face layout (top → bottom, dark-cockpit order)
1. **Split-legend annunciator switch** (Applied Avionics VIVISUN / Korry).
   - Cutout per the **specific switch series' datasheet** — confirm the exact part before
     cutting. Typical VIVISUN 1-pole rectangular bezel ≈ **15 × 15 mm** to **19 × 19 mm**
     face; provide a snap/screw retention per that series.
   - **Top half engraves `VOICE CHKLST OFF` (white); bottom half `VOICE CHKLST FAULT`
     (amber).** Legend orientation must read upright when panel-installed.
2. **Speaker grille** — see §4. Open area ≥ 40% over the speaker cone; offset from the
   switch so a finger on the switch never covers the grille.
3. **PTT button (optional)** — momentary, guarded or recessed so it is not bumped. If the
   aircraft already has a yoke/PTT tie-in, omit this and route PTT through the harness.

### 2.3 Bezel material & finish
- Face: **6061-T6 aluminum**, 2.0–3.0 mm, or ABS/PC for a non-structural demo.
- Finish: **matte black, low-gloss (≤ 10 gloss units)** to suppress windshield glare —
  this is standard for instrument-panel parts and supports dark-cockpit philosophy.
- Engraving: laser-etched + paint-fill, white and amber to match the legend colors, OR rely
  solely on the switch's internal legend (preferred — fewer painted parts to chip).
- Edges chamfered 0.5 mm; no sharp corners facing the crew.

---

## 3. Piece B — Remote processor box

### 3.1 Size & internal layout
- Target internal volume sized around the **largest board path = the ESP32-S3 DevKitC-1
  (≈ 70 × 26 mm)** plus the MAX98357A breakout, mic, microSD breakout, and the
  2-channel lamp-driver board. A practical target outer envelope:
  **≈ 110 × 80 × 45 mm (L × W × H)**. Confirm against the actual stacked board set.
- Use **internal standoffs / PCB rails** (M2.5 brass inserts) so boards are screwed down,
  not floating — important for the vibration environment (§6).
- Keep the **INMP441 mic away from the amplifier and any fan**; if the mic lives in this
  box, put an acoustic port (small grille or 4–6 mm hole with mesh) on a quiet face. For
  best recognition, the mic can instead live in the bezel near the crew — engineer's choice,
  but keep the I2S run short (< 150 mm).

### 3.2 Access & connectors
- **microSD access:** a slot on a removable face or an externally-accessible push-push SD
  carrier, so the card can be swapped (to reconfigure the aircraft) **without opening the
  sealed box**. Label it `CONFIG CARD — FAT32`.
- **USB-C service port:** a covered/recessed USB-C pass-through for flashing/power on the
  bench. Add a **silicone plug or hinged cover**; it is not for in-service use.
- **Main connector:** one **circular bayonet connector** (e.g. a small MIL-style / M12) OR
  a **9-pin D-sub** carrying: bezel switch SELECT, the two legend-lamp drives, PTT, speaker
  +/–, and power/ground. Pin-out table to be finalized from `board_pins.h`. Use a keyed,
  positive-latching connector — no loose flying leads.
- **Power:** accept the bench supply (USB 5 V ≥ 1 A). If a 28 VDC aircraft-bus mock-up is
  wanted, include a **28 V → 5 V DC-DC** (≥ 2 A) inside the box with input transient
  protection (TVS + fuse) — but mark clearly this is a demo regulator, not DO-160 qualified.

### 3.3 Box material & EMI
- Material: **aluminum (extruded or machined)** preferred for the remote box — it doubles as
  an EMI shield and a heatsink. ABS/PC acceptable for a pure desk demo.
- If plastic, add a **conductive shield liner or coating** (nickel paint) tied to ground, since
  the unit sits near sensitive avionics; this is good practice even for a mock-up.
- Single-point **chassis ground stud** bonded to the connector shell and the ESP32 ground.

---

## 4. Audio (speaker) details
- Speaker: **4–8 Ω, ≥ 2 W**, sealed-back or with a small rear volume (5–15 cm³) to avoid a
  tinny sound; the MAX98357A peaks ~650 mA at 5 V/4 Ω.
- Grille: perforated metal or molded slots, **≥ 40% open area**, with a thin acoustic mesh
  behind it for dust. Keep the speaker front-firing toward the crew.
- Gasket the speaker to the bezel to prevent buzz at volume.

---

## 5. Thermal
- The ESP32-S3 running ESP-SR is the main heat source but is **low power** (a few hundred
  mW typical); no fan is required.
- Provide **passive convection**: a few vent slots low and high on the remote box, or bond
  the ESP module's ground plane to the aluminum wall with a thermal pad.
- **Do not seal the box fully airtight if relying on convection.** If sealing is required for
  dust/water, switch to conduction cooling (thermal pad to the aluminum case) and verify the
  internal rise stays < 20 °C above ambient at 55 °C ambient.
- Keep the DC-DC (if fitted) on its own thermal path; it is the second heat source.

---

## 6. Environmental targets (DO-160G categories — *aspirational for the mock-up*)

These are the categories a real unit in this location would target. For the prototype, treat
them as **design guidance**, not test obligations.

| DO-160G section | Category to design toward | Note for this unit |
|---|---|---|
| §4 Temperature/Altitude | Cat **A2** (controlled cockpit) | −15 °C to +55 °C operating; pressurized cabin |
| §7 Shock & crash safety | Operational shock + crash-safety | Mounts/standoffs must retain boards; nothing becomes a projectile |
| §8 Vibration | Cat **S** (fixed-wing) | Use locking hardware; conformal-coat the boards; no press-fit-only parts |
| §6 Humidity | Cat **A** | 48-hr; conformal coat recommended |
| §16/17 Power input / spike | — | Add TVS + fuse on any 28 V input mock-up |
| §20/21 RF emission/susceptibility | — | Aluminum case + grounded shield; keep WiFi disabled (it is, in firmware) |
| §25 ESD | — | Bond exposed metal; recessed connectors |
| §26 Flammability | — | Use flame-rated plastics (UL94 V-0) if not aluminum |

> The firmware already runs **fully offline with WiFi/BT off**, which materially helps the
> RF-emission story for any future qualification.

---

## 7. Labeling & markings
- **Required placard on the bezel and the box:** `DEMO / TRAINING ONLY — NOT FOR FLIGHT`.
- Box exterior: unit name, a serial/asset field, the config-card format (`FAT32`), and the
  USB service-port "bench use only" note.
- Annunciator legends: `VOICE CHKLST OFF` (white, top), `VOICE CHKLST FAULT` (amber, bottom).
- Use **amber for caution / white for status** consistent with FAA AC 25-11B color
  conventions used elsewhere in this project.

---

## 8. Deliverables requested from the engineer
1. **3D CAD** (STEP + native) of both pieces, with the board set and switch modeled in place.
2. **2D drawings** with the DZUS hole pattern, the switch cutout (dimensioned from the chosen
   switch datasheet), grille pattern, and connector cutouts — fully dimensioned, GD&T where it
   matters (switch cutout, DZUS holes).
3. **Connector pin-out** mapping the bezel-to-box harness to `board_pins.h` signals.
4. A **bench-printable prototype** (FDM/SLA) of both pieces for fit-check before any aluminum.
5. **BOM** for mechanical parts (fasteners, inserts, connector, speaker, grille mesh, gasket).
6. Tolerance call-outs: switch cutout ±0.1 mm; DZUS holes ±0.1 mm on the 9.525 mm pitch;
   general ±0.25 mm.

---

## 9. Open items for the engineer to confirm
- **Exact Applied Avionics switch part number** → drives the bezel cutout and depth. This is
  the single most important dimension; nothing else can be finalized until it is fixed.
- **Mounting reality in the target panel:** is there a free DZUS slot, or must this go into a
  3-1/8 in round hole / a custom sub-panel? Pick the §2.1 variant accordingly.
- **Where the mic lives** (bezel vs. remote box) — affects acoustic ports and harness count.
- **Whether a 28 V input** is wanted, or USB 5 V bench power is sufficient for the demo.
- **Speaker model** → sets the grille open area and rear-volume cavity.

---

## 10. Reference dimensions (quick table)

| Item | Value | Source |
|---|---|---|
| DZUS fastener pitch | 3/8 in = **9.525 mm** | DZUS rail standard |
| DZUS clearance hole | 0.255 in = **6.48 mm** | DZUS rail standard |
| Panel backplate thickness | 1/16 in = **1.6 mm** | DZUS convention |
| First fastener offset from edge | 1.5 × pitch = **14.29 mm** | DZUS convention |
| Standard pedestal panel width | **≈ 146 mm** alu (144.45 mm face) | DZUS panel convention |
| Standard round instrument hole | 3-1/8 in = **79.4 mm** | Instrument panel standard |
| Remote box target envelope | **≈ 110 × 80 × 45 mm** | This design (confirm vs. boards) |
| Speaker | 4–8 Ω, ≥ 2 W | `TECH_DATA.md` §3.2 |

---

### Source references
- DZUS rail dimensions & "DZUS rhythm" — MyCockpit panel-building dimensions guide:
  https://www.mycockpit.org/tutorials/Panelbuildingfocussedondimensions.pdf
- DZUS rail product reference — Dallas Avionics:
  https://www.dallasavionics.com/cgi-bin/products.cgi?master=install&category=rail&man=dzus_rail&url=359.html
- Standard 3-1/8 in instrument cutout — Aircraft Spruce instrument adapter / cover plate:
  https://www.aircraftspruce.com/catalog/inpages/instradaptkit.php
- DO-160G environmental categories — RTCA / Wikipedia summary:
  https://en.wikipedia.org/wiki/DO-160 ; FAA AC 21-16G:
  https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1019280
- Annunciator color / dark-cockpit conventions — FAA AC 25-11B:
  https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf

> **DEMO / TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.**
