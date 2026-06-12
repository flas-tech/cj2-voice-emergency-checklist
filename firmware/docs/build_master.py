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
    "<b>installed cards</b> (Part B). The Cessna Citation CJ2 is included only as the "
    "reference example.", bodyj))
story.append(Paragraph(
    "<b>Crew audio is taken from the aircraft audio panel</b> (analog or digital, selectable per "
    "installation), and recognition is <b>voice-activated (VOX)</b> by default \u2014 the pilot simply "
    "speaks, with a push-to-talk (PTT) button retained as a manual override. <b>Configuration and "
    "checklist data live on two separate cards</b> \u2014 a write-protected <b>Config Card</b> that defines "
    "the installation (aircraft selection, audio source, VOX behavior, hardware options) and a "
    "<b>Data Card</b> that carries the checklist library and audio. This two-card, audio-panel-fed "
    "design is a deliberate change from the earlier onboard-microphone / single-card demo and carries "
    "certification consequences addressed honestly in Part C.", bodyj))
story.append(Paragraph(
    "<b>This master reference supersedes and combines</b> the previously separate documents: the "
    "technical data packet, the processor-selection note, and the enclosure specification. Those "
    "remain in the repository for history; this is the single source of truth.", bodyj))
story.append(Spacer(1, 6))
dmap = [
    ["Part", "Contents"],
    ["<b>A &nbsp;Product</b>", "What the system is, the generic architecture, and the safety model"],
    ["<b>B &nbsp;The cards</b>", "The two-card (Config + Data) model + the formal card specifications &amp; validation"],
    ["<b>C &nbsp;Certification basis</b>", "NORSEE / DO-160G / installation path, the deliberate DO-178C-avoidance argument, and the audio-panel-interface impact"],
    ["<b>D &nbsp;Hardware reference</b>", "Pin map, audio-input stage, VOX/PTT, per-device wiring, annunciator, lamp driver, power, BOM, processor selection"],
    ["<b>E &nbsp;Enclosure</b>", "Two-piece mechanical specification (dual card slots, isolated audio interface) for the fabricating engineer"],
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
    ["<b>Receive-only on the audio-panel INPUT tap</b> (galvanically isolated, listen-only); plus a <b>separate, galvanically-isolated OUTPUT into a dedicated COM3-style audio-panel channel</b> for checklist read-aloud; no command/data to any aircraft system", "A transmitter on aircraft COM radios, a panel control, or an interface to avionics/engines/flight controls. It <b>does</b> inject advisory audio into one dedicated aux/COM3-style channel via an isolated output \u2014 but that output is on a <b>separate channel</b> from the receive tap and is electrically isolated from required COM channels"],
    ["Driven entirely by the installed <b>Config Card + Data Card</b>", "Tied to one airframe in firmware"],
    ["<b>Offline</b>, deterministic, single-chip", "A cloud / connected / large-vocabulary STT device"],
    ["A <b>complement</b> to the certified/required checklist", "A substitute for the AFM/QRH or required checklist"],
]
story.append(make_table(isnot, [3.35*inch, 3.35*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "This framing is not cosmetic \u2014 it is the foundation of the certification argument in Part C. The "
    "device connects to the aircraft through <b>two electrically separate, galvanically-isolated channels</b>: "
    "(1) a <b>receive-only isolated INPUT tap</b> (listen-only; cannot back-feed) used as the ASR speech "
    "source, and (2) a <b>separate, galvanically-isolated OUTPUT into a dedicated COM3-style audio-panel "
    "channel</b> (an isolated line-level transmit stage) that delivers checklist read-aloud audio to "
    "the crew in-headset. The input-tap language of \u201creceive-only, isolated\u201d is preserved for the "
    "INPUT path; the OUTPUT path is a deliberate, bounded, unidirectional injection into one dedicated "
    "aux channel. This <b>dual-isolated-channel architecture</b> is the interface posture the Part C "
    "argument is built on. Note that the <b>addition of the isolated COM3-style audio output is the most "
    "significant certification and interface-risk change in this revision</b>; Part C addresses it "
    "honestly.", bodyj))

story.append(Paragraph("A.2 &nbsp; Generic system architecture", h2))
arch = [
    ["Block", "Function", "Install-/aircraft-specific?"],
    ["<b>MCU + speech stack</b>", "VOX/wake word &rarr; command recognition &rarr; playback sequencing", "No \u2014 fixed firmware"],
    ["<b>Audio-panel input stage</b>", "Takes crew speech <b>from the aircraft audio panel</b> \u2014 analog (isolated line tap) or digital (I2S codec), selectable per install", "<b>Config-driven</b> \u2014 source set by the Config Card; path wired at install"],
    ["<b>Audio-panel output stage (isolated TX to COM3-style channel)</b>", "Delivers checklist read-aloud audio <b>out to a dedicated COM3-style audio-panel input channel</b> via a galvanically-isolated, line-level output stage (isolation transformer + line driver on the TX line); crew hears checklist items in-headset. <b>Onboard speaker/amplifier removed.</b> The output is on a <b>separate channel and separate connector</b> from the receive-only INPUT tap.", "No (fixed output stage hardware; the audio-panel COM3 channel it drives is chosen at installation)"],
    ["<b>Config Card (microSD, slot 1)</b>", "Defines the installation: active aircraft, audio source (analog/digital), VOX parameters, hardware options", "<b>Yes \u2014 per installation</b>"],
    ["<b>Data Card (microSD, slot 2)</b>", "Carries the checklist library, trigger/advance vocabulary, and read-aloud audio", "<b>Yes \u2014 per aircraft</b>"],
    ["<b>Annunciator switch</b>", "Dark-cockpit status / fault indication, IN/OUT select, PTT override", "No"],
]
story.append(make_table(arch, [1.55*inch, 3.45*inch, 1.7*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "The MCU runs Espressif <b>ESP-SR</b> (AFE noise-suppression/VAD &rarr; WakeNet wake word &rarr; "
    "MultiNet fixed-grammar command recognition). The <b>AFE's voice-activity detector (VAD) is what "
    "enables hands-free VOX</b>: the pilot speaks and the device gates recognition on detected speech, with "
    "the PTT button retained as a manual override (force-listen). The grammar (trigger phrases, advance "
    "words) is small and bounded, which is what keeps an MCU-class part in scope (see D.7).", body))
story.append(Paragraph(
    "The crew-audio source is <b>no longer an onboard microphone in the operational design</b> \u2014 it is a "
    "tap off the aircraft audio panel. An onboard MEMS microphone is retained only as a documented "
    "<b>bench-test</b> option (D.3), never as the installed audio source.", body))

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
    "<b>Dual-isolated-channel interface.</b> The device's ties to the aircraft audio panel are two "
    "electrically separate, galvanically-isolated channels (C.3a, D.3): "
    "(a) a <b>receive-only isolated INPUT tap</b> \u2014 a high-impedance, isolation-transformer-coupled "
    "or buffered-receive-only tap off the audio panel; the unit <b>cannot transmit, key, mute, or "
    "back-feed</b> via this path; a short, open, or power loss inside the device cannot affect the "
    "panel via the input path; and "
    "(b) an <b>isolated OUTPUT into a dedicated COM3-style channel</b> \u2014 a galvanically-isolated, "
    "line-level output stage (isolation transformer on the TX line) that injects checklist read-aloud "
    "audio into the panel's dedicated COM3-style aux channel; physically separate connector from the "
    "input tap. The isolation barrier ensures a device fault <b>cannot key, jam, load, or back-feed "
    "the panel's other channels or required COM radios</b>. "
    "This output channel is the most significant certification and interface-risk item in this revision. "
    "The device draws power on its own protected rail. This dual-isolated-channel posture replaces the "
    "former \u201creceive-only only\u201d claim with a narrower, testable one covering both directions.",
]))

# ================= PART B =================
story.append(PageBreak())
story += part_divider("B", "The Two Cards",
    "Card defines everything \u2014 split across two. The product is generic; two installed microSD cards "
    "make it a specific aircraft's checklist reader, installed a specific way. A write-protected Config "
    "Card describes the installation; a Data Card carries the checklist content. This part is the formal "
    "specification \u2014 layouts, schemas, voice-grammar rules, and the validation logic that implements "
    "revert-to-unopened.")

story.append(Paragraph("B.1 &nbsp; Principle", h2))
story.append(callout(
    "<b>The product is generic. The two installed cards make it a specific aircraft's checklist reader, "
    "installed a specific way.</b> Responsibility is split: the <b>Config Card</b> describes <i>this "
    "installation</i> (which aircraft, which audio source, how VOX behaves, what hardware is fitted); the "
    "<b>Data Card</b> carries <i>the checklist content</i> (library, vocabulary, audio). To support a new "
    "airframe you author a new Data Card; to re-use it in a different aircraft or wiring you change only "
    "the Config Card. <b>No firmware change, no recompile.</b>", "info"))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Why two cards? Configuration is <b>installation-controlled</b> (set by the installer/shop and locked) "
    "while checklist data is <b>content-controlled</b> (authored from the AFM/QRH and revised as the source "
    "revises). Separating them keeps a content revision from silently changing the installation's "
    "audio/VOX setup, and lets a write-protected Config Card serve as the configuration-control record the "
    "FAA expects under NORSEE (Part C). Both cards are microSD/FAT32 and sit in <b>two physical slots</b> "
    "(slot 1 = CONFIG, slot 2 = DATA; see E.3).", bodyj))

story.append(Paragraph("B.2 &nbsp; Config Card (slot 1) \u2014 layout &amp; schema", h2))
story.append(mono_light(
    "/sdcard-config/   (slot 1, microSD, FAT32)\n"
    "  config.json     the single installation-configuration manifest"))
story.append(Spacer(1, 8))
story.append(Paragraph("<font name='Mono' size='8.5'>config.json</font> top-level object:", body))
cfg = [
    ["Field", "Type", "Req.", "Meaning"],
    ["<font name='Mono' size='8'>schema_version</font>", "integer", "rec.", "Config-schema version the firmware validates against"],
    ["<font name='Mono' size='8'>aircraft</font>", "string", "<b>yes</b>", "Active aircraft id; <b>must match</b> a folder on the Data Card"],
    ["<font name='Mono' size='8'>audio_source</font>", "string", "<b>yes</b>", "<font name='Mono' size='8'>analog</font> or <font name='Mono' size='8'>digital</font> \u2014 selects the audio-panel input path (D.3.1)"],
    ["<font name='Mono' size='8'>audio</font>", "object", "<b>yes</b>", "Audio-input parameters (below)"],
    ["<font name='Mono' size='8'>vox</font>", "object", "<b>yes</b>", "VOX behavior (below)"],
    ["<font name='Mono' size='8'>hardware</font>", "object", "opt.", "Fitted-hardware options (codec part, legend rail, PTT present, etc.)"],
    ["<font name='Mono' size='8'>install</font>", "object", "rec.", "Provenance: shop, installer, date, work-order (configuration control)"],
]
story.append(make_table(cfg, [1.55*inch, 0.75*inch, 0.6*inch, 3.8*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph("<font name='Mono' size='8.5'>audio</font> object:", body))
aud = [
    ["Field", "Type", "Req.", "Meaning"],
    ["<font name='Mono' size='8'>input_gain_db</font>", "number", "rec.", "Input trim for the line-level tap (typ. 0\u20136 dB)"],
    ["<font name='Mono' size='8'>codec</font>", "string", "when <font name='Mono' size='7.5'>digital</font>", "I2S codec fitted (e.g. <font name='Mono' size='8'>es8388</font>, <font name='Mono' size='8'>es7210</font>, <font name='Mono' size='8'>pcm1808</font>)"],
    ["<font name='Mono' size='8'>sample_rate_hz</font>", "integer", "rec.", "16000 for ESP-SR"],
]
story.append(make_table(aud, [1.55*inch, 0.75*inch, 0.85*inch, 3.55*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph("<font name='Mono' size='8.5'>vox</font> object:", body))
voxt = [
    ["Field", "Type", "Req.", "Meaning"],
    ["<font name='Mono' size='8'>mode</font>", "string", "<b>yes</b>", "<font name='Mono' size='8'>vox</font> (default, hands-free) or <font name='Mono' size='8'>ptt_only</font> (override-only)"],
    ["<font name='Mono' size='8'>vad_sensitivity</font>", "integer", "rec.", "AFE VAD aggressiveness 0\u20133 (higher = less false-trigger, may clip onset)"],
    ["<font name='Mono' size='8'>hangover_ms</font>", "integer", "rec.", "How long to keep listening after speech stops (debounce, typ. 300\u2013600 ms)"],
    ["<font name='Mono' size='8'>ptt_override</font>", "boolean", "rec.", "<font name='Mono' size='8'>true</font> keeps PTT as a force-listen override even in <font name='Mono' size='8'>vox</font> mode"],
]
story.append(make_table(voxt, [1.55*inch, 0.75*inch, 0.6*inch, 3.8*inch]))
story.append(Spacer(1, 6))
story.append(bullets([
    "<b><font name='Mono' size='8.5'>ptt_only</font> mode</b> disables VOX and reverts to the legacy "
    "push-to-talk behavior.",
    "A Config Card whose <font name='Mono' size='8.5'>aircraft</font> has no matching Data Card folder is a "
    "fault (<font name='Mono' size='8.5'>FAULT_AIRCRAFT_MISMATCH</font>), not a silent guess.",
]))

story.append(Paragraph("B.3 &nbsp; Data Card (slot 2) \u2014 layout", h2))
story.append(mono_light(
    "/sdcard-data/   (slot 2, microSD, FAT32)\n"
    "  <FOLDER>/                  one folder per aircraft (e.g. CJ2, B200, PC12)\n"
    "    checklists.json          the data manifest + checklist library\n"
    "    audio/\n"
    "      <clip>.wav             one read-aloud clip per referenced item + fault clips"))
story.append(Spacer(1, 8))
story.append(bullets([
    "The firmware loads the folder named by the <b>Config Card's</b> "
    "<font name='Mono' size='8.5'>aircraft</font> field. If no Config Card is present at all, that is "
    "<font name='Mono' size='8.5'>FAULT_NO_CONFIG</font> \u2014 the device does <b>not</b> fall back to "
    "guessing a folder.",
]))

story.append(Paragraph("B.3a &nbsp; Data Card manifest schema (checklists.json)", h2))
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
story.append(Paragraph("B.4 &nbsp; Two-card validation &amp; the revert-to-unopened rule", h2))
story.append(Paragraph(
    "On boot the firmware attempts a <b>complete, valid</b> load of <b>both cards</b> and returns exactly "
    "one status. Both cards must be present, valid, and <b>mutually consistent</b> (the Config Card's "
    "<font name='Mono' size='8.5'>aircraft</font> must resolve to a Data Card folder):", body))
val = [
    ["Status", "Card", "Meaning", "Annunc."],
    ["<font name='Mono' size='7.5'>STORE_OK</font>", "both", "Both cards mounted, both manifests parsed + schema-valid, <b>every</b> audio clip present, aircraft consistent", "dark"],
    ["<font name='Mono' size='7.5'>FAULT_NO_CONFIG</font>", "config", "Config Card not detected / <font name='Mono' size='7.5'>config.json</font> missing / unreadable", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_CONFIG_PARSE</font>", "config", "<font name='Mono' size='7.5'>config.json</font> malformed", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_CONFIG_VALIDATION</font>", "config", "Config schema / value violation (bad <font name='Mono' size='7.5'>audio_source</font>, bad <font name='Mono' size='7.5'>vox.mode</font>, missing required field)", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_NO_CARD</font>", "data", "Data Card not detected / mount failed", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_AIRCRAFT_MISMATCH</font>", "both", "Config <font name='Mono' size='7.5'>aircraft</font> has no matching Data Card folder", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_NO_JSON</font>", "data", "<font name='Mono' size='7.5'>checklists.json</font> missing / unreadable", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_PARSE</font>", "data", "Data JSON malformed", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_VALIDATION</font>", "data", "Data schema or voice-rule violation, empty data", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_AUDIO_MISSING</font>", "data", "A referenced clip is absent", "amber"],
    ["<font name='Mono' size='7.5'>FAULT_NO_MEMORY</font>", "\u2014", "Allocation failed while loading", "amber"],
]
story.append(make_table(val, [1.75*inch, 0.55*inch, 3.65*inch, 0.75*inch]))
story.append(Spacer(1, 8))
story.append(callout(
    "<b>On any FAULT the in-memory checklist table is left EMPTY</b> \u2014 the device cannot present a partial "
    "or stale checklist even if asked. This is the literal implementation of \u201calways revert to unopened "
    "if files are not available.\u201d The boot order is <b>Config Card first</b> (it names the aircraft and the "
    "audio source the input stage must initialize), then the matching Data Card folder.", "warn"))

story.append(Paragraph("B.5 &nbsp; Card integrity &amp; provenance (recommended for productized cards)", h2))
story.append(Paragraph(
    "For cards that drive a <i>safety-enhancing</i> device, integrity matters as much as schema validity. "
    "Recommended additions (forward-looking, beyond the current demo):", body))
story.append(bullets([
    "<b>Schema version gate</b> \u2014 firmware refuses either card whose <font name='Mono' size='8.5'>schema_version</font> "
    "it does not support, rather than mis-parsing it.",
    "<b>Manifest checksum / signature</b> \u2014 a per-card hash (and, for production, a signature) so a corrupted "
    "or tampered card is rejected (<font name='Mono' size='8.5'>FAULT_CONFIG_VALIDATION</font> / "
    "<font name='Mono' size='8.5'>FAULT_VALIDATION</font>).",
    "<b>Content provenance (Data Card)</b> \u2014 record the AFM/QRH source revision the checklist text was "
    "transcribed from, the author, and the date.",
    "<b>Installation provenance (Config Card)</b> \u2014 the <font name='Mono' size='8.5'>install</font> object "
    "records shop, installer, date, and work-order. The Config Card is the per-tail "
    "<b>configuration-control record</b> the FAA expects under NORSEE (Part C): it documents <i>how this "
    "specific aircraft was set up</i>, including the audio source and VOX behavior.",
    "<b>Read-only media</b> \u2014 distribute production cards write-protected; the Config Card in particular "
    "should be <b>locked after installation</b> so configuration cannot drift in service.",
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
    "<b>Bounded dual-isolated interface.</b> This revision adds <b>two</b> ties to an aircraft "
    "system (C.3a), both galvanically isolated: (a) a <b>receive-only isolated INPUT tap</b> off "
    "the audio panel \u2014 the device cannot command a function or produce output via this path; and "
    "(b) a <b>dedicated isolated OUTPUT</b> into a COM3-style audio-panel channel for checklist "
    "read-aloud delivery \u2014 a unidirectional audio injection through an isolation transformer, not "
    "a control/keying/command path. The device still produces <b>no command or control output to "
    "any aircraft system</b>, but it does inject advisory audio into one dedicated aux channel. "
    "The output injection is a <b>more invasive interface than a pure receive-only tap</b> and is "
    "called out as such; the argument now rests on <i>isolation + directionality + channel "
    "separation</i> rather than <i>total receive-only</i><super>1</super>.",
    "<b>Qualitative safety evaluation is permitted</b> for non-complex equipment; a quantitative probabilistic "
    "analysis (and the DO-178C machinery that feeds it) is not required for a minor-failure advisory "
    "function<super>1</super>.",
]))
story.append(Spacer(1, 4))
story.append(callout(
    "<b>Honest caveats (must stay in the doc):</b> (1) This argument <b>must be agreed with the FAA ACO "
    "early</b> \u2014 the applicant proposes the classification; the FAA concurs. If the FAA judges the failure "
    "condition above minor (e.g. because of over-reliance / automation-dependency human factors, <b>or because "
    "the audio-panel interface is judged to compromise an aircraft communication system</b>), the program "
    "moves to &sect;2 of the NORSEE policy (xx.1309, ARP4754A/ARP4761) and software assurance re-enters. "
    "(2) \u201cNo DO-178C\u201d is <b>earned by architecture and procedural mitigations</b>, not by labeling \u2014 "
    "the revert-to-unopened behavior, the validation gate, the dark-cockpit annunciation, the "
    "<b>dual-isolated-channel interface</b> (receive-only input tap + isolated output into a dedicated "
    "COM3-style channel), and a <b>mandatory limitation that the unit may not be used as a substitute for the "
    "required checklist</b> are the price of that classification. "
    "(3) <b>The audio-panel interface raises the installation bar \u2014 further still with the output "
    "channel.</b> What was arguably a minor alteration (a self-contained box drawing only power) now "
    "wires into an <b>aircraft communication system</b> for both receive and transmit. The output channel "
    "is a more invasive interface than a pure receive-only tap, pushing the path toward an STC or "
    "careful field-approval scrutiny on most airframes (C.3a, C.5) \u2014 do not assume a logbook-entry "
    "minor alteration any more. "
    "(4) <b>VOX adds a human-factors failure mode.</b> Hands-free activation can <b>false-trigger</b> on ambient "
    "cockpit speech, ATC audio, or crew conversation, potentially reading an unrequested checklist; it is "
    "mitigated by VAD sensitivity tuning, a bounded trigger grammar, the retained PTT override, and the "
    "standing limitation that the required checklist remains the authority (C.3a, D.3.2).", "warn"))

story.append(Paragraph("C.3a &nbsp; Audio-panel interface impact (the honest part)", h2))
story.append(Paragraph(
    "This revision adds <b>two</b> interfaces to the aircraft audio panel: a receive-only isolated "
    "INPUT tap (for crew-speech ASR) and a dedicated isolated OUTPUT channel (COM3-style) for "
    "checklist read-aloud delivery. Both must be argued explicitly. The goal is to make each interface "
    "so narrow and so demonstrably bounded that the residual failure stays minor. The output path is "
    "the more significant of the two.", bodyj))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>What the interface is \u2014 and is not:</b>", body))
ai_iface = [
    ["Property", "INPUT tap (receive-only)", "OUTPUT channel (isolated TX to COM3)"],
    ["<b>Directionality</b>",
        "<b>Receive-only.</b> No path to transmit, key a radio, mute, or back-feed.",
        "<b>Output-only.</b> Unidirectional line-level audio injection into the panel's dedicated COM3-style aux channel. Not a keying or control path."],
    ["<b>Isolation</b>",
        "<b>600 " + OHM + " aviation audio isolation transformer</b> (e.g. Allen Avionics AGL series) on the analog path; buffered receive-only I2S for the digital path. No data driven back toward any aircraft bus.",
        "<b>Line-level isolation transformer</b> on the TX output line; galvanic barrier between the device and the panel's COM3 input. A fault in the device cannot key, jam, load, or back-feed the panel's other channels or required COM radios."],
    ["<b>Fault containment</b>",
        "Short, open, or power loss inside the device cannot load down, ground, or back-feed the panel via the input path.",
        "Short, open, or power loss cannot key or jam the panel via the output path; the isolation transformer is the primary barrier."],
    ["<b>Channel separation</b>",
        "Separate connector from the OUTPUT path; cannot be mis-mated.",
        "Dedicated aux channel (COM3-style), not the crew intercom or any required COM radio channel. A failure on the output side cannot affect other panel channels."],
    ["<b>No operational credit</b>",
        "The panel feed is <i>listened to</i> for recognition only.",
        "The injected audio is advisory/informational only; the crew's authority is the required checklist."],
]
story.append(make_table(ai_iface, [1.3*inch, 2.7*inch, 2.7*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph("<b>Why this still supports a minor classification (INPUT tap):</b>", body))
story.append(bullets([
    "The audio panel and intercom <b>continue to function identically whether the device is present, powered, "
    "or failed</b> \u2014 the tap is parallel and high-impedance.",
    "The failure modes the input tap could plausibly add (loading, ground loop, injected noise) are <b>removed by "
    "isolation and the receive-only topology</b>, and are exactly what <b>DO-160G conducted/induced-susceptibility "
    "and the audio-system installation tests</b> are meant to verify (C.4).",
    "This is analogous to other <b>listen-only</b> cockpit aids (cockpit voice recorders, audio-logging headsets) "
    "that tap audio without compromising the source.",
]))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Why the output channel raises the bar (do not gloss over this):</b>", body))
story.append(bullets([
    "<b>Isolation/failure modes.</b> The isolation transformer on the TX line is the primary barrier; the "
    "isolation design ensures a fault inside the device (including output-stage failure, supply fault, or "
    "software runaway) <b>cannot key, jam, load, or back-feed</b> the panel's COM channels or intercom.",
    "<b>Non-interference with required COM audio.</b> The cert argument must show the injected advisory audio "
    "<b>cannot interfere with</b> required ATC/aircraft audio on the panel \u2014 e.g. that the output level "
    "is set conservatively, that the COM3 channel cannot bleed onto required COM1/COM2 channels, and that "
    "the injected audio cannot mask or be mistaken for required audio.",
    "<b>Masking/intelligibility human factors.</b> There must be no plausible confusion between the "
    "injected checklist audio and required ATC/aircraft audio, and the injected audio must not mask "
    "ATC calls. This requires careful level treatment, a conservative output level, and the standing "
    "limitation that the required checklist remains the authority.",
    "The interface now wires into an <b>aircraft communication system for both receive and transmit</b>; "
    "plan for STC or carefully substantiated field approval that explicitly addresses the isolated output "
    "channel (C.5).",
]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>VOX (voice-activation) certification note.</b> Replacing push-to-talk with VOX as the primary trigger "
    "introduces a <b>false-activation human-factors mode</b> (reading an unrequested checklist on stray "
    "speech / ATC audio). Mitigations carried into the design: bounded wake-word + trigger grammar (not "
    "open-vocabulary), tunable VAD sensitivity and hangover (Config Card, B.2), the <b>retained PTT override</b>, "
    "and the standing limitation that the required checklist remains the authority. The ACO will want this mode "
    "addressed in the safety / human-factors evaluation<super>1</super>.", bodyj))

story.append(PageBreak())
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
    ["&sect;18 AF Conducted Susceptibility", "Cat \u2014", "As applicable to the supply; <b>also relevant to the audio-panel input</b> \u2014 verify recognition is not corrupted by AF conducted noise"],
    ["&sect;19 Induced Signal Susceptibility", "Cat ZC", "Cockpit; <b>audio-input cabling</b> routed/shielded per the panel's installation practice"],
    ["&sect;20 RF Susceptibility", "Cat \u2014", "Aluminum case + grounded shield"],
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
story.append(Spacer(1, 6))
story.append(callout(
    "<b>Audio-interface-specific evidence (beyond the table):</b> because the unit now connects to the "
    "audio panel on both a receive-only INPUT tap and an isolated OUTPUT channel, qualification should "
    "additionally demonstrate \u2014 across all DO-160G conditions and <b>including a failed/unpowered device</b> "
    "\u2014 that (a) the receive tap does not degrade audio-panel performance (intercom level, sidetone, the "
    "panel's own VOX/hot-mic behavior), and (b) the isolated OUTPUT cannot key, jam, load, or back-feed "
    "the panel's other channels or required COM radios, and the injected advisory audio level does not "
    "mask or interfere with required ATC/aircraft audio. The isolation transformers on both paths (C.3a) "
    "and the high-impedance receive-only input topology are the design basis for that demonstration.", "info"))

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
story.append(Spacer(1, 6))
story.append(callout(
    "<b>The audio-panel interface raises the install classification \u2014 the output channel raises it further.</b> "
    "Because the device now wires into an <b>aircraft communication system</b> for both receive and transmit, "
    "step 4 should be approached assuming the interface makes the alteration <b>more than minor</b> on most "
    "airframes \u2014 i.e. plan for an <b>STC or a field approval that specifically substantiates both the "
    "receive-only input tap and the isolated COM3-style audio output</b> (isolated, no degradation of comm "
    "audio, no keying/jamming of required COM channels, no masking per C.3a/C.4), not a bare logbook entry. "
    "The earlier power-only/independent design could credibly claim a minor alteration; this one generally "
    "cannot.", "warn"))

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
    ["Software assurance", "<b>DO-178C not sought</b> \u2014 advisory/minor (C.3)", "Architecture supports it; ACO concurrence pending"],
    ["Complex hardware", "DO-254 not invoked (simple COTS) \u2014 AC 20-152A", "N/A by design"],
    ["Human factors / color", "AC 25-11B conventions, dark-cockpit", "Implemented in design"],
    ["Audio-panel interface \u2014 INPUT tap", "Receive-only + galvanic isolation (C.3a, C.4 &sect;18/&sect;19); cannot key/jam/back-feed via input path", "Architecture defined; substantiation/test pending"],
    ["<b>Audio-panel interface \u2014 OUTPUT channel (COM3)</b>", "Galvanically-isolated line-level TX to dedicated COM3-style channel; isolation transformer on TX line; cannot key/jam/load panel or required COMs; advisory audio cannot mask required ATC audio (C.3a)", "<b>Architecture defined; this is the most significant new interface-risk item \u2014 isolation design + safety assessment required before productization</b>"],
    ["VOX false-activation", "Bounded grammar + tunable VAD + retained PTT override (C.3a/D.3.2)", "Mitigations defined; ACO human-factors concurrence pending"],
    ["Installation", "STC / substantiated field approval (audio-panel interface \u2014 both input tap and isolated COM3 output \u2014 is more than minor); minor-alteration unlikely", "Per-aircraft; none performed"],
    ["Part 25 airframes", "STC (NORSEE excluded)", "Flagged"],
]
story.append(make_table(csm, [1.65*inch, 3.25*inch, 1.8*inch]))

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
    ["Speech stack", "Espressif <b>ESP-SR</b>: AFE (NS/<b>VAD &rarr; VOX</b>) &rarr; WakeNet \u201cHi ESP\u201d &rarr; MultiNet English"],
    ["<b>Crew audio input</b>", "<b>From the aircraft audio panel</b> on <b>I2S_NUM_0</b>, selectable per install: <b>analog</b> (isolated line tap &rarr; I2S codec ADC) or <b>digital</b> (I2S codec ADC fed from a buffered tap). Onboard MEMS mic = bench-test only"],
    ["Activation", "<b>VOX</b> (AFE VAD) primary, hands-free; <b>PTT</b> retained as manual override"],
    ["Audio output", f"<b>I2S_NUM_1</b> DAC &rarr; isolated line-level output stage (isolation transformer + line driver on the TX line) &rarr; <b>dedicated COM3-style audio-panel input channel</b>; crew hears checklist read-aloud in-headset. <b>Onboard speaker/amplifier removed.</b> A bench-test-only speaker output may optionally be provided in the development unit (not the installed configuration)."],
    ["Config storage", "<b>two microSD slots</b> \u2014 slot 1 <b>Config Card</b>, slot 2 <b>Data Card</b> (Part B), FAT32"],
    ["Annunciation", "Applied Avionics split-legend switch (dark-cockpit, AC 25-11B)"],
]
story.append(make_table(ovr, [1.6*inch, 5.1*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Two build paths: <b>Integrated</b> (ESP32-S3-Korvo-2 dev board \u2014 ES8311/ES7210 codec, "
    "microSD slot; line-in repurposed for the audio-panel receive feed; output stage wired to COM3 "
    "isolation transformer) or <b>DIY</b> (ESP32-S3 DevKitC-1 N16R8 + audio-panel input stage "
    "[isolation transformer + I2S codec ADC] + isolated audio output stage [I2S DAC &rarr; isolation "
    "transformer &rarr; line-level TX to COM3 channel] + <b>two</b> microSD breakouts + the annunciator "
    "switch). The earlier INMP441 MEMS mic and MAX98357A speaker-amp remain available only as "
    "bench-test items; neither is used in the installed configuration.", body))

story.append(Paragraph("D.2 &nbsp; Master pin map", h2))
pins = [
    ["Function", "Macro", "GPIO", "Dir", "Notes"],
    ["PTT <b>override</b>", "<font name='Mono' size='7.5'>PTT_GPIO</font>", "0", "in (PU)", "BOOT button; active-low; <b>force-listen</b> override of VOX"],
    ["SELECT switch", "<font name='Mono' size='7.5'>SELECT_GPIO</font>", "10", "in (PU)", "IN = GPIO&rarr;GND (active-low)"],
    ["Legend OFF (white)", "<font name='Mono' size='7.5'>LEGEND_OFF_GPIO</font>", "21", "out", "top legend half (via driver)"],
    ["Legend FAULT (amber)", "<font name='Mono' size='7.5'>LEGEND_FAULT_GPIO</font>", "14", "out", "bottom legend half (via driver)"],
    ["Status LED", "<font name='Mono' size='7.5'>STATUS_LED_GPIO</font>", "48", "out", "on-board RGB on most S3 devkits"],
    ["Audio-in bit clock", "<font name='Mono' size='7.5'>AIN_BCLK_GPIO</font>", "4", "out", "I2S0 BCLK &rarr; codec/mic SCK"],
    ["Audio-in word select", "<font name='Mono' size='7.5'>AIN_LRCLK_GPIO</font>", "5", "out", "I2S0 WS &rarr; codec/mic WS"],
    ["Audio-in data", "<font name='Mono' size='7.5'>AIN_DIN_GPIO</font>", "6", "in", "codec ADC / mic SD &rarr; ESP DIN"],
    ["Audio-in master clock", "<font name='Mono' size='7.5'>AIN_MCLK_GPIO</font>", "3", "out", "<b>MCLK to the codec</b> (ES8388/ES7210 need it; INMP441/PCM1808 do not)"],
    ["Codec I2C SDA", "<font name='Mono' size='7.5'>CODEC_SDA_GPIO</font>", "1", "i/o", "ES-series codec control bus (digital path)"],
    ["Codec I2C SCL", "<font name='Mono' size='7.5'>CODEC_SCL_GPIO</font>", "2", "out", "ES-series codec control bus (digital path)"],
    ["SD clock", "<font name='Mono' size='7.5'>SD_CLK_GPIO</font>", "7", "out", "SDMMC CLK (<b>shared</b> by both card slots)"],
    ["SD command", "<font name='Mono' size='7.5'>SD_CMD_GPIO</font>", "9", "i/o", "SDMMC CMD (needs pull-up)"],
    ["SD data 0", "<font name='Mono' size='7.5'>SD_D0_GPIO</font>", "8", "i/o", "SDMMC DAT0 (needs pull-up)"],
    ["Config-card detect", "<font name='Mono' size='7.5'>SD_CFG_CD_GPIO</font>", "47", "in (PU)", "slot-1 card-detect (Config Card)"],
    ["Data-card detect", "<font name='Mono' size='7.5'>SD_DAT_CD_GPIO</font>", "38", "in (PU)", "slot-2 card-detect (Data Card)"],
    ["Audio-out bit clock", "<font name='Mono' size='7.5'>AOUT_BCLK_GPIO</font>", "15", "out", "I2S1 BCLK &rarr; isolated audio-out (COM3) line driver/DAC"],
    ["Audio-out word select", "<font name='Mono' size='7.5'>AOUT_LRCLK_GPIO</font>", "16", "out", "I2S1 WS &rarr; isolated audio-out (COM3) line driver/DAC"],
    ["Audio-out data", "<font name='Mono' size='7.5'>AOUT_DOUT_GPIO</font>", "17", "out", "I2S1 DOUT &rarr; isolated audio-out (COM3) DIN; DAC &rarr; isolation transformer &rarr; line-level TX to COM3-style audio-panel channel. <b>Bench-test note:</b> a speaker-amp (e.g. MAX98357A) may be substituted here for bench testing only; not the installed output."],
]
story.append(make_table(pins, [1.35*inch, 1.55*inch, 0.45*inch, 0.55*inch, 2.8*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Polarity macros:</b> <font name='Mono' size='8'>PTT_ACTIVE_LOW=1</font>, "
    "<font name='Mono' size='8'>SELECT_ACTIVE_LOW=1</font>, <font name='Mono' size='8'>LEGEND_OFF_ACTIVE_HIGH=1</font>, "
    "<font name='Mono' size='8'>LEGEND_FAULT_ACTIVE_HIGH=1</font>, <font name='Mono' size='8'>STATUS_LED_ACTIVE_HIGH=1</font>, "
    "<font name='Mono' size='8'>LAMP_TEST_MS=2000</font>. Set any unused output to <font name='Mono' size='8'>-1</font> "
    "to disable it cleanly.", small))
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Two-slot SD note:</b> the demo shares one SDMMC 1-bit bus (CLK/CMD/DAT0) across both card slots, "
    "distinguished by per-slot <b>card-detect</b> lines and by mounting each at its own path "
    "(<font name='Mono' size='8'>/sdcard-config</font>, <font name='Mono' size='8'>/sdcard-data</font>). A "
    "production unit may instead give each slot its own SPI or SDMMC bus to remove any contention; the firmware "
    "reads Config first, then Data (B.4).", small))
story.append(Spacer(1, 4))
story.append(callout(
    "<b>Reserved / avoid pins (N16R8):</b> GPIO33\u201337 (octal PSRAM/flash bus \u2014 do not use), GPIO19/20 "
    "(USB D-/D+), GPIO0/45/46 (strapping \u2014 must boot in the right state), GPIO26\u201332 (SPI flash on some "
    "modules). GPIO0 here is only the BOOT/PTT button, so it is safe. GPIO1/2/3 are used here for the codec "
    "I2C + MCLK; on the Korvo-2 use that board's BSP assignments instead.", "warn"))

story.append(PageBreak())
story.append(Paragraph("D.3 &nbsp; Per-device wiring", h2))
story.append(Paragraph(
    "<b>D.3.1 Audio-panel input stage (the crew-audio source, I2S_NUM_0).</b> Crew speech comes from the "
    "<b>aircraft audio panel</b>, not an onboard mic. The source is chosen by the Config Card "
    "(<font name='Mono' size='8'>audio_source</font>); both paths terminate as an <b>I2S input</b> to the "
    "ESP32-S3 and feed the ESP-SR AFE.", bodyj))
story.append(bullets([
    "<b>Analog path (<font name='Mono' size='8'>analog</font>).</b> Tap a headphone/intercom/line output from "
    "the panel (aviation audio is typically ~150\u2013600 " + OHM + ", ~1\u20135 V RMS). Feed it through a "
    "<b>600 " + OHM + " audio ground-loop isolation transformer</b> (e.g. Allen Avionics AGL series) for "
    "galvanic isolation, then through a <b>~220\u2013470 " + OHM + " series resistor + simple RC anti-alias</b> "
    "into the <b>line-in of an I2S codec ADC</b> (ES8388/ES7210 with MCLK on GPIO3, I2C control on GPIO1/2; or "
    "PCM1808/CS5343 which self-clock). The tap is <b>high-impedance and parallel</b> so the panel sees a "
    "negligible load; the device cannot back-feed the panel. Scale the divider so panel line level maps to the "
    "codec's full-scale input without clipping.",
    "<b>Digital path (<font name='Mono' size='8'>digital</font>).</b> Where the codec sits closer to the "
    "source, take a buffered, <b>receive-only</b> I2S/line feed into the same codec ADC. This is a "
    "<b>receive-only</b> I2S/line feed \u2014 BCLK/WS/MCLK are generated by the ESP32 for the ADC only, "
    "and no data line is driven back toward any aircraft bus <i>via this input path</i>. (The separate "
    "audio output to the COM3 channel is on I2S_NUM_1 via a dedicated isolated output stage; see D.3.3a.)",
    "<b>Codec wiring:</b> SCK&rarr;GPIO4, WS&rarr;GPIO5, ADC_DATA&rarr;GPIO6, MCLK&rarr;GPIO3, I2C "
    "SDA/SCL&rarr;GPIO1/2; supply per the codec (1.8\u20133.3 V analog/digital rails); decouple each rail "
    "0.1 &micro;F.",
    "<b>Bench-test option only:</b> an <b>INMP441</b> MEMS mic may be wired in place of the codec for desk "
    "testing (VDD&rarr;3V3, SCK&rarr;GPIO4, WS&rarr;GPIO5, SD&rarr;GPIO6, L/R&rarr;GND, 100 k" + OHM + " "
    "pulldown on SD, never clock with VDD off). <b>This is not the installed audio source</b> and must not be "
    "used in an aircraft (it does not hear the panel and breaks the receive-from-panel model).",
]))
story.append(Paragraph(
    "<b>D.3.2 VOX &amp; PTT override.</b> Recognition is gated by the AFE <b>VAD</b> (VOX): the device listens "
    "whenever speech is detected on the panel feed, tuned by the Config Card "
    "(<font name='Mono' size='8'>vox.vad_sensitivity</font>, <font name='Mono' size='8'>vox.hangover_ms</font>). "
    "The <b>PTT</b> button (GPIO0, active-low) is a <b>force-listen override</b> \u2014 holding it opens "
    "recognition regardless of VAD, and with <font name='Mono' size='8'>vox.mode = ptt_only</font> it becomes "
    "the sole trigger (VOX disabled). PTT is debounced in software. There is <b>no PTT/keying line toward the "
    "aircraft</b> \u2014 this button only tells the device's own recognizer to listen.", bodyj))
story.append(Paragraph(
    "<b>D.3.3a Isolated audio output stage &rarr; COM3-style audio-panel channel (I2S_NUM_1).</b> "
    "The installed audio output is a galvanically-isolated, line-level output stage on I2S_NUM_1 "
    "(GPIO15 BCLK, GPIO16 LRC, GPIO17 DOUT). The output chain is: ESP32-S3 I2S DAC &rarr; "
    "I2S-to-analog DAC/line driver &rarr; a <b>line-level isolation transformer</b> on the TX output "
    "line &rarr; line-level output (600 " + OHM + " nominal or per the panel's COM3 input impedance) "
    "&rarr; dedicated COM3-style audio-panel input channel. The isolation transformer on the TX line "
    "provides galvanic isolation; a device fault (short, open, supply failure, output-stage failure) "
    "<b>cannot key, jam, load, or back-feed the panel's other channels or required COM radios</b>. "
    "Output level should be set conservatively so the injected advisory audio is clearly audible but "
    "does not mask required ATC/aircraft audio. "
    "<i>Judgment call / open item:</i> the exact I2S DAC part and isolation transformer type for the "
    "output stage must be confirmed by the bench engineer. Options include a small I2S DAC IC "
    "(e.g. PCM5102A class) followed by a 600&Omega;:600&Omega; aviation audio isolation transformer "
    "(Allen Avionics AGL series or equivalent). The <font name='Mono' size='8'>AOUT_BCLK/LRCLK/DOUT</font> "
    "macros (GPIO15/16/17) match the former speaker-amp I2S assignments; the firmware I2S_NUM_1 "
    "driver is retained \u2014 only the physical output hardware changes.", bodyj))
story.append(Paragraph(
    "<b>D.3.3b Bench-test speaker output (development/test only \u2014 not the installed output).</b> "
    "For bench verification of audio content before the isolated output stage is fitted, a "
    f"MAX98357A I2S Class-D amp may be wired on GPIO15/16/17: supply 2.5\u20135.5 V; ~2.4 mA "
    f"quiescent; peak ~650 mA at 5 V/4 {OHM}; no MCLK. VIN&rarr;5 V, GND&rarr;GND, "
    "BCLK&rarr;GPIO15, LRC&rarr;GPIO16, DIN&rarr;GPIO17, GAIN NC = 9 dB, SD/mode float = mono. "
    "<b>OUT+/OUT&minus; are bridge-tied \u2014 never to GND.</b> "
    "<b>This bench speaker is not routed to the aircraft audio panel and is NOT the installed "
    "audio output.</b>", bodyj))
story.append(Paragraph(
    "<b>D.3.4 Two microSD card slots &rarr; SDMMC 1-bit.</b> 3.3 V cards. Shared bus CLK&rarr;GPIO7, "
    "CMD&rarr;GPIO9 (10 k" + OHM + "&rarr;3V3), DAT0&rarr;GPIO8 (10 k" + OHM + "&rarr;3V3), VDD&rarr;3V3, "
    "VSS&rarr;GND. <b>Slot 1 = Config Card</b> (detect on GPIO47, mount "
    "<font name='Mono' size='8'>/sdcard-config</font>), <b>slot 2 = Data Card</b> (detect on GPIO38, mount "
    "<font name='Mono' size='8'>/sdcard-data</font>). FAT32; layouts per Part B. (Production option: separate "
    "bus per slot.)", bodyj))
story.append(Paragraph(
    "<b>D.3.5 Discrete inputs.</b> SELECT (GPIO10): LOW = selected IN; pull-up HIGH = OUT. PTT (GPIO0): "
    "LOW = pressed (override). Each is a simple SPST to GND; debounce in software.", body))

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
    ["<b>3.3 V</b>", "ESP32-S3 (Wi-Fi off) + audio codec + audio output DAC/line driver + <b>two</b> microSD slots", "~90\u2013180 mA", "~290 mA (SD init / SR burst)"],
    ["<b>5 V</b>", "Audio output line driver (if used; typically low-current line-level stage)", "a few mA", f"~50 mA (varies by line driver; <b>not the ~650 mA speaker-amp figure</b> \u2014 speaker amp removed)"],
    ["<b>Lamp rail</b>", "up to 2 legend halves", "0 (dark)", "per lamp spec (e.g. 28 V incand.)"],
]
story.append(make_table(pwr, [1.1*inch, 2.9*inch, 1.35*inch, 1.35*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "The audio-input codec (a few mA\u2013~20 mA) and the second microSD slot add a little to the 3.3 V rail; "
    "the isolation transformers (input and output) are passive. Power from <b>USB 5 V &ge; 1 A</b> (the "
    "removed MAX98357A was the dominant load; the new output stage is much lower current). Keep a 28 V "
    "legend supply separate from logic 5 V (grounds common only). Bulk decoupling &ge; 100 &micro;F near "
    "the output line driver (if applicable) plus 0.1 &micro;F per device. The audio-panel tap draws "
    "<b>no power from the aircraft</b> and is isolated from the device's own grounds through the "
    "transformer (analog path); the audio-panel output stage is similarly isolated.", body))

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
    ["Components", "<font name='Mono' size='8'>esp-sr</font>, <font name='Mono' size='8'>esp_spiffs</font>, <font name='Mono' size='8'>driver</font>, <font name='Mono' size='8'>json</font> (cJSON), <font name='Mono' size='8'>fatfs</font>, <font name='Mono' size='8'>sdmmc</font>, <font name='Mono' size='8'>esp_driver_sdmmc</font>, <font name='Mono' size='8'>esp_codec_dev</font> (codec init for the digital/analog path)"],
    ["Speech models", "WakeNet <font name='Mono' size='8'>WN9_HIESP</font>; MultiNet English <font name='Mono' size='8'>mn6_en</font>/<font name='Mono' size='8'>mn7_en</font> (S3 only)"],
    ["Partitions", "factory app 3 MB + model 5 MB + storage 2 MB &rarr; needs <b>16 MB</b> flash (N16R8)"],
    ["Audio input", "ESP-SR AFE fed from I2S0 (codec ADC); <b>VAD&rarr;VOX</b> gating, PTT override; codec init from Config Card <font name='Mono' size='8'>audio.codec</font>"],
    ["Two-card load", "Config Card first (<font name='Mono' size='8'>/sdcard-config/config.json</font>) &rarr; init audio source + VOX &rarr; then matching Data Card folder (<font name='Mono' size='8'>/sdcard-data/&lt;aircraft&gt;/</font>)"],
    ["Grammar rules", "lowercase + single spaces; spell numbers (\u201cv one\u201d); ~200-cmd cap"],
    ["Fault behavior", "any card/config fault &rarr; <font name='Mono' size='8'>ST_FAULT</font>, amber legend, <b>no checklist shown</b> (B.4)"],
]
story.append(make_table(fw, [1.5*inch, 5.2*inch]))

story.append(Paragraph("D.9 &nbsp; Bill of materials (DIY build)", h2))
bom = [
    ["Qty", "Part", "Spec / example"],
    ["1", "ESP32-S3 DevKit", "DevKitC-1 <b>N16R8</b> (PSRAM)"],
    ["1", "<b>Audio-panel input codec</b>", "I2S codec ADC with line-in: <b>ES8388 / ES7210</b> (need MCLK+I2C) or <b>PCM1808 / CS5343</b> (self-clocking)"],
    ["1", "<b>Audio isolation transformer</b>", f"600 {OHM}:600 {OHM} aviation audio ground-loop isolator (<b>Allen Avionics AGL</b> series)"],
    ["1", "Input network", f"~220\u2013470 {OHM} series resistor + RC anti-alias for the analog tap"],
    ["1", "<b>Audio output isolation transformer</b>", f"600 {OHM}:600 {OHM} line-level isolation transformer for the TX output stage (e.g. <b>Allen Avionics AGL series</b> or equivalent) \u2014 galvanic barrier on the COM3 output line"],
    ["1", "<b>Audio output DAC / line driver</b>", "I2S DAC IC (e.g. PCM5102A class) or I2S-in line driver for the COM3 output stage; select based on output impedance and level requirements for the panel's COM3 input"],
    ["<i>(bench only)</i>", "I2S amp (bench test)", "MAX98357A breakout \u2014 bench-test use only; not installed"],
    ["<i>(bench only)</i>", "Speaker (bench test)", f"4\u20138 {OHM}, &ge; 2 W \u2014 bench-test use only; not installed"],
    ["<b>2</b>", "microSD card + breakout", "FAT32 \u2014 <b>Config Card</b> (slot 1) + <b>Data Card</b> (slot 2)"],
    ["1", "Annunciator switch", "Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench)"],
    ["2", "Lamp driver", "logic-level N-MOSFET (2N7002/AO3400) or NPN (2N2222)"],
    ["4", "Resistors", f"1 k{OHM} &times;2 (gate), 10 k{OHM} &times;2 (pulldown)"],
    ["2\u20134", "Pull-ups", f"10 k{OHM} on SD CMD/DAT0; codec I2C pull-ups if needed"],
    ["\u2014", "Caps", "0.1 &micro;F per device/rail, 100 &micro;F bulk near output line driver (if applicable)"],
    ["1", "PTT button", "momentary SPST (or use BOOT) \u2014 <b>VOX override</b>"],
    ["(opt.)", "INMP441 MEMS mic", "<b>bench-test input only</b>, not the installed source"],
]
story.append(make_table(bom, [0.55*inch, 1.85*inch, 4.3*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Integrated alternative: <b>ESP32-S3-Korvo-2</b> (~$45\u201355) provides codec/SD on-board; use its BSP "
    "pin map and codec (ES8311/ES7210) init, repurpose its line-in for the audio-panel receive feed, and "
    "add the isolated COM3 output stage externally (DAC/line driver + output isolation transformer). "
    "A production unit adds the second card slot.", small))

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
    story.append(Paragraph("Complete system wiring \u2014 ESP32-S3, audio input, amp, two microSD cards (Config + "
                           "Data), and split-legend annunciator with per-half lamp drivers.", cap))

# ================= PART E =================
story.append(PageBreak())
story += part_divider("E", "Enclosure Specification",
    "For the fabricating engineer. The housing is generic \u2014 sized for the electronics and the panel "
    "interface, not for a specific airframe. The only airframe-specific item is the mounting variant "
    "(DZUS slot vs. round instrument hole) and the card inside it.")

story.append(Paragraph("E.1 &nbsp; Two-piece architecture", h2))
arch2 = [
    ["Piece", "Contents", "Where", "Why"],
    ["<b>A. Panel bezel</b>", "Split-legend annunciator switch, <b>PTT override</b> button", "Front panel / pedestal, on the <b>DZUS rail</b>", "Crew must see/reach it; dark-cockpit annunciator in the normal scan. Speaker grille removed (no onboard speaker in the installed design)."],
    ["<b>B. Remote processor box</b>", "ESP32-S3, audio-input stage (isolation transformer + codec), <b>audio output stage</b> (DAC/line driver + isolation transformer for COM3 TX output), <b>two microSD card slots</b>, lamp-driver, power conditioning", "Avionics bay / behind-panel, blind", "Keeps heat, the card slots, and wiring out of the panel; close to the audio-panel tap and COM3 output point"],
]
story.append(make_table(arch2, [1.05*inch, 2.5*inch, 1.5*inch, 1.65*inch]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "A single all-in-one box is acceptable for a pure bench demo, but the two-piece split mirrors real "
    "remote-mount avionics and keeps the audio-input stage near the panel tap.", body))

story.append(Paragraph("E.2 &nbsp; Piece A \u2014 panel bezel", h2))
story.append(bullets([
    "<b>DZUS rail mount:</b> fastener pitch <b>3/8 in (9.525 mm)</b>; clearance hole <b>0.255 in (6.48 mm)</b>; "
    "bezel height a whole multiple of 3/8 in (target 3-unit = <b>28.575 mm</b> \u2014 the speaker cone space is "
    "freed so the 4-unit height is no longer needed unless a larger switch requires it; confirm against the "
    "chosen switch datasheet); standard pedestal width <b>&asymp; 146 mm</b> aluminum (144.45 mm face); backplate "
    "<b>1/16 in (1.6 mm)</b> 6061-T6; first/last fastener <b>14.29 mm</b> from each end.",
    "<b>Round-hole variant:</b> fits a standard <b>3-1/8 in (79.4 mm)</b> instrument cutout with four 6-32 "
    "screws on the standard bolt circle, to replace a blanking plate where no DZUS slot exists.",
    "<b>Face layout (top&rarr;bottom):</b> split-legend annunciator switch (cut per the <i>specific</i> switch "
    "datasheet \u2014 typical VIVISUN bezel &asymp; 15&times;15 mm to 19&times;19 mm; top half <font name='Mono' "
    "size='8'>VOICE CHKLST OFF</font> white, bottom <font name='Mono' size='8'>VOICE CHKLST FAULT</font> amber, "
    "upright when installed); optional guarded/recessed PTT. <b>No speaker grille</b> \u2014 the onboard speaker "
    "is removed; checklist audio plays through the crew headsets via the COM3 output channel. The bezel "
    "height may be reduced from the prior 4-unit to 3-unit (28.575 mm) since the speaker cone space is freed.",
    "<b>Material/finish:</b> 6061-T6 aluminum 2.0\u20133.0 mm (or ABS/PC for a non-structural demo); <b>matte "
    "black, low-gloss (&le; 10 gloss units)</b> to suppress glare; legend by the switch's internal engraving "
    "(preferred) or laser-etch + white/amber paint-fill; edges chamfered 0.5 mm.",
]))

story.append(Paragraph("E.3 &nbsp; Piece B \u2014 remote processor box", h2))
story.append(bullets([
    "<b>Envelope:</b> sized around the ESP32-S3 DevKitC-1 (&asymp; 70&times;26 mm) plus the audio-input stage "
    "(codec + input isolation transformer), the audio output stage (DAC/line driver + output isolation "
    "transformer), <b>two</b> microSD breakouts, and the 2-channel lamp-driver; practical outer "
    "<b>&asymp; 120 &times; 85 &times; 45 mm</b> (unchanged \u2014 the output stage is compact; confirm against "
    "the actual stacked board set with both transformers). Note: without the speaker-amp the box is "
    "likely lighter and slightly cooler.",
    "<b>Mounting:</b> internal standoffs / M2.5 brass inserts \u2014 boards screwed down, not floating "
    "(vibration). Keep the audio-input and output stages and their shielded cabling away from the "
    "switching DC-DC; route input and output audio cables separately, both shielded; the isolation "
    "transformer mounts solidly (it is a magnetic part).",
    "<b>Card slots:</b> <b>two externally-swappable microSD carriers</b>, clearly and distinctly labeled "
    "<font name='Mono' size='8'>CONFIG CARD \u2014 FAT32</font> (slot 1) and <font name='Mono' size='8'>DATA "
    "CARD \u2014 FAT32</font> (slot 2), keyed or spaced so they cannot be confused/swapped; both swappable "
    "without opening the box. The Config Card carrier should accept a <b>write-protect-locked</b> card.",
    "<b>Access &amp; connectors:</b> covered/recessed <b>USB-C</b> service port (bench use only); one keyed, "
    "positive-latching main connector (small MIL-circular or D-sub) carrying SELECT, both legend drives, PTT, "
    "power/ground (pinout from <font name='Mono' size='8'>board_pins.h</font>); <b>plus a separate, shielded, "
    "clearly-labeled <font name='Mono' size='8'>AUDIO IN \u2014 ISOLATED, RX ONLY</font> connector</b> for the "
    "audio-panel tap \u2014 kept on its own keyed connector so it can never be mis-mated to power, with the "
    "input isolation transformer <b>inside</b> the box on the panel side of the codec; <b>and a separate, "
    "shielded, clearly-labeled <font name='Mono' size='8'>AUDIO OUT \u2014 ISOLATED (COM3)</font> connector</b> "
    "for the isolated TX output to the audio-panel COM3-style channel \u2014 on its own keyed connector, "
    "physically distinct from the input connector, with the output isolation transformer inside the box "
    "on the panel side of the output stage. The two audio connectors must be clearly distinct "
    "and cannot be mis-mated. "
    "Accept USB 5 V &ge; 1 A; optional internal <b>28 V&rarr;5 V DC-DC</b> (&ge; 1 A; speaker-amp is removed) "
    "with TVS + fuse if a 28 V bus mock-up is wanted (mark as demo regulator, not DO-160 qualified).",
    "<b>Material/EMI:</b> aluminum preferred (doubles as EMI shield + heatsink); if plastic, add a grounded "
    "conductive shield liner/coating; single-point chassis ground stud bonded to the connector shell and "
    "ESP32 ground. Route the audio-in shield per the panel's grounding practice (often <b>grounded only at the "
    "intercom</b> \u2014 see C.3a).",
]))

story.append(PageBreak())
story.append(Paragraph("E.4 &nbsp; Audio, thermal, environmental, labeling", h2))
story.append(bullets([
    "<b>Audio:</b> No onboard speaker in the installed design \u2014 speaker/grille removed from both pieces. "
    "Checklist read-aloud audio is delivered in-headset via the isolated COM3 output channel. If a "
    "bench-test speaker output is optionally fitted on the development unit (see D.3.3b), it may be "
    "wired to a header on the processor box only; no speaker cutout on the panel bezel.",
    "<b>Thermal:</b> ESP32-S3 + ESP-SR is low-power (a few hundred mW) \u2014 <b>no fan</b>. Passive convection "
    "(vent slots low/high) or conduction (thermal pad to the aluminum wall). If sealed, verify internal rise "
    "&lt; 20 &deg;C above 55 &deg;C ambient. DC-DC (if fitted) on its own thermal path.",
    "<b>Environmental:</b> design toward the DO-160G categories in <b>C.4</b> (Cat A2 temp, Cat S vibration, "
    "etc.) \u2014 design guidance for the prototype, formal test for a productized unit.",
    "<b>Labeling:</b> placard <font name='Mono' size='8'>DEMO / TRAINING ONLY \u2014 NOT FOR FLIGHT</font>; box "
    "exterior carries unit name, serial/asset field, the <b>two card-slot labels</b> (<font name='Mono' "
    "size='8'>CONFIG CARD</font> / <font name='Mono' size='8'>DATA CARD</font>, FAT32), the <font name='Mono' "
    "size='8'>AUDIO IN \u2014 ISOLATED, RX ONLY</font> connector marking (receive-only input tap), the "
    "<font name='Mono' size='8'>AUDIO OUT \u2014 ISOLATED, COM3</font> connector marking (TX output to "
    "audio-panel COM3 channel), and the USB \u201cbench use only\u201d "
    "note; annunciator legends <font name='Mono' size='8'>VOICE CHKLST OFF</font> (white) / <font name='Mono' "
    "size='8'>VOICE CHKLST FAULT</font> (amber); amber = caution, white = status per AC 25-11B.",
]))

story.append(Paragraph("E.5 &nbsp; Deliverables &amp; open items for the engineer", h2))
story.append(Paragraph(
    "<b>Deliverables:</b> STEP + native 3D CAD of both pieces (boards + switch modeled in place); "
    "fully-dimensioned 2D drawings (DZUS pattern, switch cutout from the chosen datasheet, connector "
    "cutouts; GD&amp;T on the switch cutout and DZUS holes); connector pinout mapped to <font name='Mono' "
    "size='8'>board_pins.h</font>; an FDM/SLA printable prototype for fit-check; a mechanical BOM; tolerances "
    "(switch cutout &plusmn;0.1 mm, DZUS holes &plusmn;0.1 mm on the 9.525 mm pitch, general &plusmn;0.25 mm).", body))
story.append(callout(
    "<b>Open items (confirm before CAD):</b> the <b>exact Applied Avionics switch part number</b> \u2014 the single "
    "most critical dimension; nothing finalizes until it is fixed. Also: DZUS slot vs. 3-1/8 in round hole in "
    "the target panel; the <b>audio-panel tap point, level, and grounding</b> for the target installation (sets "
    "the input isolation-transformer + divider design); the <b>codec part</b> for the digital path (sets the "
    "I2C/MCLK init); the <b>audio-panel COM3-style output channel injection point, impedance, and level "
    "requirements</b> (sets the output isolation transformer and line driver design \u2014 this is a critical "
    "open item for the output stage); the <b>output DAC/line driver part</b> (sets the COM3 output stage "
    "component selection); whether a 28 V input is wanted. No speaker \u2014 the speaker is removed.", "warn"))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Reference dimensions:</b> DZUS pitch 9.525 mm &middot; DZUS hole 6.48 mm &middot; backplate 1.6 mm "
    "&middot; first fastener offset 14.29 mm &middot; pedestal panel width &asymp; 146 mm &middot; round "
    "instrument hole 79.4 mm &middot; remote box &asymp; 120 &times; 85 &times; 45 mm &middot; two microSD slots "
    "&middot; isolated <font name='Mono' size='8'>AUDIO IN (RX ONLY)</font> connector (input tap) "
    "&middot; isolated <font name='Mono' size='8'>AUDIO OUT (COM3)</font> connector (TX output to "
    "audio-panel COM3 channel) &middot; no onboard speaker in the installed design.", small))

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
    ("Allen Avionics AGL audio ground-loop isolation transformers (analog audio-panel tap)", "https://www.allenavionics.com/categories/agl-audio-ground-loop-isolation-transformers"),
    ("Everest-Semi ES8388 audio codec (line-in I2S ADC, MCLK + I2C)", "https://dl.radxa.com/rock2/docs/hw/datasheet/ES8388%20user%20Guide.pdf"),
    ("ES7210 multichannel audio ADC (Espressif-supported codec)", "https://docs.espressif.com/projects/esp-adf/en/latest/design-guide/dev-boards/board-esp32-s3-korvo-2.html"),
    ("TI PCM1808 stereo audio ADC (self-clocking I2S input)", "https://www.ti.com/lit/ds/symlink/pcm1808.pdf"),
    ("Espressif ESP-SR AFE / VAD (voice-activity detection for VOX)", "https://github.com/espressif/esp-sr"),
    ("INMP441 microphone datasheet (bench-test option only)", "https://www.farnell.com/datasheets/1824785.pdf"),
    ("MAX98357A amplifier datasheet (Analog Devices) (bench-test amp only)", "https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf"),
    ("MAX98357A breakout guide (Adafruit) (bench-test amp only)", "https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf"),
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
    canvas.drawString(ML, PAGE_H - 2.85*inch, "Generic advisory reader \u00b7 audio-panel input \u00b7 Config + Data cards")
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
