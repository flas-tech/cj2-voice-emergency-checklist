#!/usr/bin/env python3
"""Build the CJ2 Voice Emergency Checklist enclosure mechanical spec (PDF).

Reuses the visual language of build_packet.py (fonts, palette, helpers, page
templates) so the two documents look like a matched set.

GLYPH NOTE: DM Sans has U+2126 (ohm) and U+00B5 (micro) but NOT U+03A9.
Use \u2126 for the ohm sign. Avoid Unicode subscripts.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    NextPageTemplate, PageBreak, Image, ListFlowable, ListItem, HRFlowable,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

FONTS = "/home/user/workspace/fonts"
DOCS = "/home/user/workspace/cj2-checklist/firmware/docs"
OUT = os.path.join(DOCS, "CJ2_Voice_Checklist_Enclosure_Spec.pdf")
DIAGRAM = os.path.join(DOCS, "wiring_diagram.png")

# ---- fonts ----
pdfmetrics.registerFont(TTFont("DM", f"{FONTS}/DMSans-Regular-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-B", f"{FONTS}/DMSans-Bold-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-M", f"{FONTS}/DMSans-Medium-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-I", f"{FONTS}/DMSans-Italic-static.ttf"))
pdfmetrics.registerFont(TTFont("Mono", f"{FONTS}/JetBrainsMono-Regular-static.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B", f"{FONTS}/JetBrainsMono-Bold-static.ttf"))
registerFontFamily("DM", normal="DM", bold="DM-B", italic="DM-I", boldItalic="DM-B")

# ---- palette (matched to tech packet) ----
INK   = colors.HexColor("#28251D")
MUTED = colors.HexColor("#5A5852")
FAINT = colors.HexColor("#9A988F")
BG    = colors.HexColor("#F7F6F2")
SURF  = colors.HexColor("#FBFBF9")
BORDER= colors.HexColor("#D4D1CA")
TEAL  = colors.HexColor("#01696F")
TEALD = colors.HexColor("#0C4E54")
AMBER = colors.HexColor("#964219")
HEADER_BG = colors.HexColor("#0C4E54")
ROW_ALT = colors.HexColor("#F1F0EB")

PAGE_W, PAGE_H = letter
ML = MR = 0.85 * inch
MT = 0.9 * inch
MB = 0.85 * inch

ss = getSampleStyleSheet()
def S(name, **kw):
    base = kw.pop("parent", ss["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

body = S("body", fontName="DM", fontSize=9.5, leading=14, textColor=INK, spaceAfter=6, alignment=TA_LEFT)
bodyj = S("bodyj", parent=body, alignment=TA_JUSTIFY)
h1 = S("h1", fontName="DM-B", fontSize=18, leading=22, textColor=TEALD, spaceBefore=4, spaceAfter=10)
h2 = S("h2", fontName="DM-B", fontSize=13, leading=17, textColor=INK, spaceBefore=14, spaceAfter=6)
h3 = S("h3", fontName="DM-M", fontSize=10.5, leading=14, textColor=TEALD, spaceBefore=10, spaceAfter=4)
small = S("small", fontName="DM", fontSize=8, leading=11, textColor=MUTED)
cap = S("cap", fontName="DM-I", fontSize=8.5, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceBefore=4)
cell = S("cell", fontName="DM", fontSize=8.3, leading=11, textColor=INK)
cellb = S("cellb", fontName="DM-B", fontSize=8.3, leading=11, textColor=INK)
cellmono = S("cellmono", fontName="Mono", fontSize=7.8, leading=10.5, textColor=INK)
cellhdr = S("cellhdr", fontName="DM-B", fontSize=8.3, leading=11, textColor=colors.white)

def A(text, url):
    return f'<a href="{url}" color="#01696F">{text}</a>'

def make_table(data, col_widths, header=True, font_styles=None):
    rows = []
    for r_i, row in enumerate(data):
        new = []
        for c_i, c in enumerate(row):
            if isinstance(c, Paragraph):
                new.append(c)
            else:
                st = cellhdr if (header and r_i == 0) else cell
                if font_styles and (r_i, c_i) in font_styles:
                    st = font_styles[(r_i, c_i)]
                new.append(Paragraph(str(c), st))
        rows.append(new)
    t = Table(rows, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,-1), 0.4, BORDER),
        ("LINEABOVE", (0,0), (-1,0), 0.6, HEADER_BG),
    ]
    if header:
        style += [
            ("BACKGROUND", (0,0), (-1,0), HEADER_BG),
            ("LINEBELOW", (0,0), (-1,0), 0.6, HEADER_BG),
            ("TOPPADDING", (0,0), (-1,0), 6),
            ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ]
        for ri in range(2, len(data), 2):
            style.append(("BACKGROUND", (0,ri), (-1,ri), ROW_ALT))
    else:
        for ri in range(1, len(data), 2):
            style.append(("BACKGROUND", (0,ri), (-1,ri), ROW_ALT))
    style.append(("BOX", (0,0), (-1,-1), 0.6, BORDER))
    t.setStyle(TableStyle(style))
    return t

def mono_light(text):
    st = S("monol", fontName="Mono", fontSize=7.6, leading=11, textColor=colors.HexColor("#CDCCCA"))
    p = Paragraph(text.replace(" ", "&nbsp;").replace("\n", "<br/>"), st)
    t = Table([[p]], colWidths=[PAGE_W - ML - MR])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1C1B19")),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#393836")),
        ("ROUNDEDCORNERS",[4,4,4,4]),
    ]))
    return t

def callout(text, kind="warn"):
    color = AMBER if kind == "warn" else TEAL
    bgc = colors.HexColor("#FBF1E9") if kind == "warn" else colors.HexColor("#E8F1F1")
    st = S("co", fontName="DM-M", fontSize=9, leading=13, textColor=INK)
    p = Paragraph(text, st)
    t = Table([[p]], colWidths=[PAGE_W - ML - MR])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), bgc),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("LINEBEFORE",(0,0),(0,-1),3,color),
    ]))
    return t

def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(t, body), leftIndent=6) for t in items],
        bulletType="bullet", start="\u2022", bulletFontName="DM",
        bulletFontSize=8, leftIndent=14,
    )

def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceBefore=10, spaceAfter=10)

# ================= STORY =================
story = []
story.append(NextPageTemplate("main"))
story.append(PageBreak())   # cover is page 1

OHM = "\u2126"

# ---- 1. Design intent ----
story.append(Paragraph("1 &nbsp; Design Intent &amp; Architecture", h1))
story.append(Paragraph(
    "This document is written for the mechanical / industrial-design engineer who will model, "
    "prototype, and fabricate the housing for the voice emergency-checklist unit. It assumes the "
    "electronics, pin-out, and behavior are fixed and documented in the companion "
    "<font name='Mono' size='8.5'>TECH_DATA.md</font> and the wiring diagram (reproduced in &sect;9).", bodyj))
story.append(Paragraph(
    "The unit splits into <b>two physical pieces</b> joined by a short harness, because the "
    "pilot-facing controls and the processor have very different placement needs:", body))
arch = [
    ["Piece", "Contents", "Where it lives", "Why"],
    ["<b>A. Panel bezel</b><br/>(pilot-facing)",
     "Split-legend annunciator switch, PTT button (optional)",
     "Front instrument panel / pedestal, on the <b>DZUS rail</b>",
     "Must be seen and reached by the crew; the dark-cockpit annunciator must sit in the pilot's normal scan"],
    ["<b>B. Remote processor box</b><br/>(blind)",
     "ESP32-S3 board, isolated audio-input stage (isolation transformer + I2S codec ADC / analog tap), "
     "isolated audio-output stage (line driver/DAC + output isolation transformer \u2192 COM3-style channel), "
     "two microSD breakouts (Config Card slot 1 + Data Card slot 2), lamp-driver board, power conditioning. "
     "(INMP441 mic + MAX98357A speaker-amp: bench-test only, not installed.)",
     "Avionics bay / behind-panel shelf, blind-mounted",
     "Keeps heat, the SD slots, and wiring out of the panel; only the bezel needs panel real estate"],
]
story.append(make_table(arch, [1.25*inch, 1.95*inch, 1.6*inch, 1.9*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "A <b>single all-in-one panel box</b> is acceptable for a pure bench demo, but the two-piece "
    "split is the recommended target: it mirrors how real remote-mount avionics are installed and "
    "routes audio-panel signals (receive tap + COM3 output) cleanly from the avionics bay.", body))
story.append(Spacer(1, 4))
story.append(mono_light(
    "   PANEL (crew side)                       AVIONICS BAY (blind)\n"
    " +----------------------+               +------------------------------+\n"
    " |  [VOICE CHKLST OFF]  |  bezel harness|  ESP32-S3                    |\n"
    " |  [VOICE CHKLST FALT] |<=============>|  isolated audio-IN stage     |\n"
    " |    o  PTT (optional) |  (D-sub or    |  isolated audio-OUT stage    |\n"
    " +----------------------+   circular)   |  Config Card (front access)  |\n"
    "        Piece A                         |  Data Card  (front access)   |\n"
    "                                        |  lamp-driver board           |\n"
    "                                        |  power conditioning          |\n"
    "                                        +------------------------------+\n"
    "                                                Piece B"))

# ---- 2. Piece A ----
story.append(PageBreak())
story.append(Paragraph("2 &nbsp; Piece A &mdash; Panel Bezel", h1))

story.append(Paragraph("2.1 &nbsp; Form factor &amp; mounting", h3))
story.append(bullets([
    "<b>Mounting standard:</b> DZUS rail (the CJ2 pedestal and most of its panel use DZUS). "
    "Fastener pitch (hole-to-hole) = <b>3/8 in (9.525 mm)</b>; fastener clearance hole "
    "<b>0.255 in (6.48 mm)</b>.",
    "Bezel <b>height must be a whole multiple of 3/8 in</b> (the \u201cDZUS rhythm\u201d). Target a "
    "<b>3-unit panel = 1.125 in (28.575 mm)</b> tall (switch + PTT fit comfortably; no speaker/grille cutout required). "
    "4-unit = 1.5 in (38.1 mm) if additional connector cutouts are needed.",
    "Standard pedestal panel <b>width = 5.75 in (146.05 mm)</b> nominal aluminum "
    "(&asymp; 144.45 mm usable face). Use this width so the bezel drops into a standard slot.",
    "Backplate: <b>1/16 in (1.6 mm) aluminum</b> (6061-T6) per DZUS convention; first / last "
    "fastener centers <b>1.5 &times; 3/8 in = 14.29 mm</b> from each end.",
    "<b>Alternative (round-hole) mount:</b> if no DZUS slot is available, provide a variant that "
    "fits a <b>standard 3-1/8 in (79.4 mm) instrument cutout</b> with four 6-32 screws on the "
    "standard bolt circle, so it can replace a blanking plate.",
]))

story.append(Paragraph("2.2 &nbsp; Front-face layout (top &rarr; bottom, dark-cockpit order)", h3))
story.append(bullets([
    "<b>Split-legend annunciator switch</b> (Applied Avionics VIVISUN / Korry). Cutout per the "
    "<b>specific switch series' datasheet</b> \u2014 confirm the exact part before cutting. A typical "
    "VIVISUN 1-pole rectangular bezel is &asymp; <b>15 &times; 15 mm</b> to <b>19 &times; 19 mm</b> "
    "face; provide snap or screw retention per that series.",
    "Legend engraving: <b>top half = </b><font name='Mono' size='8.5'>VOICE CHKLST OFF</font><b> (white)</b>; "
    "<b>bottom half = </b><font name='Mono' size='8.5'>VOICE CHKLST FAULT</font><b> (amber)</b>. "
    "Legend orientation must read upright when panel-installed.",
    "<b>PTT button (optional)</b> \u2014 momentary, guarded or recessed so it is not bumped. If the "
    "aircraft already has a yoke / PTT tie-in, omit this and route PTT through the harness.",
    "<b>No speaker grille.</b> The installed configuration has no onboard speaker; checklist audio "
    "is delivered in-headset via the isolated COM3-style output channel. No acoustic aperture is "
    "required on the bezel for speaker output.",
]))

story.append(Paragraph("2.3 &nbsp; Bezel material &amp; finish", h3))
story.append(bullets([
    "Face: <b>6061-T6 aluminum</b>, 2.0&ndash;3.0 mm, or ABS/PC for a non-structural demo.",
    "Finish: <b>matte black, low-gloss (&le; 10 gloss units)</b> to suppress windshield glare \u2014 "
    "standard for instrument-panel parts and consistent with dark-cockpit philosophy.",
    "Engraving: laser-etched + paint-fill in white and amber to match the legend colors, OR rely "
    "solely on the switch's internal legend (preferred \u2014 fewer painted parts to chip).",
    "Edges chamfered 0.5 mm; no sharp corners facing the crew.",
]))

# ---- 3. Piece B ----
story.append(PageBreak())
story.append(Paragraph("3 &nbsp; Piece B &mdash; Remote Processor Box", h1))

story.append(Paragraph("3.1 &nbsp; Size &amp; internal layout", h3))
story.append(bullets([
    "Size the internal volume around the <b>largest board path = the ESP32-S3 DevKitC-1 "
    "(&asymp; 70 &times; 26 mm)</b> plus the isolated audio-output stage board (line driver/DAC + "
    "output isolation transformer), the audio-input stage board (isolation transformer + codec), "
    "two microSD breakouts (Config Card slot 1 + Data Card slot 2), and the 2-channel lamp-driver board. "
    "Practical outer envelope: <b>&asymp; 110 &times; 80 &times; 45 mm (L &times; W &times; H)</b>. "
    "Confirm against the actual stacked board set.",
    "Use <b>internal standoffs / PCB rails</b> (M2.5 brass inserts) so boards are screwed down, not "
    "floating \u2014 important for the vibration environment (&sect;6).",
    "The installed audio input is the <b>audio-panel tap</b> (isolated analog line tap or buffered "
    "digital I2S), not an onboard microphone. No acoustic port is needed on the remote box for "
    "the installed configuration. The audio-panel tap takes already-mixed crew audio from the panel, "
    "eliminating sensitivity to cockpit fan or avionics noise entirely.",
    "<b>No onboard speaker or speaker grille</b> in the installed build. The output goes out through "
    "the isolated line-level stage to the panel's COM3-style channel; the crew hears checklist audio "
    "in-headset, not from a speaker in the box.",
]))

story.append(Paragraph("3.2 &nbsp; Access &amp; connectors", h3))
story.append(bullets([
    "<b>microSD access \u2014 two front-accessible slots:</b> both the <b>Config Card (slot 1)</b> and "
    "<b>Data Card (slot 2)</b> must be externally accessible (push-push carriers or slots on a "
    "removable face) so either card can be swapped without opening the sealed box. "
    "Label: <font name='Mono' size='8.5'>CONFIG CARD (SLOT 1) &mdash; FAT32</font> and "
    "<font name='Mono' size='8.5'>DATA CARD (SLOT 2) &mdash; FAT32</font>.",
    "<b>USB-C service port:</b> a covered / recessed USB-C pass-through for flashing and power on the "
    "bench. Add a silicone plug or hinged cover; it is not for in-service use.",
    "<b>Main connector (bezel harness):</b> one circular bayonet connector (e.g. a small MIL-style / M12) "
    "OR a D-sub carrying: bezel switch SELECT, the two legend-lamp drives, PTT, and power / ground. "
    "Pin-out to be finalized from <font name='Mono' size='8.5'>board_pins.h</font>. "
    "Use a keyed, positive-latching connector \u2014 no loose flying leads.",
    "<b>AUDIO IN connector (isolated input tap):</b> a separate panel connector / feedthrough for the "
    "galvanically-isolated receive-only audio-panel INPUT tap line (600 \u2126 line level or buffered I2S). "
    "Label: <font name='Mono' size='8.5'>AUDIO IN &mdash; PANEL TAP (ISOLATED)</font>.",
    "<b>AUDIO OUT connector (isolated COM3 output):</b> a separate panel connector / feedthrough for "
    "the galvanically-isolated line-level OUTPUT to the dedicated COM3-style audio-panel channel. "
    "Label: <font name='Mono' size='8.5'>AUDIO OUT &mdash; COM3 ISOLATED</font>. "
    "Separate connector from the input tap; keep the TX and RX paths on distinct connectors.",
    "<b>Power:</b> accept bench supply (USB 5 V &ge; 1 A). If a 28 VDC aircraft-bus mock-up is wanted, "
    "include a <b>28 V &rarr; 5 V DC-DC</b> (&ge; 2 A) inside the box with input transient protection "
    "(TVS + fuse) \u2014 but mark clearly that this is a demo regulator, not DO-160 qualified.",
]))

story.append(Paragraph("3.3 &nbsp; Box material &amp; EMI", h3))
story.append(bullets([
    "Material: <b>aluminum (extruded or machined)</b> preferred for the remote box \u2014 it doubles as "
    "an EMI shield and a heatsink. ABS/PC acceptable for a pure desk demo.",
    "If plastic, add a <b>conductive shield liner or coating</b> (nickel paint) tied to ground, since "
    "the unit sits near sensitive avionics; good practice even for a mock-up.",
    "Single-point <b>chassis ground stud</b> bonded to the connector shell and the ESP32 ground.",
]))

# ---- 4. Audio (panel connectors) ----
story.append(Paragraph("4 &nbsp; Audio Interface &mdash; Isolated Panel Connectors", h1))
story.append(Paragraph(
    "The installed configuration has <b>no onboard speaker and no speaker grille</b>. "
    "Checklist audio is delivered in-headset via two electrically separate, galvanically-isolated "
    "audio-panel connections on two dedicated external connectors (see \u00a73.2):", body))
story.append(bullets([
    "<b>AUDIO IN \u2014 PANEL TAP (ISOLATED):</b> galvanically-isolated receive-only tap of the aircraft "
    "audio panel (analog isolated line tap via 600 \u2126:600 \u2126 aviation isolation transformer, e.g. "
    "Allen Avionics AGL series, OR buffered receive-only digital I2S, selectable per install). "
    "No signal path back toward the panel from this connector. "
    "Use a shielded audio cable; keep the run to the panel short and away from ignition wiring.",
    "<b>AUDIO OUT \u2014 COM3 ISOLATED:</b> galvanically-isolated line-level TX to the dedicated "
    f"COM3-style audio-panel input channel. Output impedance: 600 {OHM} nominal (per panel COM3 input spec). "
    "The isolation transformer on the TX line is the primary galvanic barrier; a device fault cannot "
    "key, jam, load, or back-feed the panel\u2019s other channels or required COM radios. "
    "Use shielded cable; confirm output level is set conservatively so COM3 advisory audio "
    "cannot mask required ATC audio on other channels.",
    "<b>No acoustic grille needed on either the bezel or the box</b> for the installed configuration. "
    "Remove grille-pattern cutouts from the CAD model; plug any bench-prototype holes cleanly.",
]))

# ---- 5. Thermal ----
story.append(Paragraph("5 &nbsp; Thermal", h1))
story.append(bullets([
    "The ESP32-S3 running ESP-SR is the main heat source but is <b>low power</b> (a few hundred mW "
    "typical); <b>no fan is required</b>.",
    "Provide <b>passive convection</b>: a few vent slots low and high on the remote box, or bond the "
    "ESP module's ground plane to the aluminum wall with a thermal pad.",
    "<b>Do not seal the box fully airtight if relying on convection.</b> If sealing is required for "
    "dust / water, switch to conduction cooling (thermal pad to the aluminum case) and verify the "
    "internal rise stays &lt; 20 &deg;C above ambient at 55 &deg;C ambient.",
    "Keep the DC-DC (if fitted) on its own thermal path; it is the second heat source.",
]))

# ---- 6. Environmental ----
story.append(PageBreak())
story.append(Paragraph("6 &nbsp; Environmental Targets", h1))
story.append(Paragraph(
    "DO-160G categories a real unit in this location would target. For the prototype, treat these as "
    "<b>design guidance</b>, not test obligations.", body))
env = [
    ["DO-160G section", "Category to design toward", "Note for this unit"],
    ["&sect;4 Temperature / Altitude", "Cat <b>A2</b> (controlled cockpit)", "\u221215 \u00b0C to +55 \u00b0C operating; pressurized cabin"],
    ["&sect;7 Shock &amp; crash safety", "Operational shock + crash-safety", "Mounts / standoffs must retain boards; nothing becomes a projectile"],
    ["&sect;8 Vibration", "Cat <b>S</b> (fixed-wing)", "Locking hardware; conformal-coat the boards; no press-fit-only parts"],
    ["&sect;6 Humidity", "Cat <b>A</b>", "48-hr; conformal coat recommended"],
    ["&sect;16/17 Power input / spike", "&mdash;", "Add TVS + fuse on any 28 V input mock-up"],
    ["&sect;20/21 RF emission / susceptibility", "&mdash;", "Aluminum case + grounded shield; Wi-Fi stays disabled (it is, in firmware)"],
    ["&sect;25 ESD", "&mdash;", "Bond exposed metal; recessed connectors"],
    ["&sect;26 Flammability", "&mdash;", "Use flame-rated plastics (UL94 V-0) if not aluminum"],
]
story.append(make_table(env, [1.85*inch, 2.0*inch, 2.85*inch]))
story.append(Spacer(1, 8))
story.append(callout(
    "The firmware already runs fully offline with Wi-Fi and Bluetooth off, which materially helps the "
    "RF-emission story for any future qualification.", "info"))

# ---- 7. Labeling ----
story.append(Paragraph("7 &nbsp; Labeling &amp; Markings", h1))
story.append(bullets([
    "<b>Required placard on the bezel and the box:</b> "
    "<font name='Mono' size='8.5'>DEMO / TRAINING ONLY &mdash; NOT FOR FLIGHT</font>.",
    "Box exterior: unit name, a serial / asset field, the config-card format "
    "(<font name='Mono' size='8.5'>FAT32</font>), and the USB service-port \u201cbench use only\u201d note.",
    "Annunciator legends: <font name='Mono' size='8.5'>VOICE CHKLST OFF</font> (white, top), "
    "<font name='Mono' size='8.5'>VOICE CHKLST FAULT</font> (amber, bottom).",
    "Use <b>amber for caution</b> / <b>white for status</b>, consistent with FAA AC 25-11B color "
    "conventions used elsewhere in this project.",
]))

# ---- 8. Deliverables + Open items ----
story.append(Paragraph("8 &nbsp; Deliverables Requested from the Engineer", h1))
story.append(ListFlowable([
    ListItem(Paragraph("<b>3D CAD</b> (STEP + native) of both pieces, with the board set and switch modeled in place.", body), leftIndent=6),
    ListItem(Paragraph("<b>2D drawings</b> with the DZUS hole pattern, the switch cutout (dimensioned from the chosen switch datasheet), AUDIO IN / AUDIO OUT connector cutouts, and any remaining panel apertures \u2014 fully dimensioned, GD&amp;T where it matters (switch cutout, DZUS holes). No speaker-grille pattern required.", body), leftIndent=6),
    ListItem(Paragraph("<b>Connector pin-out</b> mapping the bezel-to-box harness to <font name='Mono' size='8.5'>board_pins.h</font> signals.", body), leftIndent=6),
    ListItem(Paragraph("A <b>bench-printable prototype</b> (FDM/SLA) of both pieces for fit-check before any aluminum.", body), leftIndent=6),
    ListItem(Paragraph("<b>Mechanical BOM</b> (fasteners, inserts, connectors, AUDIO IN / AUDIO OUT panel feedthroughs, gaskets, conformal-coat).", body), leftIndent=6),
    ListItem(Paragraph("Tolerance call-outs: switch cutout &plusmn;0.1 mm; DZUS holes &plusmn;0.1 mm on the 9.525 mm pitch; general &plusmn;0.25 mm.", body), leftIndent=6),
], bulletType="1", leftIndent=18))

story.append(Paragraph("8.1 &nbsp; Open items for the engineer to confirm", h3))
story.append(callout(
    "<b>The single most critical unknown is the exact Applied Avionics switch part number</b> \u2014 it "
    "drives the bezel cutout and depth. Nothing else can be finalized until it is fixed.", "warn"))
story.append(Spacer(1, 4))
story.append(bullets([
    "<b>Mounting reality in the target panel:</b> is there a free DZUS slot, or must this go into a "
    "3-1/8 in round hole or a custom sub-panel? Pick the &sect;2.1 variant accordingly.",
    "<b>Audio-panel connection type:</b> confirm whether the install uses the analog isolated line tap "
    "or the buffered digital I2S path \u2014 this drives the audio-input stage BOM and the AUDIO IN "
    "connector pin-out. The Config Card sets the active source.",
    "<b>COM3 channel input impedance</b> \u2014 confirm the panel's COM3-style input spec so the "
    "isolated output stage (line driver + transformer) can be matched to the correct output level "
    "and impedance (typically 600 \u2126).",
    "<b>Whether a 28 V input</b> is wanted, or USB 5 V bench power is sufficient for the demo.",
]))

# ---- 9. Reference dims + diagram ----
story.append(PageBreak())
story.append(Paragraph("9 &nbsp; Reference Dimensions &amp; Wiring Context", h1))
dims = [
    ["Item", "Value", "Source"],
    ["DZUS fastener pitch", "3/8 in = <b>9.525 mm</b>", "DZUS rail standard"],
    ["DZUS clearance hole", "0.255 in = <b>6.48 mm</b>", "DZUS rail standard"],
    ["Panel backplate thickness", "1/16 in = <b>1.6 mm</b>", "DZUS convention"],
    ["First fastener offset from edge", "1.5 &times; pitch = <b>14.29 mm</b>", "DZUS convention"],
    ["Standard pedestal panel width", "<b>&asymp; 146 mm</b> alu (144.45 mm face)", "DZUS panel convention"],
    ["Standard round instrument hole", "3-1/8 in = <b>79.4 mm</b>", "Instrument panel standard"],
    ["Remote box target envelope", "<b>&asymp; 110 &times; 80 &times; 45 mm</b>", "This design (confirm vs. boards)"],
    ["Audio IN connector", "600 \u2126 line level (isolated) or buffered I2S", "TECH_DATA.md \u00a7D.3.1 / D.3.2"],
    ["Audio OUT connector (COM3)", f"600 {OHM} line-level output (isolated, via transformer)", "TECH_DATA.md \u00a7D.3.3a"],
]
story.append(make_table(dims, [2.25*inch, 2.55*inch, 1.9*inch]))
story.append(Spacer(1, 12))
story.append(Paragraph(
    "The harness between Piece A and Piece B carries the signals shown below. The full electrical "
    "reference (pin map, per-device wiring, lamp driver) is in the companion technical packet.", small))
story.append(Spacer(1, 6))
# embed wiring diagram scaled to content width
if os.path.exists(DIAGRAM):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(DIAGRAM).size
    avail_w = PAGE_W - ML - MR
    disp_w = avail_w
    disp_h = ih * (disp_w / iw)
    max_h = 4.6 * inch
    if disp_h > max_h:
        disp_h = max_h
        disp_w = iw * (disp_h / ih)
    img = Image(DIAGRAM, width=disp_w, height=disp_h)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Paragraph("System wiring diagram (from the companion technical packet).", cap))

# ---- 10. Sources ----
story.append(PageBreak())
story.append(Paragraph("10 &nbsp; Source References", h1))
sources = [
    ("DZUS rail dimensions & the \u201cDZUS rhythm\u201d", "MyCockpit panel-building guide",
     "https://www.mycockpit.org/tutorials/Panelbuildingfocussedondimensions.pdf"),
    ("DZUS rail product reference", "Dallas Avionics",
     "https://www.dallasavionics.com/cgi-bin/products.cgi?master=install&category=rail&man=dzus_rail&url=359.html"),
    ("Standard 3-1/8 in instrument cutout / adapter", "Aircraft Spruce",
     "https://www.aircraftspruce.com/catalog/inpages/instradaptkit.php"),
    ("DO-160G environmental categories (summary)", "Wikipedia",
     "https://en.wikipedia.org/wiki/DO-160"),
    ("Environmental qualification guidance", "FAA AC 21-16G",
     "https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1019280"),
    ("Annunciator color / dark-cockpit conventions", "FAA AC 25-11B",
     "https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf"),
    ("LED lighted pushbutton / split-legend switches", "Applied Avionics (VIVISUN)",
     "https://www.appliedavionics.com/led-lighted-pushbutton-switches.html"),
]
src_rows = [["#", "Reference", "Source"]]
for i, (title, pub, url) in enumerate(sources, 1):
    src_rows.append([str(i), title, Paragraph(A(pub, url), cell)])
fss = {(i,0): cellb for i in range(1, len(src_rows))}
story.append(make_table(src_rows, [0.4*inch, 3.85*inch, 2.45*inch], font_styles=fss))
story.append(Spacer(1, 16))
story.append(callout(
    "DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS. This enclosure is for a bench / "
    "training prototype. It is not a certified avionics installation and is not an STC, TSO, or "
    "field-approval package. Any installation in or near an actual aircraft requires a licensed "
    "A&amp;P/IA and the appropriate FAA approval. Repository: "
    "github.com/flas-tech/cj2-voice-emergency-checklist (MIT License).", "warn"))

# ================= PAGE TEMPLATES =================
TITLE = "CJ2 Voice Emergency Checklist"

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(HEADER_BG)
    canvas.rect(0, PAGE_H - 3.1*inch, PAGE_W, 3.1*inch, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 3.18*inch, PAGE_W, 0.08*inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#BCE2E7"))
    canvas.setFont("DM-M", 11)
    canvas.drawString(ML, PAGE_H - 1.15*inch, "MECHANICAL ENCLOSURE SPECIFICATION  \u00b7  FOR THE FABRICATING ENGINEER")
    canvas.setFillColor(colors.white)
    canvas.setFont("DM-B", 33)
    canvas.drawString(ML, PAGE_H - 1.95*inch, "Enclosure")
    canvas.drawString(ML, PAGE_H - 2.45*inch, "Specification")
    canvas.setFont("DM-M", 15)
    canvas.setFillColor(colors.HexColor("#BCE2E7"))
    canvas.drawString(ML, PAGE_H - 2.85*inch, "CJ2 Voice Emergency Checklist Unit")
    canvas.setFillColor(INK)
    canvas.setFont("DM", 11)
    y = PAGE_H - 3.9*inch
    lines = [
        "Cessna Citation CJ2 (CE 525A)  \u2014  bench / training prototype",
        "Two-piece housing: DZUS-rail panel bezel + remote processor box",
        "Mounting, materials, audio, thermal, environmental targets,",
        "labeling, deliverables, and reference dimensions.",
    ]
    for ln in lines:
        canvas.drawString(ML, y, ln); y -= 0.28*inch
    canvas.setFillColor(colors.HexColor("#FBF1E9"))
    canvas.roundRect(ML, 2.05*inch, PAGE_W - ML - MR, 0.95*inch, 6, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.rect(ML, 2.05*inch, 0.05*inch, 0.95*inch, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.setFont("DM-B", 11.5)
    canvas.drawString(ML + 0.25*inch, 2.68*inch, "DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS")
    canvas.setFillColor(INK)
    canvas.setFont("DM", 8.8)
    canvas.drawString(ML + 0.25*inch, 2.42*inch, "Not a certified avionics installation. Borrows airworthiness conventions (DZUS, DO-160) so the prototype fits and")
    canvas.drawString(ML + 0.25*inch, 2.24*inch, "looks right, but it is a mock-up. Real installation requires a licensed A&P/IA and FAA approval (337/STC/TSO).")
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(0.6)
    canvas.line(ML, 1.5*inch, PAGE_W - MR, 1.5*inch)
    canvas.setFillColor(MUTED); canvas.setFont("DM", 9)
    canvas.drawString(ML, 1.25*inch, "Repository:  github.com/flas-tech/cj2-voice-emergency-checklist")
    canvas.drawString(ML, 1.05*inch, "Generated June 10, 2026  \u00b7  Perplexity Computer")
    canvas.restoreState()

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DM", 7.5); canvas.setFillColor(FAINT)
    canvas.drawString(ML, PAGE_H - 0.55*inch, TITLE + "  \u00b7  Enclosure Specification")
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(0.5)
    canvas.line(ML, PAGE_H - 0.65*inch, PAGE_W - MR, PAGE_H - 0.65*inch)
    canvas.line(ML, 0.62*inch, PAGE_W - MR, 0.62*inch)
    canvas.setFillColor(FAINT); canvas.setFont("DM", 7.5)
    canvas.drawString(ML, 0.45*inch, "DEMO / TRAINING ONLY \u2014 NOT FOR FLIGHT")
    canvas.drawRightString(PAGE_W - MR, 0.45*inch, f"Page {doc.page}")
    canvas.restoreState()

frame_main = Frame(ML, MB, PAGE_W - ML - MR, PAGE_H - MT - MB, id="main")
frame_full = Frame(0, 0, PAGE_W, PAGE_H, id="cover")

doc = BaseDocTemplate(
    OUT, pagesize=letter,
    leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    title="CJ2 Voice Emergency Checklist \u2014 Enclosure Specification",
    author="Perplexity Computer",
)
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[frame_full], onPage=draw_cover),
    PageTemplate(id="main", frames=[frame_main], onPage=header_footer),
])
doc.build(story)
print("BUILT", OUT, os.path.getsize(OUT), "bytes")
