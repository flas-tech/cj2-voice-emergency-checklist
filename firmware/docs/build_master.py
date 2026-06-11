#!/usr/bin/env python3
"""Build the Voice Emergency Checklist MASTER technical + certification PDF.

Combines the technical data packet, processor-selection note, and enclosure
spec into one aircraft-agnostic master reference, plus the NORSEE / DO-160G
certification basis. Reuses the visual language of build_enclosure.py /
build_packet.py so all documents look like a matched set.

GLYPH NOTE: DM Sans has U+2126 (ohm) and U+00B5 (micro) but NOT U+03A9.
Use \\u2126 for the ohm sign. For ListFlowable bullets use start="\\u2022"
(NOT start="circle", which renders as a "G"). Avoid Unicode subscripts.
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
OUT = os.path.join(DOCS, "Voice_Checklist_Master_Spec.pdf")
DIAGRAM = os.path.join(DOCS, "wiring_diagram.png")

# ---- fonts ----
pdfmetrics.registerFont(TTFont("DM", f"{FONTS}/DMSans-Regular-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-B", f"{FONTS}/DMSans-Bold-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-M", f"{FONTS}/DMSans-Medium-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-I", f"{FONTS}/DMSans-Italic-static.ttf"))
pdfmetrics.registerFont(TTFont("Mono", f"{FONTS}/JetBrainsMono-Regular-static.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B", f"{FONTS}/JetBrainsMono-Bold-static.ttf"))
registerFontFamily("DM", normal="DM", bold="DM-B", italic="DM-I", boldItalic="DM-B")

# ---- palette ----
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
cellmono = S("cellmono", fontName="Mono", fontSize=7.6, leading=10.5, textColor=INK)
cellhdr = S("cellhdr", fontName="DM-B", fontSize=8.3, leading=11, textColor=colors.white)
partlead = S("partlead", fontName="DM", fontSize=10, leading=15, textColor=MUTED, spaceAfter=8, alignment=TA_JUSTIFY)

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

def numbered(items):
    return ListFlowable(
        [ListItem(Paragraph(t, body), leftIndent=6) for t in items],
        bulletType="1", leftIndent=18,
    )

def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceBefore=10, spaceAfter=10)

def part_divider(letter_label, title, lead):
    """A part-opening flowable block (not a full page) styled as a teal band."""
    st_l = S("pl", fontName="DM-B", fontSize=30, leading=34, textColor=TEALD)
    st_t = S("pt", fontName="DM-M", fontSize=13, leading=17, textColor=TEAL, spaceBefore=2, spaceAfter=8)
    return [
        Paragraph(f"PART {letter_label}", S("pp", fontName="DM-B", fontSize=10, leading=12, textColor=AMBER, spaceAfter=2)),
        Paragraph(title, st_l),
        HRFlowable(width="38%", thickness=2, color=TEAL, spaceBefore=6, spaceAfter=8, hAlign="LEFT"),
        Paragraph(lead, partlead),
    ]

OHM = "\u2126"

# ================= STORY =================
story = []
story.append(NextPageTemplate("main"))
story.append(PageBreak())   # cover is page 1

# ---------- Front matter: scope + document map ----------
story.append(Paragraph("Scope &amp; Status", h1))
story.append(callout(
    "<b>DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS.</b> This document describes "
    "a bench / training prototype and a <i>certification-readiness roadmap</i>. As built, the unit "
    "is not airworthy, not certified, and must never be installed in or relied upon aboard an "
    "aircraft. Nothing here is an STC, TSO authorization, PMA, or NORSEE letter of approval. The "
    "certification sections (Part C) describe the path a productized unit <i>would</i> follow \u2014 they "
    "are a plan, not a claim of compliance.", "warn"))
story.append(Spacer(1, 10))
story.append(Paragraph(
    "The product is a generic, offline, voice-driven <b>advisory</b> emergency-checklist reader. The "
    "pilot states an emergency by name; the device reads each checklist item aloud and waits for a "
    "spoken completion word before advancing. It runs entirely on-device (no cloud, no Wi-Fi). "
    "<b>The product itself is aircraft-agnostic</b> \u2014 all aircraft-specific behavior comes from the "
    "<b>Aircraft Card</b> that is installed (Part B). The Cessna Citation CJ2 is included only as the "
    "reference example card.", bodyj))
story.append(Paragraph(
    "<b>This master reference supersedes and combines</b> the previously separate documents: the "
    "technical data packet, the processor-selection note, and the enclosure specification. Those "
    "remain in the repository for history; this is the single source of truth.", bodyj))
story.append(Spacer(1, 6))
dmap = [
    ["Part", "Contents"],
    ["<b>A &nbsp;Product</b>", "What the system is, the generic architecture, and the safety model"],
    ["<b>B &nbsp;Aircraft Card</b>", "The card-defines-everything model + the formal card specification &amp; validation"],
    ["<b>C &nbsp;Certification basis</b>", "NORSEE / DO-160G / installation path, and the deliberate DO-178C-avoidance argument"],
    ["<b>D &nbsp;Hardware reference</b>", "Pin map, per-device wiring, annunciator, lamp driver, power, BOM, processor selection"],
    ["<b>E &nbsp;Enclosure</b>", "Two-piece mechanical specification for the fabricating engineer"],
    ["<b>F &nbsp;References</b>", "All cited regulatory and component sources"],
]
story.append(make_table(dmap, [1.6*inch, 5.1*inch]))

# ================= PART A =================
story.append(PageBreak())
story += part_divider("A", "The Product",
    "A generic, offline, advisory checklist reader. This part defines what the system is "
    "(and is not), its block-level architecture, and the three safety rules that the entire "
    "certification argument in Part C is built on.")

story.append(Paragraph("A.1 &nbsp; What it is (and is not)", h2))
isnot = [
    ["It <b>is</b>", "It <b>is not</b>"],
    ["An <b>advisory</b> read-aloud reader of checklist items", "A required or primary aircraft system"],
    ["<b>Independent</b> \u2014 no electrical/data tie to any aircraft system", "An interface to avionics, engines, or controls"],
    ["Driven entirely by an installed <b>Aircraft Card</b>", "Tied to one airframe in firmware"],
    ["<b>Offline</b>, deterministic, single-chip", "A cloud / connected / large-vocabulary STT device"],
    ["A <b>complement</b> to the certified/required checklist", "A substitute for the AFM/QRH or required checklist"],
]
story.append(make_table(isnot, [3.35*inch, 3.35*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "This framing is not cosmetic \u2014 it is the foundation of the certification argument in Part C. A "
    "device that is non-required, advisory-only, independent of primary systems, and fails to a "
    "clearly-annunciated safe state is the textbook profile for the <b>NORSEE</b> (Non-Required Safety "
    "Enhancing Equipment) approval path, and it is what lets the program lean on DO-160G environmental "
    "qualification while avoiding DO-178C software assurance.", bodyj))

story.append(Paragraph("A.2 &nbsp; Generic system architecture", h2))
arch = [
    ["Block", "Function", "Aircraft-specific?"],
    ["<b>MCU + speech stack</b>", "Wake word &rarr; command recognition &rarr; playback sequencing", "No \u2014 fixed firmware"],
    ["<b>Microphone (I2S)</b>", "Captures crew speech for recognition", "No"],
    ["<b>Speaker + amplifier (I2S)</b>", "Reads checklist items / annunciations aloud", "No"],
    ["<b>microSD (the Aircraft Card)</b>", "Carries aircraft ID, checklist library, audio, config, validation", "<b>Yes \u2014 the only aircraft-specific element</b>"],
    ["<b>Annunciator switch</b>", "Dark-cockpit status / fault indication, IN/OUT select", "No"],
]
story.append(make_table(arch, [1.7*inch, 3.4*inch, 1.6*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "The MCU runs Espressif <b>ESP-SR</b> (AFE noise-suppression/VAD &rarr; WakeNet wake word &rarr; "
    "MultiNet fixed-grammar command recognition). The grammar (trigger phrases, advance words) is small "
    "and bounded, which is what keeps an MCU-class part in scope (see D.7).", body))

story.append(Paragraph("A.3 &nbsp; The safety model (carried into the cert argument)", h2))
story.append(Paragraph(
    "Three design rules define the failure behavior, and each one maps to a NORSEE requirement (Part C):", body))
story.append(numbered([
    "<b>Revert-to-unopened.</b> If the card is missing, unreadable, malformed, fails schema validation, "
    "or any referenced audio clip is absent, the device <b>refuses to present any checklist</b> and enters "
    "a clearly-annunciated FAULT state. It never shows partial or stale data. <i>(Failure mode = loss of "
    "function, not misleading information.)</i>",
    "<b>Dark-cockpit annunciation.</b> When selected IN and healthy, the unit shows <b>nothing</b>. A fault "
    "lights the amber FAULT legend. Selected OUT shows the white OFF status and <b>inhibits</b> the fault "
    "legend (a deliberately deselected system needs no crew action). A power-up lamp test proves the legend "
    "is alive.",
    "<b>Independence.</b> The device draws power and nothing else from the aircraft; it neither reads from "
    "nor writes to any aircraft system. Loss of the device cannot affect any primary function.",
]))

# ================= PART B =================
story.append(PageBreak())
story += part_divider("B", "The Aircraft Card",
    "Card defines everything. The product is generic; the installed microSD card makes it a specific "
    "aircraft's checklist reader. This part is the formal card specification \u2014 layout, manifest schema, "
    "voice-grammar rules, and the validation logic that implements revert-to-unopened.")

story.append(Paragraph("B.1 &nbsp; Principle", h2))
story.append(callout(
    "<b>The product is generic. The installed card makes it a specific aircraft's checklist reader.</b> "
    "To support a new airframe \u2014 King Air, PC-12, TBM, another Citation \u2014 you author a new card. "
    "<b>No firmware change, no recompile, no hardware change.</b>", "info"))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Everything that varies by aircraft lives on the card: the aircraft identity, the checklist library "
    "(titles, trigger phrases, ordered items, per-item completion/advance words), the read-aloud audio, "
    "and the universal advance vocabulary. The firmware contains only the generic engine that loads, "
    "validates, and plays whatever a valid card provides.", bodyj))

story.append(Paragraph("B.2 &nbsp; Card layout (microSD, FAT32)", h2))
story.append(mono_light(
    "/sdcard/\n"
    "  config.txt                 (optional) one line: AIRCRAFT=<FOLDER>\n"
    "  <FOLDER>/                  one folder per aircraft (e.g. CJ2, B200, PC12)\n"
    "    checklists.json          the card manifest + checklist library\n"
    "    audio/\n"
    "      <clip>.wav             one read-aloud clip per referenced item + fault clips"))
story.append(Spacer(1, 8))
story.append(bullets([
    "<b>Auto-select:</b> if exactly one aircraft folder is present, it loads automatically.",
    "<b>Explicit select:</b> if multiple folders exist, <font name='Mono' size='8.5'>config.txt</font> "
    "names the active one. A missing/invalid target is a fault (revert-to-unopened), not a silent guess.",
]))

story.append(Paragraph("B.3 &nbsp; Card manifest schema (checklists.json)", h2))
story.append(Paragraph("Top-level object:", body))
top = [
    ["Field", "Type", "Req.", "Meaning"],
    ["<font name='Mono' size='8'>schema_version</font>", "integer", "rec.", "Card schema version the firmware validates against"],
    ["<font name='Mono' size='8'>aircraft</font>", "string", "<b>yes</b>", "Short aircraft id; must match the folder name"],
    ["<font name='Mono' size='8'>title</font>", "string", "<b>yes</b>", "Human-readable aircraft name shown in logs"],
    ["<font name='Mono' size='8'>universal_advance</font>", "string[]", "<b>yes</b>", "Advance words accepted on every item (e.g. check, checked, complete, next)"],
    ["<font name='Mono' size='8'>checklists</font>", "object[]", "<b>yes</b>", "The checklist library (&ge; 1)"],
]
story.append(make_table(top, [1.55*inch, 0.85*inch, 0.6*inch, 3.7*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph("Each <font name='Mono' size='8.5'>checklists[]</font> entry:", body))
clt = [
    ["Field", "Type", "Req.", "Meaning"],
    ["<font name='Mono' size='8'>id</font>", "string", "<b>yes</b>", "Stable identifier (e.g. <font name='Mono' size='8'>engine_fire</font>)"],
    ["<font name='Mono' size='8'>title</font>", "string", "<b>yes</b>", "Spoken/displayed checklist name"],
    ["<font name='Mono' size='8'>type</font>", "string", "rec.", "<font name='Mono' size='8'>emergency</font>, <font name='Mono' size='8'>abnormal</font>, <font name='Mono' size='8'>normal</font>"],
    ["<font name='Mono' size='8'>triggers</font>", "string[]", "<b>yes</b>", "Phrases that invoke this checklist by voice"],
    ["<font name='Mono' size='8'>items</font>", "object[]", "<b>yes</b>", "Ordered checklist steps (&ge; 1)"],
]
story.append(make_table(clt, [1.55*inch, 0.85*inch, 0.6*inch, 3.7*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph("Each <font name='Mono' size='8.5'>items[]</font> entry:", body))
itt = [
    ["Field", "Type", "Req.", "Meaning"],
    ["<font name='Mono' size='8'>clip</font>", "string", "<b>yes</b>", "Audio basename in <font name='Mono' size='8'>audio/</font> (read-aloud <font name='Mono' size='8'>&lt;clip&gt;.wav</font>)"],
    ["<font name='Mono' size='8'>text</font>", "string", "<b>yes</b>", "The item text (for logs / optional display)"],
    ["<font name='Mono' size='8'>advance</font>", "string[]", "opt.", "Item-specific completion words (in addition to <font name='Mono' size='8'>universal_advance</font>)"],
]
story.append(make_table(itt, [1.55*inch, 0.85*inch, 0.6*inch, 3.7*inch]))

story.append(Paragraph("B.3.1 &nbsp; Voice-grammar rules (validation-enforced)", h3))
story.append(Paragraph(
    "MultiNet (English) imposes grammar constraints that the card author <b>must</b> honor; the validator "
    "rejects a card that violates them (revert-to-unopened):", body))
story.append(bullets([
    "Phrases are <b>lowercase letters and single spaces only</b> \u2014 no digits or punctuation.",
    "<b>Spell numbers as words</b>: \u201cV-one\u201d &rarr; <font name='Mono' size='8.5'>v one</font>, not <font name='Mono' size='8.5'>V1</font>.",
    "Keep the <b>total command count modest</b> (well under the ~200-command MultiNet cap).",
    "Every <font name='Mono' size='8.5'>clip</font> referenced by any item <b>must</b> exist as "
    "<font name='Mono' size='8.5'>audio/&lt;clip&gt;.wav</font>.",
]))

story.append(PageBreak())
story.append(Paragraph("B.4 &nbsp; Card validation &amp; the revert-to-unopened rule", h2))
story.append(Paragraph(
    "On boot the firmware attempts a <b>complete, valid</b> load and returns exactly one status:", body))
val = [
    ["Status", "Meaning", "Annunciation"],
    ["<font name='Mono' size='8'>STORE_OK</font>", "SD mounted, JSON parsed + schema-valid, <b>every</b> audio clip present", "dark (healthy)"],
    ["<font name='Mono' size='8'>FAULT_NO_CARD</font>", "SD not detected / mount failed", "amber FAULT"],
    ["<font name='Mono' size='8'>FAULT_NO_AIRCRAFT</font>", "No aircraft folder, or <font name='Mono' size='8'>config.txt</font> target missing", "amber FAULT"],
    ["<font name='Mono' size='8'>FAULT_NO_JSON</font>", "<font name='Mono' size='8'>checklists.json</font> missing / unreadable", "amber FAULT"],
    ["<font name='Mono' size='8'>FAULT_PARSE</font>", "JSON malformed", "amber FAULT"],
    ["<font name='Mono' size='8'>FAULT_VALIDATION</font>", "Schema or voice-rule violation, empty data", "amber FAULT"],
    ["<font name='Mono' size='8'>FAULT_AUDIO_MISSING</font>", "A referenced clip is absent", "amber FAULT"],
    ["<font name='Mono' size='8'>FAULT_NO_MEMORY</font>", "Allocation failed while loading", "amber FAULT"],
]
story.append(make_table(val, [1.85*inch, 3.5*inch, 1.35*inch]))
story.append(Spacer(1, 8))
story.append(callout(
    "<b>On any FAULT the in-memory checklist table is left EMPTY</b> \u2014 the device cannot present a partial "
    "or stale checklist even if asked. This is the literal implementation of \u201calways revert to unopened "
    "if files are not available.\u201d", "warn"))

story.append(Paragraph("B.5 &nbsp; Card integrity &amp; provenance (recommended for a productized card)", h2))
story.append(Paragraph(
    "For a card that drives a <i>safety-enhancing</i> device, integrity matters as much as schema validity. "
    "Recommended additions (forward-looking, beyond the current demo):", body))
story.append(bullets([
    "<b>Schema version gate</b> \u2014 firmware refuses a card whose <font name='Mono' size='8.5'>schema_version</font> "
    "it does not support, rather than mis-parsing it.",
    "<b>Manifest checksum / signature</b> \u2014 a per-card hash (and, for production, a signature) so a corrupted "
    "or tampered card is rejected as <font name='Mono' size='8.5'>FAULT_VALIDATION</font>.",
    "<b>Content provenance</b> \u2014 record, per card, the AFM/QRH source revision the checklist text was "
    "transcribed from, the author, and the date. Advisory equipment is only as good as the source it "
    "mirrors; provenance is part of the configuration-control story the FAA expects under NORSEE (Part C).",
    "<b>Read-only media</b> \u2014 distribute production cards write-protected.",
]))

# ================= PART C =================
story.append(PageBreak())
story += part_divider("C", "Certification Basis",
    "STC / PMA / NORSEE-ready reference. This part is a roadmap, not evidence of compliance \u2014 the demo "
    "unit holds no approvals. It explains why NORSEE is the right path, the standards elected as Minimum "
    "Design Requirements, and the deliberate, documented argument for avoiding DO-178C.")
story.append(callout(
    "<b>Status:</b> this part is a <b>roadmap</b>, not evidence of compliance. The demo unit holds no "
    "approvals. The intent is to design and document so that a productized unit can pursue approval "
    "efficiently.", "warn"))

story.append(Paragraph("C.1 &nbsp; Why NORSEE is the right path", h2))
story.append(Paragraph(
    "The product profile \u2014 non-required, advisory, independent of primary systems, failing to a "
    "clearly-annunciated safe state \u2014 matches the FAA's <b>Non-Required Safety Enhancing Equipment "
    "(NORSEE)</b> policy, <b>PS-AIR-21.8-1602</b> (issued 03/31/2016)<super>1</super>. NORSEE approval is a "
    "<b>combined design and production approval</b> issued under <b>14 CFR &sect; 21.8(d)</b> for equipment "
    "that is \u201cnot required by any Federal regulation with the intent to measurably increase aircraft "
    "safety,\u201d determined to be a <b>minor change to type design</b> with a <b>minor failure condition</b>. "
    "A voice reader that simply reads aloud the same items already in the certified/required checklist \u2014 "
    "while the paper/electronic required checklist remains the authority \u2014 is a strong fit.", bodyj))

story.append(Paragraph("C.1.1 &nbsp; Applicability limit (read this)", h3))
story.append(Paragraph(
    "NORSEE policy <b>applies to aircraft certified under 14 CFR Part 23, 27, and 29</b> (and predecessor "
    "categories) and <b>explicitly excludes Part 25 transport-category aircraft</b><super>1</super>.", body))
story.append(bullets([
    "The reference example, the <b>Citation CJ2 (525A), is a Part 23 airplane</b> \u2014 so NORSEE is available "
    "for it.",
    "Because the product is generic, the card library will inevitably include <b>Part 25</b> aircraft (e.g. "
    "larger jets). <b>For a Part 25 installation, NORSEE is not available</b>; that installation must use an "
    "<b>STC</b> (or other major/minor-change path appropriate to the airframe). The product's certification "
    "status is therefore <b>per-airframe</b>, and the documentation must say so explicitly.",
]))

story.append(Paragraph("C.2 &nbsp; Minimum Design Requirements (the standards we elect)", h2))
story.append(Paragraph(
    "Under NORSEE the applicant <b>proposes the industry standard(s)</b> that become the Minimum Design "
    "Requirements (MDR); the FAA accepts, partially accepts, or augments them. The FAA recommends "
    "widely-accepted RTCA / SAE / ASTM standards<super>1</super>.", body))
mdr = [
    ["Topic", "Elected standard / basis", "Notes"],
    ["<b>Environmental</b>", "<b>RTCA/DO-160G</b>", "Primary qualification evidence. Categories in C.4. FAA accepts DO-160 D/E/F/G per <b>AC 21-16G</b> and \u201cstrongly encourages DO-160G for new articles.\u201d"],
    ["<b>Software</b>", "<b>No DO-178C</b> sought \u2014 see C.3", "Argued out via function/failure classification, not avoided by omission"],
    ["<b>Complex hardware</b>", "<b>DO-254 not invoked</b>", "COTS MCU + simple discrete logic; no custom complex devices (ASIC/FPGA/PLD). Per AC 20-152A, <i>simple</i> hardware verifiable by test needs no DO-254 design assurance."],
    ["<b>Human factors / color</b>", "<b>FAA AC 25-11B</b> conventions", "amber=caution, white=status, dark-cockpit. Accepted design convention even though the unit is not a Part 25 article."],
    ["<b>System safety (if needed)</b>", "<b>SAE ARP4761 / AC 23.1309-1</b>", "Only invoked if the safety evaluation ever rises above \u201cminor\u201d (it should not)"],
]
story.append(make_table(mdr, [1.45*inch, 1.85*inch, 3.4*inch]))

story.append(PageBreak())
story.append(Paragraph("C.3 &nbsp; The DO-178C-avoidance argument (deliberate, documented)", h2))
story.append(Paragraph(
    "DO-178C is software <i>design-assurance</i> guidance whose rigor scales with the <b>failure condition</b> "
    "the software can contribute to. NORSEE lets us classify the function and, for a genuinely minor-failure "
    "advisory device, <b>scope software assurance down to essentially nothing formal</b> \u2014 provided the "
    "architecture earns it. The argument has four legs:", bodyj))
story.append(numbered([
    "<b>Function is advisory, not required.</b> The device does not perform, command, or feed any required "
    "function. The crew's authority is the certified/required checklist; this unit only reads it aloud.",
    "<b>Worst-case failure is minor.</b> The two credible failures are (a) <b>loss of function</b> \u2014 it goes "
    "silent or annunciates FAULT, and the crew uses the paper/QRH exactly as today; and (b) <b>misleading "
    "information</b> \u2014 mitigated by the revert-to-unopened rule (no partial/stale output), card validation, "
    "and a procedural requirement that the crew cross-checks against the required checklist. Neither failure "
    "reduces the crew's ability to cope with a condition worse than minor \u2014 the NORSEE safety-evaluation "
    "test<super>1</super>.",
    "<b>Independence.</b> No input from or output to any primary system; physical and electrical separation. "
    "This is one of the design considerations the policy lists for keeping a failure minor<super>1</super>.",
    "<b>Qualitative safety evaluation is permitted</b> for non-complex equipment; a quantitative probabilistic "
    "analysis (and the DO-178C machinery that feeds it) is not required for a minor-failure advisory "
    "function<super>1</super>.",
]))
story.append(Spacer(1, 4))
story.append(callout(
    "<b>Honest caveats (must stay in the doc):</b> (1) This argument <b>must be agreed with the FAA ACO "
    "early</b> \u2014 the applicant proposes the classification; the FAA concurs. If the FAA judges the failure "
    "condition above minor (e.g. because of over-reliance / automation-dependency human factors), the program "
    "moves to &sect;2 of the NORSEE policy (xx.1309, ARP4754A/ARP4761) and software assurance re-enters. "
    "(2) \u201cNo DO-178C\u201d is <b>earned by architecture and procedural mitigations</b>, not by labeling. The "
    "revert-to-unopened behavior, the validation gate, the dark-cockpit annunciation, the independence, and a "
    "<b>mandatory limitation that the unit may not be used as a substitute for the required checklist</b> are "
    "the price of that classification.", "warn"))

story.append(Paragraph("C.4 &nbsp; DO-160G environmental qualification plan", h2))
story.append(Paragraph(
    "Categories a cockpit/avionics-bay unit would target. For the prototype these are <b>design targets</b>, "
    "not completed tests<super>2</super>.", body))
env = [
    ["DO-160G section", "Target category", "Rationale for this unit"],
    ["&sect;4 Temperature &amp; Altitude", "<b>Cat A2</b> (controlled/pressurized)", "\u221215 \u00b0C to +55 \u00b0C operating; pressurized cabin"],
    ["&sect;5 Temperature Variation", "Cat B", "Cockpit rate of change"],
    ["&sect;6 Humidity", "<b>Cat A</b>", "Conformal coat recommended"],
    ["&sect;7 Operational/Crash Shock", "Operational + crash-safety", "Boards retained; nothing becomes a projectile"],
    ["&sect;8 Vibration", "<b>Cat S</b> (fixed-wing)", "Locking hardware; conformal coat; no press-fit-only parts"],
    ["&sect;15 Magnetic Effect", "Class Z", "Small device; classify by measured deflection"],
    ["&sect;16 Power Input", "per installation (e.g. 28 VDC)", "Only if a 28 V variant is built; TVS + fuse"],
    ["&sect;17 Voltage Spike", "Cat A", "Input transient protection"],
    ["&sect;19 Induced Signal Susceptibility", "Cat ZC", "Cockpit"],
    ["&sect;21 RF Emission", "<b>Cat M</b> (or better)", "<b>Wi-Fi/BT disabled in firmware</b> materially helps emissions"],
    ["&sect;22 Lightning Induced Transient", "as installed", "Behind-panel mounting reduces exposure"],
    ["&sect;25 ESD", "per &sect;25", "Bond exposed metal; recessed connectors"],
    ["&sect;26 Flammability", "UL94 <b>V-0</b> materials", "Required if not aluminum"],
]
story.append(make_table(env, [2.0*inch, 1.95*inch, 2.75*inch]))
story.append(Spacer(1, 6))
story.append(callout(
    "The deliberate choice to <b>disable Wi-Fi and Bluetooth in firmware</b> is both a security decision and "
    "an emissions-qualification advantage (&sect;21).", "info"))

story.append(PageBreak())
story.append(Paragraph("C.5 &nbsp; Approval &amp; installation path (per airframe)", h2))
story.append(Paragraph(
    "NORSEE approval is <b>design + production approval \u2014 not installation approval</b>. The full chain for a "
    "Part 23/27/29 airframe:", body))
story.append(numbered([
    "<b>Pre-application</b> \u2014 engage the responsible FAA <b>ACO</b> early; agree on the NORSEE classification "
    "(minor change / minor failure) and the MDR (C.2).",
    "<b>Design + test</b> \u2014 complete DO-160G qualification, the safety evaluation, human-factors assessment, "
    "and the configuration-control / card-provenance package.",
    "<b>NORSEE Letter of Approval (LOA)</b> under <b>&sect; 21.8(d)</b>, with the <b>certifying statement of "
    "compliance</b> (template in C.6) and a quality system per the policy.",
    "<b>Installation</b> \u2014 NORSEE <i>eligibility</i> still requires an installation approval on each aircraft: "
    "if a <b>minor alteration</b>, a logbook entry / FAA Form 337 as applicable; if a <b>major change</b> to "
    "type design (panel structure, electrical integration), an <b>STC</b> or field-approval path.",
    "<b>Part 25 aircraft</b> \u2014 skip NORSEE; pursue <b>STC</b> for the installation (C.1.1).",
]))

story.append(Paragraph("C.5.1 &nbsp; Where TSO and PMA fit (and don't, here)", h3))
story.append(bullets([
    "<b>TSO authorization</b> is a <i>minimum-performance</i> design+production approval against a specific "
    "TSO. <b>There is no TSO that defines a \u201cvoice advisory checklist reader,\u201d</b> so a TSOA is not the "
    "natural path; NORSEE (applicant-proposed MDR) is. A TSOA would also still require separate installation "
    "approval<super>3</super>.",
    "<b>PMA</b> is for <i>modification/replacement</i> articles for a type-certificated product and is typically "
    "tied to an STC or identicality. This unit is <b>added</b> equipment, not a replacement part, so PMA is "
    "not the primary path \u2014 though a production unit may end up holding PMA in conjunction with an STC for "
    "specific airframes (14 CFR &sect; 21.303).",
]))

story.append(Paragraph("C.6 &nbsp; Certifying statement of compliance (template)", h2))
story.append(Paragraph(
    "Per the NORSEE policy, the LOA application carries a statement in this form (placeholders to be "
    "completed at application). <i>Reproduced as a template only \u2014 not a current certification.</i>", body))
story.append(callout(
    "\u201cI, <i>(authorized representative)</i>, certify that <i>(company)</i> has complied with all applicable "
    "requirements as identified in <i>RTCA/DO-160G and the other Minimum Design Requirements accepted for this "
    "article</i>, and policy statement <b>PS-AIR-21.8-1602</b>, and that the article is produced under the "
    "required quality system.\u201d", "info"))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Two limitation statements the FAA expects on advisory NORSEE, to be placarded / in the manual:", body))
story.append(callout(
    "\u201c<b>No operational credit may be taken for installation of this system.</b>\u201d &nbsp;&middot;&nbsp; "
    "\u201c<b>This system is not a required system and may not be used as a substitution for the certificated "
    "aircraft checklist.</b>\u201d", "warn"))

story.append(Paragraph("C.7 &nbsp; Compliance summary matrix", h2))
csm = [
    ["Requirement", "Means of compliance", "Status (demo)"],
    ["Non-required, safety-enhancing", "NORSEE PS-AIR-21.8-1602, &sect; 21.8(d)", "Argued; not applied"],
    ["Minor change / minor failure", "Qualitative safety evaluation (C.3)", "Drafted; ACO concurrence pending"],
    ["Environmental", "RTCA/DO-160G (C.4) per AC 21-16G", "Targets defined; <b>not tested</b>"],
    ["Software assurance", "<b>DO-178C not sought</b> \u2014 advisory/minor (C.3)", "Architecture supports it; ACO pending"],
    ["Complex hardware", "DO-254 not invoked (simple COTS) \u2014 AC 20-152A", "N/A by design"],
    ["Human factors / color", "AC 25-11B conventions, dark-cockpit", "Implemented in design"],
    ["Installation", "Minor alteration or STC, per airframe", "Per-aircraft; none performed"],
    ["Part 25 airframes", "STC (NORSEE excluded)", "Flagged"],
]
story.append(make_table(csm, [2.05*inch, 2.85*inch, 1.8*inch]))

# Part C footnotes
story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=2, spaceAfter=6))
fnstyle = S("fn", fontName="DM", fontSize=7.3, leading=10, textColor=MUTED)
story.append(Paragraph("<super>1</super> FAA Policy Statement PS-AIR-21.8-1602, \u201cApproval of Non-Required Safety "
    "Enhancing Equipment (NORSEE)\u201d \u2014 " + A("gajsc.org", "https://www.gajsc.org/wordpress/wp-content/uploads/2016/08/PS-AIR-21.8-1602.pdf"), fnstyle))
story.append(Paragraph("<super>2</super> RTCA/DO-160G; FAA AC 21-16G acceptance of DO-160 D\u2013G \u2014 " +
    A("faa.gov AC 21-16G", "https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1019280"), fnstyle))
story.append(Paragraph("<super>3</super> FAA Technical Standard Orders (TSO) program \u2014 " +
    A("faa.gov/aircraft/air_cert", "https://www.faa.gov/aircraft/air_cert/design_approvals/tso"), fnstyle))

# ================= PART D =================
story.append(PageBreak())
story += part_divider("D", "Hardware Reference",
    "The generic hardware platform shared by every aircraft card: MCU, pin map, per-device wiring, "
    "annunciator, lamp driver, power budget, processor selection, firmware notes, and the DIY bill of "
    "materials. Pin numbers match firmware/main/board_pins.h.")
story.append(callout(
    "Pin numbers match <font name='Mono' size='8.5'>firmware/main/board_pins.h</font>. The wiring diagram is "
    "in &sect;D.10. Logic level is <b>3.3 V</b> (the ESP32-S3 is <b>not</b> 5 V tolerant on GPIO).", "info"))

story.append(Paragraph("D.1 &nbsp; System overview", h2))
ovr = [
    ["Item", "Value"],
    ["MCU", "<b>ESP32-S3</b> (dual-core LX7 @ 240 MHz) \u2014 <b>PSRAM required</b> by ESP-SR"],
    ["Recommended module", "ESP32-S3-WROOM-1 <b>N16R8</b> (16 MB flash, 8 MB octal PSRAM)"],
    ["Speech stack", "Espressif <b>ESP-SR</b>: AFE (NS/VAD) &rarr; WakeNet \u201cHi ESP\u201d &rarr; MultiNet English"],
    ["Mic input", "I2S MEMS microphone on <b>I2S_NUM_0</b>"],
    ["Audio output", f"I2S Class-D amplifier on <b>I2S_NUM_1</b> &rarr; 4\u20138 {OHM} speaker"],
    ["Config storage", "<b>microSD</b> \u2014 the Aircraft Card (Part B), FAT32"],
    ["Annunciation", "Applied Avionics split-legend switch (dark-cockpit, AC 25-11B)"],
]
story.append(make_table(ovr, [1.6*inch, 5.1*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Two build paths: <b>Integrated</b> (ESP32-S3-Korvo-2 dev board \u2014 on-board dual mic, ES8311 codec, "
    "NS4150 amp, microSD slot; best mic performance) or <b>DIY</b> (ESP32-S3 DevKitC-1 N16R8 + INMP441 mic + "
    "MAX98357A amp + microSD breakout + the annunciator switch).", body))

story.append(Paragraph("D.2 &nbsp; Master pin map", h2))
pins = [
    ["Function", "Macro", "GPIO", "Dir", "Notes"],
    ["Push-to-talk", "<font name='Mono' size='7.5'>PTT_GPIO</font>", "0", "in (PU)", "BOOT button; active-low"],
    ["SELECT switch", "<font name='Mono' size='7.5'>SELECT_GPIO</font>", "10", "in (PU)", "IN = GPIO&rarr;GND (active-low)"],
    ["Legend OFF (white)", "<font name='Mono' size='7.5'>LEGEND_OFF_GPIO</font>", "21", "out", "top legend half (via driver)"],
    ["Legend FAULT (amber)", "<font name='Mono' size='7.5'>LEGEND_FAULT_GPIO</font>", "14", "out", "bottom legend half (via driver)"],
    ["Status LED", "<font name='Mono' size='7.5'>STATUS_LED_GPIO</font>", "48", "out", "on-board RGB on most S3 devkits"],
    ["Mic bit clock", "<font name='Mono' size='7.5'>MIC_BCLK_GPIO</font>", "4", "out", "I2S0 BCLK &rarr; mic SCK"],
    ["Mic word select", "<font name='Mono' size='7.5'>MIC_LRCLK_GPIO</font>", "5", "out", "I2S0 WS &rarr; mic WS"],
    ["Mic data in", "<font name='Mono' size='7.5'>MIC_DIN_GPIO</font>", "6", "in", "mic SD &rarr; ESP DIN"],
    ["SD clock", "<font name='Mono' size='7.5'>SD_CLK_GPIO</font>", "7", "out", "SDMMC CLK"],
    ["SD command", "<font name='Mono' size='7.5'>SD_CMD_GPIO</font>", "9", "i/o", "SDMMC CMD (needs pull-up)"],
    ["SD data 0", "<font name='Mono' size='7.5'>SD_D0_GPIO</font>", "8", "i/o", "SDMMC DAT0 (needs pull-up)"],
    ["Speaker bit clock", "<font name='Mono' size='7.5'>SPK_BCLK_GPIO</font>", "15", "out", "I2S1 BCLK &rarr; amp BCLK"],
    ["Speaker word select", "<font name='Mono' size='7.5'>SPK_LRCLK_GPIO</font>", "16", "out", "I2S1 WS &rarr; amp LRC"],
    ["Speaker data out", "<font name='Mono' size='7.5'>SPK_DOUT_GPIO</font>", "17", "out", "I2S1 DOUT &rarr; amp DIN"],
]
story.append(make_table(pins, [1.4*inch, 1.6*inch, 0.5*inch, 0.6*inch, 2.6*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Polarity macros:</b> <font name='Mono' size='8'>PTT_ACTIVE_LOW=1</font>, "
    "<font name='Mono' size='8'>SELECT_ACTIVE_LOW=1</font>, <font name='Mono' size='8'>LEGEND_OFF_ACTIVE_HIGH=1</font>, "
    "<font name='Mono' size='8'>LEGEND_FAULT_ACTIVE_HIGH=1</font>, <font name='Mono' size='8'>STATUS_LED_ACTIVE_HIGH=1</font>, "
    "<font name='Mono' size='8'>LAMP_TEST_MS=2000</font>. Set any unused output to <font name='Mono' size='8'>-1</font> "
    "to disable it cleanly.", small))
story.append(Spacer(1, 4))
story.append(callout(
    "<b>Reserved / avoid pins (N16R8):</b> GPIO33\u201337 (octal PSRAM/flash bus \u2014 do not use), GPIO19/20 "
    "(USB D-/D+), GPIO0/45/46 (strapping \u2014 must boot in the right state), GPIO26\u201332 (SPI flash on some "
    "modules). GPIO0 here is only the BOOT/PTT button, so it is safe.", "warn"))

story.append(PageBreak())
story.append(Paragraph("D.3 &nbsp; Per-device wiring", h2))
story.append(Paragraph(
    "<b>D.3.1 INMP441 MEMS mic &rarr; ESP32-S3 (I2S_NUM_0).</b> Supply 1.8\u20133.3 V (never 5 V), ~2.2\u20132.5 mA. "
    "VDD&rarr;3V3, GND&rarr;GND, SCK&rarr;GPIO4, WS&rarr;GPIO5, SD&rarr;GPIO6, L/R&rarr;GND (left channel). Decouple "
    "0.1 &micro;F; 100 k" + OHM + " pulldown on SD; never clock with VDD off.", body))
story.append(Paragraph(
    "<b>D.3.2 MAX98357A Class-D amp &rarr; ESP32-S3 (I2S_NUM_1).</b> Supply 2.5\u20135.5 V; ~2.4 mA quiescent; "
    f"peak ~650 mA at 5 V/4 {OHM}; no MCLK. VIN&rarr;5 V (full output), GND&rarr;GND, BCLK&rarr;GPIO15, "
    "LRC&rarr;GPIO16, DIN&rarr;GPIO17, GAIN NC = 9 dB, SD/mode float = mono. <b>OUT+/OUT&minus; are bridge-tied "
    "\u2014 never to GND.</b>", body))
story.append(Paragraph(
    "<b>D.3.3 microSD (the Aircraft Card) &rarr; SDMMC 1-bit.</b> 3.3 V card. CLK&rarr;GPIO7, CMD&rarr;GPIO9 "
    "(10 k" + OHM + "&rarr;3V3), DAT0&rarr;GPIO8 (10 k" + OHM + "&rarr;3V3), VDD&rarr;3V3, VSS&rarr;GND. FAT32; "
    "layout per Part B.", body))
story.append(Paragraph(
    "<b>D.3.4 Discrete inputs.</b> SELECT (GPIO10): LOW = selected IN; pull-up HIGH = OUT. PTT (GPIO0): "
    "LOW = pressed. Each is a simple SPST to GND; debounce in software.", body))

story.append(Paragraph("D.4 &nbsp; Annunciator switch (split-legend, dark-cockpit)", h2))
ann = [
    ["State", "TOP \u2014 white <b>VOICE CHKLST OFF</b>", "BOTTOM \u2014 amber <b>VOICE CHKLST FAULT</b>"],
    ["Selected <b>IN</b>, healthy", "dark", "dark &larr; true dark cockpit"],
    ["Selected <b>IN</b>, fault", "dark", "<b>amber ON</b>"],
    ["Selected <b>OUT</b>", "<b>white ON</b>", "dark (fault inhibited)"],
]
story.append(make_table(ann, [1.7*inch, 2.5*inch, 2.5*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Power-up <b>lamp test</b>: both halves on for ~2 s, then dark, so a dead LED cannot masquerade as "
    "healthy. <b>OUT inhibits fault</b> per AC 25-11B \u2014 a deselected system needs no crew action, so only "
    "the white OFF status shows; recognition and fault monitoring are suspended while OUT.", body))

story.append(Paragraph("D.5 &nbsp; Lamp-driver circuit (one per legend half)", h2))
story.append(Paragraph(
    "An ESP32 GPIO (~20 mA default, 40 mA max; 1.5 A total chip limit) <b>cannot drive a 28 V \u2014 or 5 V at "
    "lamp current \u2014 legend directly.</b> Use a low-side switch per half:", body))
story.append(mono_light(
    "            +V_lamp (5 V or 28 V, separate rail)\n"
    "                  |\n"
    "              [ legend lamp ]        <- VIVISUN legend (white or amber)\n"
    "                  |\n"
    "                  +------------------ Drain\n"
    "   GPIO21 --[1k]--|G   N-ch MOSFET (logic-level, e.g. 2N7002 / AO3400)\n"
    "   (or G14)       |    or NPN (e.g. 2N2222 with base resistor)\n"
    "              [10k]                  <- gate/base pulldown -> GND (defined OFF)\n"
    "                  |\n"
    "                 GND  (Source) ------ common ground with ESP32"))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "One driver for GPIO21 (OFF/white), one for GPIO14 (FAULT/amber). The 10 k" + OHM + " pulldown guarantees "
    "the lamp is OFF during boot/reset before the GPIO is configured (dark-cockpit integrity). For a 28 V "
    "incandescent legend, use a FET with Vds &ge; 40 V and current &ge; inrush. Applied Avionics VIVISUN/Korry "
    "legends come in 28 VDC, 5 VDC, 28 VAC, 5 VAC, and 115 V lamp variants. For a quick bench mock-up, "
    "substitute two 3.3 V LEDs (white + amber) with series resistors driven straight from GPIO21/GPIO14 "
    "within the ~20 mA limit.", body))

story.append(PageBreak())
story.append(Paragraph("D.6 &nbsp; Power budget", h2))
pwr = [
    ["Rail", "Loads", "Typical", "Peak"],
    ["<b>3.3 V</b>", "ESP32-S3 (Wi-Fi off) + mic + microSD", "~80\u2013150 mA", "~250 mA (SD init / SR burst)"],
    ["<b>5 V</b>", "MAX98357A output", "a few mA idle", f"<b>~650 mA</b> (5 V/4 {OHM}, loud)"],
    ["<b>Lamp rail</b>", "up to 2 legend halves", "0 (dark)", "per lamp spec (e.g. 28 V incand.)"],
]
story.append(make_table(pwr, [1.1*inch, 2.9*inch, 1.35*inch, 1.35*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Power from <b>USB 5 V &ge; 1 A</b>. Keep a 28 V legend supply separate from logic 5 V (grounds common "
    "only). Bulk decoupling &ge; 100 &micro;F near the amp VIN plus 0.1 &micro;F per device.", body))

story.append(Paragraph("D.7 &nbsp; Processor selection", h2))
story.append(Paragraph(
    "This is a narrow, bounded workload \u2014 a <b>small fixed vocabulary</b> (checklist triggers + universal "
    "advance words, well under the ~200-command MultiNet cap), <b>offline</b>, and <b>deterministic</b>. That "
    "is command recognition on a fixed grammar, <b>not</b> open-ended transcription, which keeps an MCU-class "
    "part firmly in scope and makes a Linux SBC overkill. It is also exactly the property that supports the "
    "minor-failure / no-DO-178C argument (C.3): a single-chip, fixed-grammar device has a small, "
    "well-understood failure surface.", bodyj))
story.append(callout(
    "<b>Recommendation:</b> keep the ESP32-S3 as the baseline; consider the ESP32-P4 only for headroom. "
    "ESP-SR (v2.1+) supports S3 and P4 for English MultiNet; the classic ESP32 is no longer supported by the "
    "current speech algorithms and should be avoided.", "info"))
story.append(Spacer(1, 6))
proc = [
    ["Option", "Summary", "Verdict"],
    ["<b>ESP32-S3</b> (baseline)", "LX7 dual-core @240 MHz + AI vector ext, 512 KB SRAM, Wi-Fi+BLE, ~$8\u201315", "Best AI/voice part in the line, most mature tooling; firmware/diagram/BOM built on it"],
    ["<b>ESP32-P4</b> (upgrade)", "RISC-V to 400 MHz + AI ext, 768 KB SRAM, ~2.5&times; compute, <b>no Wi-Fi/BT</b>", "Worth it only for more compute or a future display; no-radio is arguably a safety plus"],
    ["Syntiant NDP120", "Always-on ultra-low-power NDP", "Overkill; we have panel power, need full grammar + playback + SD"],
    ["Picovoice Porcupine+Rhino", "Offline wake+intent on Cortex-M4", "Clean fit but needs a per-deployment license key \u2014 undesirable for self-contained safety gear"],
    ["Fluent.ai / NXP i.MX RT600", "Commercial intent / heavy audio DSP", "More licensing/board complexity than a fixed grammar needs"],
    ["Raspberry Pi (whisper/Vosk)", "Full Linux STT", "Non-deterministic boot, higher power/cost \u2014 less robust for a fixed-grammar safety device"],
]
story.append(make_table(proc, [1.55*inch, 2.85*inch, 2.3*inch]))

story.append(PageBreak())
story.append(Paragraph("D.8 &nbsp; Firmware build notes", h2))
fw = [
    ["Topic", "Value"],
    ["Framework", "<b>ESP-IDF &ge; 5.2</b>"],
    ["Components", "<font name='Mono' size='8'>esp-sr</font>, <font name='Mono' size='8'>esp_spiffs</font>, <font name='Mono' size='8'>driver</font>, <font name='Mono' size='8'>json</font> (cJSON), <font name='Mono' size='8'>fatfs</font>, <font name='Mono' size='8'>sdmmc</font>, <font name='Mono' size='8'>esp_driver_sdmmc</font>"],
    ["Speech models", "WakeNet <font name='Mono' size='8'>WN9_HIESP</font>; MultiNet English <font name='Mono' size='8'>mn6_en</font>/<font name='Mono' size='8'>mn7_en</font> (S3 only)"],
    ["Partitions", "factory app 3 MB + model 5 MB + storage 2 MB &rarr; needs <b>16 MB</b> flash (N16R8)"],
    ["Grammar rules", "lowercase + single spaces; spell numbers (\u201cv one\u201d); ~200-cmd cap"],
    ["Fault behavior", "any card fault &rarr; <font name='Mono' size='8'>ST_FAULT</font>, amber legend, <b>no checklist shown</b>"],
]
story.append(make_table(fw, [1.5*inch, 5.2*inch]))

story.append(Paragraph("D.9 &nbsp; Bill of materials (DIY build)", h2))
bom = [
    ["Qty", "Part", "Spec / example"],
    ["1", "ESP32-S3 DevKit", "DevKitC-1 <b>N16R8</b> (PSRAM)"],
    ["1", "I2S MEMS mic", "<b>INMP441</b> / ICS-43434 breakout"],
    ["1", "I2S amp", "<b>MAX98357A</b> breakout"],
    ["1", "Speaker", f"4\u20138 {OHM}, &ge; 2 W"],
    ["1", "microSD card + breakout", "FAT32 (the Aircraft Card)"],
    ["1", "Annunciator switch", "Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench)"],
    ["2", "Lamp driver", "logic-level N-MOSFET (2N7002/AO3400) or NPN (2N2222)"],
    ["4", "Resistors", f"1 k{OHM} &times;2 (gate), 10 k{OHM} &times;2 (pulldown)"],
    ["2\u20133", "Pull-ups", f"10 k{OHM} on SD CMD/DAT0 (if breakout lacks them)"],
    ["\u2014", "Caps", "0.1 &micro;F per device, 100 &micro;F bulk near amp"],
    ["1", "PTT button", "momentary SPST (or use BOOT)"],
]
story.append(make_table(bom, [0.55*inch, 1.85*inch, 4.3*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Integrated alternative: <b>ESP32-S3-Korvo-2</b> (~$45\u201355) replaces mic/codec/amp/SD; use its BSP pin "
    "map and ES8311 codec init.", small))

story.append(Paragraph("D.10 &nbsp; System wiring diagram", h2))
if os.path.exists(DIAGRAM):
    from PIL import Image as PILImage
    iw, ih = PILImage.open(DIAGRAM).size
    avail_w = PAGE_W - ML - MR
    disp_w = avail_w
    disp_h = ih * (disp_w / iw)
    max_h = 4.8 * inch
    if disp_h > max_h:
        disp_h = max_h
        disp_w = iw * (disp_h / ih)
    img = Image(DIAGRAM, width=disp_w, height=disp_h)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Paragraph("Complete system wiring \u2014 ESP32-S3, mic, amp, microSD (Aircraft Card), and "
                           "split-legend annunciator with per-half lamp drivers.", cap))

# ================= PART E =================
story.append(PageBreak())
story += part_divider("E", "Enclosure Specification",
    "For the fabricating engineer. The housing is generic \u2014 sized for the electronics and the panel "
    "interface, not for a specific airframe. The only airframe-specific item is the mounting variant "
    "(DZUS slot vs. round instrument hole) and the card inside it.")

story.append(Paragraph("E.1 &nbsp; Two-piece architecture", h2))
arch2 = [
    ["Piece", "Contents", "Where", "Why"],
    ["<b>A. Panel bezel</b>", "Split-legend annunciator switch, speaker + grille, optional PTT", "Front panel / pedestal, on the <b>DZUS rail</b>", "Crew must see/reach it; annunciator in the normal scan"],
    ["<b>B. Remote box</b>", "ESP32-S3, mic, amp, <b>microSD slot</b>, lamp-driver, power conditioning", "Avionics bay / behind-panel, blind", "Keeps heat, the card slot, and wiring out of the panel"],
]
story.append(make_table(arch2, [1.15*inch, 2.2*inch, 1.65*inch, 1.7*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "A single all-in-one box is acceptable for a pure bench demo, but the two-piece split mirrors real "
    "remote-mount avionics and keeps the mic away from fan/avionics noise.", body))

story.append(Paragraph("E.2 &nbsp; Piece A \u2014 panel bezel", h2))
story.append(bullets([
    "<b>DZUS rail mount:</b> fastener pitch <b>3/8 in (9.525 mm)</b>; clearance hole <b>0.255 in (6.48 mm)</b>; "
    "bezel height a whole multiple of 3/8 in (target 3-unit = <b>28.575 mm</b>, or 4-unit = <b>38.1 mm</b> if "
    "the grille needs room); standard pedestal width <b>&asymp; 146 mm</b> aluminum (144.45 mm face); backplate "
    "<b>1/16 in (1.6 mm)</b> 6061-T6; first/last fastener <b>14.29 mm</b> from each end.",
    "<b>Round-hole variant:</b> fits a standard <b>3-1/8 in (79.4 mm)</b> instrument cutout with four 6-32 "
    "screws on the standard bolt circle, to replace a blanking plate where no DZUS slot exists.",
    "<b>Face layout (top&rarr;bottom):</b> split-legend annunciator switch (cut per the <i>specific</i> switch "
    "datasheet \u2014 typical VIVISUN bezel &asymp; 15&times;15 mm to 19&times;19 mm; top half <font name='Mono' "
    "size='8'>VOICE CHKLST OFF</font> white, bottom <font name='Mono' size='8'>VOICE CHKLST FAULT</font> amber, "
    "upright when installed); speaker grille (&ge; 40 % open over the cone, offset from the switch); optional "
    "guarded/recessed PTT.",
    "<b>Material/finish:</b> 6061-T6 aluminum 2.0\u20133.0 mm (or ABS/PC for a non-structural demo); <b>matte "
    "black, low-gloss (&le; 10 gloss units)</b> to suppress glare; legend by the switch's internal engraving "
    "(preferred) or laser-etch + white/amber paint-fill; edges chamfered 0.5 mm.",
]))

story.append(Paragraph("E.3 &nbsp; Piece B \u2014 remote processor box", h2))
story.append(bullets([
    "<b>Envelope:</b> sized around the ESP32-S3 DevKitC-1 (&asymp; 70&times;26 mm) plus amp, mic, microSD "
    "breakout, and the 2-channel lamp-driver; practical outer <b>&asymp; 110 &times; 80 &times; 45 mm</b>. "
    "Confirm against the actual stacked board set.",
    "<b>Mounting:</b> internal standoffs / M2.5 brass inserts \u2014 boards screwed down, not floating "
    "(vibration). Keep the mic away from the amp/any fan; if the mic lives here, add a meshed acoustic port; "
    "mic may instead live in the bezel (keep the I2S run &lt; 150 mm).",
    "<b>Access &amp; connectors:</b> externally swappable <b>microSD (Aircraft Card)</b> carrier labeled "
    "<font name='Mono' size='8'>CONFIG CARD \u2014 FAT32</font> (swap without opening the box); covered/recessed "
    "<b>USB-C</b> service port (bench use only); one keyed, positive-latching main connector (small "
    "MIL-circular or 9-pin D-sub) carrying SELECT, both legend drives, PTT, speaker +/&minus;, power/ground "
    "(pinout from <font name='Mono' size='8'>board_pins.h</font>). Accept USB 5 V &ge; 1 A; optional internal "
    "<b>28 V&rarr;5 V DC-DC</b> (&ge; 2 A) with TVS + fuse if a 28 V bus mock-up is wanted (mark as demo "
    "regulator, not DO-160 qualified).",
    "<b>Material/EMI:</b> aluminum preferred (doubles as EMI shield + heatsink); if plastic, add a grounded "
    "conductive shield liner/coating; single-point chassis ground stud bonded to the connector shell and "
    "ESP32 ground.",
]))

story.append(PageBreak())
story.append(Paragraph("E.4 &nbsp; Audio, thermal, environmental, labeling", h2))
story.append(bullets([
    f"<b>Audio:</b> 4\u20138 {OHM}, &ge; 2 W speaker, sealed-back or small rear volume (5\u201315 cm&sup3;); grille "
    "&ge; 40 % open with acoustic mesh; gasket the speaker to prevent buzz.",
    "<b>Thermal:</b> ESP32-S3 + ESP-SR is low-power (a few hundred mW) \u2014 <b>no fan</b>. Passive convection "
    "(vent slots low/high) or conduction (thermal pad to the aluminum wall). If sealed, verify internal rise "
    "&lt; 20 &deg;C above 55 &deg;C ambient. DC-DC (if fitted) on its own thermal path.",
    "<b>Environmental:</b> design toward the DO-160G categories in <b>C.4</b> (Cat A2 temp, Cat S vibration, "
    "etc.) \u2014 design guidance for the prototype, formal test for a productized unit.",
    "<b>Labeling:</b> placard <font name='Mono' size='8'>DEMO / TRAINING ONLY \u2014 NOT FOR FLIGHT</font>; box "
    "exterior carries unit name, serial/asset field, <font name='Mono' size='8'>FAT32</font> card format, and "
    "the USB \u201cbench use only\u201d note; annunciator legends <font name='Mono' size='8'>VOICE CHKLST OFF</font> "
    "(white) / <font name='Mono' size='8'>VOICE CHKLST FAULT</font> (amber); amber = caution, white = status "
    "per AC 25-11B.",
]))

story.append(Paragraph("E.5 &nbsp; Deliverables &amp; open items for the engineer", h2))
story.append(Paragraph(
    "<b>Deliverables:</b> STEP + native 3D CAD of both pieces (boards + switch modeled in place); "
    "fully-dimensioned 2D drawings (DZUS pattern, switch cutout from the chosen datasheet, grille, connector "
    "cutouts; GD&amp;T on the switch cutout and DZUS holes); connector pinout mapped to <font name='Mono' "
    "size='8'>board_pins.h</font>; an FDM/SLA printable prototype for fit-check; a mechanical BOM; tolerances "
    "(switch cutout &plusmn;0.1 mm, DZUS holes &plusmn;0.1 mm on the 9.525 mm pitch, general &plusmn;0.25 mm).", body))
story.append(callout(
    "<b>Open items (confirm before CAD):</b> the <b>exact Applied Avionics switch part number</b> \u2014 the single "
    "most critical dimension; nothing finalizes until it is fixed. Also: DZUS slot vs. 3-1/8 in round hole in "
    "the target panel; where the mic lives; whether a 28 V input is wanted; and the speaker model (sets grille "
    "open area + rear-volume cavity).", "warn"))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Reference dimensions:</b> DZUS pitch 9.525 mm &middot; DZUS hole 6.48 mm &middot; backplate 1.6 mm "
    "&middot; first fastener offset 14.29 mm &middot; pedestal panel width &asymp; 146 mm &middot; round "
    "instrument hole 79.4 mm &middot; remote box &asymp; 110 &times; 80 &times; 45 mm &middot; speaker 4\u20138 "
    + OHM + " &ge; 2 W.", small))

# ================= PART F =================
story.append(PageBreak())
story += part_divider("F", "References",
    "All cited regulatory, component, and mechanical sources, with clickable links.")

story.append(Paragraph("Certification &amp; regulatory", h3))
cert_src = [
    ("FAA Policy Statement PS-AIR-21.8-1602 \u2014 \u201cApproval of Non-Required Safety Enhancing Equipment (NORSEE)\u201d", "https://www.gajsc.org/wordpress/wp-content/uploads/2016/08/PS-AIR-21.8-1602.pdf"),
    ("FAA Technical Standard Orders (TSO) program overview", "https://www.faa.gov/aircraft/air_cert/design_approvals/tso"),
    ("FAA AC 21-16G \u2014 acceptance of RTCA/DO-160 versions D\u2013G", "https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/1019280"),
    ("RTCA DO-160G \u2014 Environmental Conditions and Test Procedures for Airborne Equipment", "https://www.rtca.org/training/do-160g-training/"),
    ("FAA AC 20-152A \u2014 Development Assurance for Airborne Electronic Hardware (simple-hardware relief)", "https://en.wikipedia.org/wiki/AC_20-152"),
    ("FAA AC 20-168 / RTCA DO-313 \u2014 installation of non-essential, non-required equipment", "https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentid/315695"),
    ("TSO / TC / STC / PMA primer (Afuzion)", "https://afuzion.com/tso-tc-stc-and-pma-intro/"),
    ("FAA AC 25-11B \u2014 electronic flight displays; annunciation color / dark-cockpit conventions", "https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf"),
]
rows = [["#", "Reference", "Link"]]
for i, (t, u) in enumerate(cert_src, 1):
    rows.append([str(i), t, Paragraph(A("open", u), cell)])
fss = {(i,0): cellb for i in range(1, len(rows))}
story.append(make_table(rows, [0.4*inch, 5.5*inch, 0.8*inch], font_styles=fss))

story.append(Paragraph("Hardware &amp; components", h3))
hw_src = [
    ("INMP441 microphone datasheet", "https://www.farnell.com/datasheets/1824785.pdf"),
    ("MAX98357A amplifier datasheet (Analog Devices)", "https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf"),
    ("MAX98357A breakout guide (Adafruit)", "https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf"),
    ("ESP32-S3 GPIO drive current discussion", "https://esp32.com/viewtopic.php?t=20097"),
    ("microSD operating current", "https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975"),
    ("Applied Avionics VIVISUN lighted pushbutton switches", "https://www.appliedavionics.com/led-lighted-pushbutton-switches.html"),
    ("Espressif ESP-SR speech framework", "https://docs.espressif.com/projects/esp-sr/en/latest/esp32s3/index.html"),
    ("Espressif ESP32-P4 product page", "https://www.espressif.com/en/products/socs/esp32-p4"),
    ("ESP32-P4 vs ESP32-S3 performance", "https://www.elecrow.com/blog/who-is-the-true-performance-king-esp32-p4-vs-esp32-s3.html"),
]
rows = [["#", "Reference", "Link"]]
for i, (t, u) in enumerate(hw_src, 1):
    rows.append([str(i), t, Paragraph(A("open", u), cell)])
fss = {(i,0): cellb for i in range(1, len(rows))}
story.append(make_table(rows, [0.4*inch, 5.5*inch, 0.8*inch], font_styles=fss))

story.append(Paragraph("Mechanical / panel", h3))
mech_src = [
    ("DZUS panel-building dimensions guide (MyCockpit)", "https://www.mycockpit.org/tutorials/Panelbuildingfocussedondimensions.pdf"),
    ("Standard 3-1/8 in instrument cutout (Aircraft Spruce)", "https://www.aircraftspruce.com/catalog/inpages/instradaptkit.php"),
]
rows = [["#", "Reference", "Link"]]
for i, (t, u) in enumerate(mech_src, 1):
    rows.append([str(i), t, Paragraph(A("open", u), cell)])
fss = {(i,0): cellb for i in range(1, len(rows))}
story.append(make_table(rows, [0.4*inch, 5.5*inch, 0.8*inch], font_styles=fss))

story.append(Spacer(1, 14))
story.append(callout(
    "<b>DEMO / TRAINING ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS.</b> Repository: "
    "github.com/flas-tech/cj2-voice-emergency-checklist (MIT License). The certification sections describe a "
    "path, not held approvals; no NORSEE LOA, STC, PMA, or TSOA exists for this article.", "warn"))

# ================= PAGE TEMPLATES =================
TITLE = "Voice Emergency Checklist"

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(HEADER_BG)
    canvas.rect(0, PAGE_H - 3.3*inch, PAGE_W, 3.3*inch, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 3.38*inch, PAGE_W, 0.08*inch, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#BCE2E7"))
    canvas.setFont("DM-M", 11)
    canvas.drawString(ML, PAGE_H - 1.1*inch, "MASTER TECHNICAL & CERTIFICATION REFERENCE  \u00b7  AIRCRAFT-AGNOSTIC")
    canvas.setFillColor(colors.white)
    canvas.setFont("DM-B", 33)
    canvas.drawString(ML, PAGE_H - 1.9*inch, "Voice Emergency")
    canvas.drawString(ML, PAGE_H - 2.4*inch, "Checklist System")
    canvas.setFont("DM-M", 14)
    canvas.setFillColor(colors.HexColor("#BCE2E7"))
    canvas.drawString(ML, PAGE_H - 2.85*inch, "Generic advisory reader \u00b7 driven by the installed Aircraft Card")
    canvas.setFillColor(INK)
    canvas.setFont("DM", 11)
    y = PAGE_H - 4.05*inch
    lines = [
        "One combined reference: product, Aircraft Card spec, certification basis,",
        "hardware, and enclosure. Supersedes the separate tech, processor, and",
        "enclosure documents.",
        "",
        "Cert path: NORSEE (PS-AIR-21.8-1602) \u00b7 DO-160G environmental \u00b7",
        "deliberate DO-178C-avoidance argument \u00b7 STC/PMA placement.",
    ]
    for ln in lines:
        canvas.drawString(ML, y, ln); y -= 0.27*inch
    canvas.setFillColor(colors.HexColor("#FBF1E9"))
    canvas.roundRect(ML, 1.95*inch, PAGE_W - ML - MR, 1.0*inch, 6, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.rect(ML, 1.95*inch, 0.05*inch, 1.0*inch, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.setFont("DM-B", 11.5)
    canvas.drawString(ML + 0.25*inch, 2.62*inch, "DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS")
    canvas.setFillColor(INK)
    canvas.setFont("DM", 8.8)
    canvas.drawString(ML + 0.25*inch, 2.36*inch, "Not airworthy and not certified. The certification sections describe the path a productized unit would")
    canvas.drawString(ML + 0.25*inch, 2.18*inch, "follow \u2014 a plan, not held approvals. No NORSEE LOA, STC, PMA, or TSOA exists for this article.")
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(0.6)
    canvas.line(ML, 1.5*inch, PAGE_W - MR, 1.5*inch)
    canvas.setFillColor(MUTED); canvas.setFont("DM", 9)
    canvas.drawString(ML, 1.25*inch, "Repository:  github.com/flas-tech/cj2-voice-emergency-checklist")
    canvas.drawString(ML, 1.05*inch, "Generated June 10, 2026  \u00b7  Perplexity Computer")
    canvas.restoreState()

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DM", 7.5); canvas.setFillColor(FAINT)
    canvas.drawString(ML, PAGE_H - 0.55*inch, TITLE + "  \u00b7  Master Technical & Certification Reference")
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
    title="Voice Emergency Checklist \u2014 Master Technical & Certification Reference",
    author="Perplexity Computer",
)
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[frame_full], onPage=draw_cover),
    PageTemplate(id="main", frames=[frame_main], onPage=header_footer),
])
doc.build(story)
print("BUILT", OUT, os.path.getsize(OUT), "bytes")
