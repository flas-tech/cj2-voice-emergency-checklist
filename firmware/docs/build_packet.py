#!/usr/bin/env python3
"""Build the comprehensive CJ2 Voice Emergency Checklist technical packet (PDF)."""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    NextPageTemplate, PageBreak, Image, KeepTogether, ListFlowable, ListItem, HRFlowable,
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

FONTS = "/home/user/workspace/fonts"
DOCS = "/home/user/workspace/cj2-checklist/firmware/docs"
OUT = os.path.join(DOCS, "CJ2_Voice_Checklist_Tech_Packet.pdf")

# ---- fonts ----
pdfmetrics.registerFont(TTFont("DM", f"{FONTS}/DMSans-Regular-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-B", f"{FONTS}/DMSans-Bold-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-M", f"{FONTS}/DMSans-Medium-static.ttf"))
pdfmetrics.registerFont(TTFont("DM-I", f"{FONTS}/DMSans-Italic-static.ttf"))
pdfmetrics.registerFont(TTFont("Mono", f"{FONTS}/JetBrainsMono-Regular-static.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B", f"{FONTS}/JetBrainsMono-Bold-static.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
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
WHITEHL = colors.HexColor("#1B474D")
HEADER_BG = colors.HexColor("#0C4E54")
ROW_ALT = colors.HexColor("#F1F0EB")

PAGE_W, PAGE_H = letter
ML = MR = 0.85 * inch
MT = 0.9 * inch
MB = 0.85 * inch

# ---- styles ----
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
mono = S("mono", fontName="Mono", fontSize=8, leading=11.5, textColor=INK)
cell = S("cell", fontName="DM", fontSize=8.3, leading=11, textColor=INK)
cellb = S("cellb", fontName="DM-B", fontSize=8.3, leading=11, textColor=INK)
cellmono = S("cellmono", fontName="Mono", fontSize=7.8, leading=10.5, textColor=INK)
cellhdr = S("cellhdr", fontName="DM-B", fontSize=8.3, leading=11, textColor=colors.white)
link = S("link", parent=body)
warn = S("warn", fontName="DM-B", fontSize=9.5, leading=13, textColor=AMBER)
foot = S("foot", fontName="DM", fontSize=7.5, leading=10, textColor=FAINT)

def A(text, url):
    return f'<a href="{url}" color="#01696F">{text}</a>'

# ---- table helpers ----
def make_table(data, col_widths, header=True, font_styles=None, align_cols=None):
    """data: list of rows; each cell is a string (wrapped in Paragraph) or Paragraph."""
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

def codeblock(text):
    p = Paragraph(text.replace(" ", "&nbsp;").replace("\n", "<br/>"), mono)
    t = Table([[p]], colWidths=[PAGE_W - ML - MR])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1C1B19")),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#393836")),
    ]))
    # override mono color to light
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

# ---- document with sections ----
story = []

def hr():
    return HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceBefore=10, spaceAfter=10)

# ============ COVER (handled by page template) ============
story.append(NextPageTemplate("toc"))
story.append(PageBreak())

# ============ TOC ============
story.append(Paragraph("Contents", h1))
story.append(Spacer(1, 4))
toc_items = [
    ("1", "System Overview", "3"),
    ("2", "Master Pin Map", "3"),
    ("3", "Per-Device Wiring", "4"),
    ("4", "Annunciator Switch & Lamp Driver", "6"),
    ("5", "Power Budget & Supply", "7"),
    ("6", "Bill of Materials", "8"),
    ("7", "ESP32-S3-Korvo-2 Differences", "8"),
    ("8", "Firmware Build & Behavior", "9"),
    ("9", "Processor Selection", "10"),
    ("10", "microSD Configuration & JSON Schema", "12"),
    ("11", "CJ2 Checklist Library", "13"),
    ("12", "Wiring Diagram", "15"),
    ("13", "Source References", "16"),
]
toc_rows = []
for num, title, pg in toc_items:
    toc_rows.append([
        Paragraph(f'<font name="DM-B" color="#01696F">{num}</font>', cell),
        Paragraph(f'<font name="DM-M">{title}</font>', cell),
        Paragraph(f'<font color="#5A5852">{pg}</font>', S("r", parent=cell, alignment=2)),
    ])
tt = Table(toc_rows, colWidths=[0.4*inch, 5.2*inch, 0.6*inch])
tt.setStyle(TableStyle([
    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ("LINEBELOW",(0,0),(-1,-1),0.3,BORDER),
    ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
    ("LEFTPADDING",(0,0),(-1,-1),2),
]))
story.append(tt)
story.append(Spacer(1, 18))
story.append(callout("DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS. This is a bench/educational prototype. It is not airworthy, not certified, and must never be installed in or relied upon aboard an aircraft.", "warn"))

story.append(NextPageTemplate("main"))
story.append(PageBreak())

# ============ 1. SYSTEM OVERVIEW ============
story.append(Paragraph("1 &nbsp; System Overview", h1))
story.append(Paragraph(
    "An offline, on-device voice-driven emergency checklist reader for the Cessna Citation CJ2 (CE 525A). "
    "The pilot states an emergency by name; the device reads each checklist item aloud from pre-recorded audio "
    "and waits for the spoken completion word before advancing. It runs entirely on an ESP32-S3 using Espressif's "
    "ESP-SR speech framework (WakeNet wake word + MultiNet offline English command recognition) \u2014 no cloud, no "
    "Wi-Fi, no phone. All GPIO numbers in this packet match <font name='Mono' size='8.5'>main/board_pins.h</font>.", bodyj))

ov = [
    ["Item", "Value"],
    ["MCU", "<b>ESP32-S3</b> (dual-core LX7 @ 240 MHz) \u2014 <b>PSRAM required</b> by ESP-SR"],
    ["Recommended module", "ESP32-S3-WROOM-1 <b>N16R8</b> (16 MB flash, 8 MB octal PSRAM)"],
    ["Speech stack", "Espressif <b>ESP-SR</b>: AFE (NS/VAD) \u2192 WakeNet \u201cHi ESP\u201d \u2192 MultiNet English"],
    ["Mic input", "I2S MEMS microphone on <b>I2S_NUM_0</b>"],
    ["Audio output", "I2S Class-D amplifier on <b>I2S_NUM_1</b> \u2192 4\u20138 \u2126 speaker"],
    ["Config storage", "<b>microSD</b> (SDMMC 1-bit), FAT32, one folder per aircraft"],
    ["Annunciation", "Applied Avionics split-legend switch (dark-cockpit, FAA AC 25-11)"],
    ["Logic level", "<b>3.3 V</b> (ESP32-S3 is <b>not</b> 5 V tolerant on GPIO)"],
]
story.append(make_table(ov, [1.7*inch, 5.0*inch]))
story.append(Spacer(1, 8))
story.append(Paragraph("Two build paths are supported:", body))
story.append(ListFlowable([
    ListItem(Paragraph("<b>Integrated:</b> ESP32-S3-Korvo-2 dev board (on-board dual mic, ES8311 codec, NS4150 amp, microSD slot). Least wiring; best mic performance.", body), leftIndent=6),
    ListItem(Paragraph("<b>DIY (this document):</b> ESP32-S3 DevKitC-1 N16R8 + INMP441 mic + MAX98357A amp + microSD breakout + the annunciator switch.", body), leftIndent=6),
], bulletType="bullet", start="circle", leftIndent=14))

# ============ 2. MASTER PIN MAP ============
story.append(Paragraph("2 &nbsp; Master Pin Map", h1))
story.append(Paragraph("All GPIO assignments from <font name='Mono' size='8.5'>main/board_pins.h</font>.", small))
story.append(Spacer(1, 6))
pin = [
    ["Function", "Macro", "GPIO", "Dir", "Notes"],
    ["Push-to-talk", "PTT_GPIO", "0", "in (PU)", "BOOT button; active-low"],
    ["SELECT switch", "SELECT_GPIO", "10", "in (PU)", "IN = GPIO\u2192GND (active-low)"],
    ["Legend OFF (white)", "LEGEND_OFF_GPIO", "21", "out", "drives top legend half (via driver)"],
    ["Legend FAULT (amber)", "LEGEND_FAULT_GPIO", "14", "out", "drives bottom legend half (via driver)"],
    ["Status LED", "STATUS_LED_GPIO", "48", "out", "on-board RGB on most S3 devkits"],
    ["Mic bit clock", "MIC_BCLK_GPIO", "4", "out", "I2S0 BCLK \u2192 mic SCK"],
    ["Mic word select", "MIC_LRCLK_GPIO", "5", "out", "I2S0 WS \u2192 mic WS"],
    ["Mic data in", "MIC_DIN_GPIO", "6", "in", "mic SD \u2192 ESP DIN"],
    ["SD clock", "SD_CLK_GPIO", "7", "out", "SDMMC CLK"],
    ["SD command", "SD_CMD_GPIO", "9", "i/o", "SDMMC CMD (needs pull-up)"],
    ["SD data 0", "SD_D0_GPIO", "8", "i/o", "SDMMC DAT0 (needs pull-up)"],
    ["Speaker bit clock", "SPK_BCLK_GPIO", "15", "out", "I2S1 BCLK \u2192 amp BCLK"],
    ["Speaker word select", "SPK_LRCLK_GPIO", "16", "out", "I2S1 WS \u2192 amp LRC"],
    ["Speaker data out", "SPK_DOUT_GPIO", "17", "out", "I2S1 DOUT \u2192 amp DIN"],
]
fs = {}
for i in range(1, len(pin)):
    fs[(i,1)] = cellmono
    fs[(i,2)] = cellmono
story.append(make_table(pin, [1.5*inch, 1.55*inch, 0.5*inch, 0.65*inch, 2.5*inch], font_styles=fs))
story.append(Spacer(1, 7))
story.append(Paragraph("<b>Polarity macros</b> (flip to match your hardware): <font name='Mono' size='8'>PTT_ACTIVE_LOW=1, SELECT_ACTIVE_LOW=1, LEGEND_OFF_ACTIVE_HIGH=1, LEGEND_FAULT_ACTIVE_HIGH=1, STATUS_LED_ACTIVE_HIGH=1, LAMP_TEST_MS=2000</font>. Set any unused output to <font name='Mono' size='8'>-1</font> to disable it cleanly.", body))
story.append(Paragraph("Reserved / avoid pins (ESP32-S3-WROOM-1 N16R8)", h3))
res = [
    ["Pins", "Reason"],
    ["GPIO33\u201337", "Octal PSRAM/flash internal bus \u2014 <b>do not use</b> on R8 modules"],
    ["GPIO19, GPIO20", "USB D-/D+ (native USB / USB-Serial-JTAG)"],
    ["GPIO0, 45, 46", "Strapping pins \u2014 usable but must be in the correct state at boot"],
    ["GPIO26\u201332", "SPI flash on some modules \u2014 verify your board"],
]
fs2 = {(i,0): cellmono for i in range(1,len(res))}
story.append(make_table(res, [1.6*inch, 5.1*inch], font_styles=fs2))
story.append(Spacer(1,4))
story.append(Paragraph("GPIO0 is used here only as the BOOT/PTT button (its natural strapping use), so it is safe. None of the chosen pins conflict with the reserved set.", small))

# ============ 3. PER-DEVICE WIRING ============
story.append(PageBreak())
story.append(Paragraph("3 &nbsp; Per-Device Wiring", h1))

story.append(Paragraph("3.1 &nbsp; INMP441 MEMS Microphone \u2192 ESP32-S3 (I2S_NUM_0)", h3))
story.append(Paragraph("Supply <b>1.8\u20133.3 V</b> (never 5 V), ~2.2\u20132.5 mA at 3.3 V. " + A("INMP441 datasheet", "https://www.farnell.com/datasheets/1824785.pdf") + ".", body))
mic = [
    ["INMP441 pin", "Connects to", "Net"],
    ["VDD", "ESP <b>3V3</b>", "3.3 V"],
    ["GND", "ESP <b>GND</b>", "GND"],
    ["SCK", "ESP <b>GPIO4</b> (BCLK)", "mic I2S"],
    ["WS", "ESP <b>GPIO5</b> (WS)", "mic I2S"],
    ["SD", "ESP <b>GPIO6</b> (DIN)", "mic I2S"],
    ["L/R", "<b>GND</b>", "selects <b>left</b> channel"],
]
story.append(make_table(mic, [1.5*inch, 3.0*inch, 2.2*inch]))
story.append(Spacer(1,4))
story.append(ListFlowable([
    ListItem(Paragraph("Decouple VDD\u2192GND with <b>0.1 \u00b5F</b> close to the module.", small), leftIndent=6),
    ListItem(Paragraph("Add a <b>100 k\u2126 pulldown</b> on the SD line (datasheet-recommended to discharge the bus when tri-stated). Most breakouts include it.", small), leftIndent=6),
    ListItem(Paragraph("Do <b>not</b> clock WS/SCK with VDD unpowered (stresses ESD diodes).", small), leftIndent=6),
], bulletType="bullet", leftIndent=14))

story.append(Paragraph("3.2 &nbsp; MAX98357A Class-D Amplifier \u2192 ESP32-S3 (I2S_NUM_1)", h3))
story.append(Paragraph("Supply <b>2.5\u20135.5 V</b>; 2.4 mA quiescent; peak speaker current up to <b>~650 mA</b> at 5 V/4 \u2126. No MCLK required. " + A("Analog Devices datasheet", "https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf") + ", " + A("Adafruit guide", "https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf") + ".", body))
amp = [
    ["MAX98357A pin", "Connects to", "Net"],
    ["VIN", "<b>5 V</b> (USB/VBUS) for full output (3.3 V also works, less power)", "5 V"],
    ["GND", "ESP <b>GND</b>", "GND"],
    ["BCLK", "ESP <b>GPIO15</b>", "spk I2S"],
    ["LRC", "ESP <b>GPIO16</b>", "spk I2S"],
    ["DIN", "ESP <b>GPIO17</b>", "spk I2S"],
    ["GAIN", "<b>NC</b> = 9 dB (default)", "\u2014"],
    ["SD (mode)", "<b>float</b> = mono (L+R)/2", "\u2014"],
    ["OUT+/OUT\u2212", "speaker (4\u20138 \u2126) \u2014 bridge-tied, no ground ref", "\u2014"],
]
story.append(make_table(amp, [1.5*inch, 3.9*inch, 1.3*inch]))
story.append(Spacer(1,4))
story.append(ListFlowable([
    ListItem(Paragraph("<b>GAIN options:</b> 100 k\u2126\u2192GND = 15 dB; \u2192GND = 12 dB; <b>NC = 9 dB</b>; \u2192VIN = 6 dB; 100 k\u2126\u2192VIN = 3 dB.", small), leftIndent=6),
    ListItem(Paragraph("<b>SD/mode pin:</b> &lt;0.16 V = shutdown; 0.16\u20130.77 V = (L+R)/2 mono; 0.77\u20131.4 V = right; &gt;1.4 V = left. Breakouts usually float it to mono.", small), leftIndent=6),
    ListItem(Paragraph("The OUT pins are <b>bridge-tied</b> \u2014 never connect either to GND.", small), leftIndent=6),
], bulletType="bullet", leftIndent=14))

story.append(Paragraph("3.3 &nbsp; microSD Card \u2192 ESP32-S3 (SDMMC, 1-bit)", h3))
story.append(Paragraph("<b>3.3 V</b> card. Sleep ~100\u2013200 \u00b5A; init/read peaks <b>50\u2013200 mA</b>. " + A("SD current notes", "https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975") + ".", body))
sd = [
    ["SD signal", "ESP32-S3", "Net", "Pull-up"],
    ["CLK", "<b>GPIO7</b>", "microSD", "\u2014"],
    ["CMD", "<b>GPIO9</b>", "microSD", "<b>10 k\u2126 \u2192 3V3</b>"],
    ["DAT0", "<b>GPIO8</b>", "microSD", "<b>10 k\u2126 \u2192 3V3</b>"],
    ["VDD", "<b>3V3</b>", "3.3 V", "\u2014"],
    ["VSS", "<b>GND</b>", "GND", "\u2014"],
]
story.append(make_table(sd, [1.4*inch, 1.6*inch, 1.6*inch, 2.1*inch]))
story.append(Spacer(1,4))
story.append(ListFlowable([
    ListItem(Paragraph("1-bit mode uses only DAT0 (DAT1\u20133 unused). For 4-bit, add DAT1/2/3 with pull-ups.", small), leftIndent=6),
    ListItem(Paragraph("Keep CLK trace short; SDMMC runs at MHz clocks. Format <b>FAT32</b>.", small), leftIndent=6),
], bulletType="bullet", leftIndent=14))

story.append(Paragraph("3.4 &nbsp; Discrete Inputs", h3))
di = [
    ["Input", "ESP32-S3", "Active", "Idle"],
    ["SELECT switch (IN/OUT)", "<b>GPIO10</b>", "LOW = selected IN", "internal PU \u2192 HIGH = OUT"],
    ["Push-to-talk", "<b>GPIO0</b>", "LOW = pressed", "internal PU \u2192 HIGH"],
]
story.append(make_table(di, [2.0*inch, 1.2*inch, 1.7*inch, 1.8*inch]))
story.append(Spacer(1,4))
story.append(Paragraph("Wire each as a simple SPST contact to <b>GND</b>. No external resistor needed (internal pull-ups enabled in firmware). Debounce is handled in software.", small))

# ============ 4. ANNUNCIATOR ============
story.append(PageBreak())
story.append(Paragraph("4 &nbsp; Annunciator Switch & Lamp Driver", h1))
story.append(Paragraph("Applied Avionics split-legend switch with two independently driven legend halves, following dark-cockpit philosophy per " + A("FAA AC 25-11B", "https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf") + " and the " + A("AEA design guidance", "https://aea.net/AvionicsNews/ANArchives/DesignDisplayOct03.pdf") + ".", bodyj))
ann = [
    ["State", "TOP \u2014 white VOICE CHKLST OFF", "BOTTOM \u2014 amber VOICE CHKLST FAULT"],
    ["Selected <b>IN</b>, healthy", "dark", "dark \u2190 true dark cockpit"],
    ["Selected <b>IN</b>, fault", "dark", "<b>amber ON</b>"],
    ["Selected <b>OUT</b>", "<b>white ON</b>", "dark (fault inhibited)"],
]
story.append(make_table(ann, [1.8*inch, 2.45*inch, 2.45*inch]))
story.append(Spacer(1,6))
story.append(ListFlowable([
    ListItem(Paragraph("<b>Power-up lamp test:</b> both halves on for <font name='Mono' size='8'>LAMP_TEST_MS</font> (~2 s) so a dead LED cannot be mistaken for a healthy dark state, then dark.", body), leftIndent=6),
    ListItem(Paragraph("<b>OUT inhibits fault:</b> a deliberately deselected system needs no crew action, so AC 25-11 keeps the amber caution off; only the white OFF status shows. Recognition and fault monitoring are suspended while OUT.", body), leftIndent=6),
], bulletType="bullet", leftIndent=14))

story.append(Paragraph("4.1 &nbsp; VIVISUN Voltage Options", h3))
story.append(Paragraph("Applied Avionics VIVISUN / Korry lighted pushbuttons are offered in <b>28 VDC, 5 VDC, 28 VAC, 5 VAC, 115 V</b> lamp variants. " + A("Applied Avionics", "https://www.appliedavionics.com/led-lighted-pushbutton-switches.html") + ". An ESP32 GPIO <b>cannot</b> drive a 28 V (or even 5 V at lamp current) legend directly \u2014 use a low-side driver per half (below). For a quick bench mock-up, substitute two ordinary 3.3 V LEDs (white + amber) with series resistors driven straight from GPIO21/GPIO14, observing the ~20 mA GPIO limit.", bodyj))

story.append(Paragraph("4.2 &nbsp; Lamp-Driver Circuit (one per legend half)", h3))
story.append(Paragraph("ESP32-S3 GPIO sources ~20 mA default (40 mA max, configurable), with a <b>1.5 A total</b> chip limit. " + A("ESP32 GPIO current", "https://esp32.com/viewtopic.php?t=20097") + ". Legend lamps need their own supply and a switch device:", body))
ckt = """            +V_lamp (5 V or 28 V, separate rail)
                  |
              [ legend lamp ]        <- VIVISUN legend (white or amber)
                  |
                  +------------------ Drain
   GPIO21 --[1k]--|G   N-ch MOSFET (logic-level, e.g. 2N7002 / AO3400)
   (or G14)       |    or NPN (e.g. 2N2222 with base resistor)
              [10k]                  <- gate/base pulldown -> GND (defined OFF)
                  |
                 GND  (Source) ------ common ground with ESP32"""
story.append(mono_light(ckt))
story.append(Spacer(1,4))
story.append(ListFlowable([
    ListItem(Paragraph("One driver for <b>GPIO21</b> (OFF/white half), one for <b>GPIO14</b> (FAULT/amber half).", small), leftIndent=6),
    ListItem(Paragraph("<b>10 k\u2126 gate/base pulldown</b> guarantees the lamp is OFF during boot/reset before the GPIO is configured (dark-cockpit integrity).", small), leftIndent=6),
    ListItem(Paragraph("Choose a MOSFET/transistor and supply rated for the lamp. For a 28 V incandescent legend, ensure FET Vds \u2265 40 V and current \u2265 lamp inrush.", small), leftIndent=6),
    ListItem(Paragraph("Tie the lamp supply ground to the ESP32 ground (single common ground).", small), leftIndent=6),
], bulletType="bullet", leftIndent=14))

# ============ 5. POWER ============
story.append(PageBreak())
story.append(Paragraph("5 &nbsp; Power Budget & Supply", h1))
pw = [
    ["Rail", "Loads", "Typical", "Peak"],
    ["<b>3.3 V</b>", "ESP32-S3 + Wi-Fi off + mic + microSD", "~80\u2013150 mA", "~250 mA (SD init / SR burst)"],
    ["<b>5 V</b>", "MAX98357A speaker output", "a few mA idle", "<b>~650 mA</b> (5 V/4 \u2126, loud)"],
    ["<b>Lamp rail</b>", "up to 2 legend halves", "0 (dark)", "per lamp spec (e.g. 28 V incand.)"],
]
story.append(make_table(pw, [1.0*inch, 2.7*inch, 1.4*inch, 1.6*inch]))
story.append(Spacer(1,6))
story.append(ListFlowable([
    ListItem(Paragraph("Power the board from <b>USB 5 V capable of \u2265 1 A</b> (the on-board 3.3 V LDO feeds the S3, mic, and SD). Reserve headroom for the amp's peak.", body), leftIndent=6),
    ListItem(Paragraph("Keep the <b>legend-lamp supply separate</b> from the logic 5 V if using 28 V lamps; only the grounds are common.", body), leftIndent=6),
    ListItem(Paragraph("Add bulk decoupling: <b>\u2265 100 \u00b5F</b> near the amp VIN plus 0.1 \u00b5F per device.", body), leftIndent=6),
], bulletType="bullet", leftIndent=14))

# ============ 6. BOM ============
story.append(Paragraph("6 &nbsp; Bill of Materials (DIY build)", h1))
bom = [
    ["Qty", "Part", "Spec / example", "Approx."],
    ["1", "ESP32-S3 DevKit", "DevKitC-1 <b>N16R8</b> (PSRAM!)", "$12\u201318"],
    ["1", "I2S MEMS mic", "<b>INMP441</b> or ICS-43434 breakout", "$4\u20136"],
    ["1", "I2S amp", "<b>MAX98357A</b> breakout", "$4\u20137"],
    ["1", "Speaker", "4\u20138 \u2126, \u2265 2 W", "$2\u20135"],
    ["1", "microSD card + breakout", "FAT32; Korvo-2 has on-board slot", "$5\u20138"],
    ["1", "Annunciator switch", "Applied Avionics VIVISUN/Korry split-legend (or 2 LEDs for bench)", "varies"],
    ["2", "Lamp driver", "logic-level N-MOSFET (2N7002/AO3400) or NPN (2N2222)", "&lt;$1"],
    ["4", "Resistors", "1 k\u2126 \u00d72 (gate), 10 k\u2126 \u00d72 (pulldown)", "&lt;$1"],
    ["2\u20133", "Pull-ups", "10 k\u2126 on SD CMD/DAT0 (if breakout lacks them)", "&lt;$1"],
    ["\u2014", "Caps", "0.1 \u00b5F per device, 100 \u00b5F bulk near amp", "&lt;$1"],
    ["1", "PTT button", "momentary SPST (or use BOOT)", "&lt;$1"],
]
story.append(make_table(bom, [0.5*inch, 1.7*inch, 3.5*inch, 1.0*inch]))
story.append(Spacer(1,5))
story.append(Paragraph("<b>Integrated alternative:</b> ESP32-S3-Korvo-2 (~$45\u201355) replaces the mic/codec/amp/SD items above; use its BSP pin map and the ES8311 codec init.", body))

# ============ 7. KORVO-2 ============
story.append(Paragraph("7 &nbsp; ESP32-S3-Korvo-2 Differences (integrated build)", h1))
story.append(ListFlowable([
    ListItem(Paragraph("Audio codec is <b>ES8311</b> (I2C control + I2S data) with an <b>NS4150</b> speaker amp \u2014 not the MAX98357A path. Initialize the codec over I2C (see <font name='Mono' size='8'>esp_codec_dev</font>/BSP).", body), leftIndent=6),
    ListItem(Paragraph("<b>Dual mics</b> feed the AFE \u2014 markedly better recognition in noise than one INMP441.", body), leftIndent=6),
    ListItem(Paragraph("microSD slot is wired on the board; map <font name='Mono' size='8'>SD_*</font> pins to the Korvo-2 schematic.", body), leftIndent=6),
    ListItem(Paragraph("Expose the annunciator on free header GPIOs; keep the same firmware logic.", body), leftIndent=6),
], bulletType="bullet", leftIndent=14))

# ============ 8. FIRMWARE BUILD & BEHAVIOR ============
story.append(PageBreak())
story.append(Paragraph("8 &nbsp; Firmware Build & Behavior", h1))
fb = [
    ["Topic", "Value"],
    ["Framework", "<b>ESP-IDF \u2265 5.2</b>"],
    ["Components", "<font name='Mono' size='7.6'>esp-sr, esp_spiffs, driver, json (cJSON), fatfs, sdmmc, esp_driver_sdmmc</font>"],
    ["Speech models", "WakeNet <font name='Mono' size='7.6'>WN9_HIESP</font>; MultiNet English <font name='Mono' size='7.6'>mn6_en/mn7_en</font> (S3)"],
    ["Partitions", "factory app 3 MB + model 5 MB + storage (UI clips) 2 MB \u2192 needs <b>16 MB</b> flash"],
    ["MultiNet phrases", "lowercase letters + single spaces only; spell numbers (\u201cv one\u201d); ~200 cmd cap"],
    ["Fault behavior", "any SD/parse/validation/audio fault \u2192 <font name='Mono' size='7.6'>ST_FAULT</font>, amber legend, no checklist shown"],
]
story.append(make_table(fb, [1.5*inch, 5.2*inch]))
story.append(Spacer(1,6))
story.append(callout("The partition table assumes a 16 MB flash part (N16R8). An 8 MB module will not fit the 3 MB app + 5 MB model + 2 MB storage layout.", "warn"))

story.append(Paragraph("8.1 &nbsp; Build & Flash", h3))
build = """cd firmware
# 1) Render the spoken checklist clips into ./audio (pick your TTS engine):
python3 scripts/make_audio.py --engine say        # macOS
#   or  --engine espeak    or  --engine piper --voice <model.onnx>
# 2) Target the S3 and build/flash (models + audio embedded automatically):
idf.py set-target esp32s3
idf.py menuconfig          # optional - defaults select Hi ESP + mn6_en
idf.py build flash monitor"""
story.append(mono_light(build))

story.append(Paragraph("8.2 &nbsp; State Machine & Fault Codes", h3))
story.append(Paragraph("The firmware mirrors the web demo with four states. <font name='Mono' size='8'>HOME</font> recognises a checklist trigger and loads it; <font name='Mono' size='8'>RUN</font> recognises each item's advance word and steps forward. To keep recognition fast, only the phrases relevant to the current step are registered (<font name='Mono' size='8'>esp_mn_commands_add</font> + <font name='Mono' size='8'>esp_mn_commands_update</font>).", bodyj))
sm = [
    ["State", "Meaning"],
    ["ST_OFF", "SELECT switched OUT \u2014 white OFF legend lit, voice ignored, fault monitoring suspended"],
    ["ST_FAULT", "SD/data/audio problem \u2014 amber FAULT legend lit, cause annunciated, retries loading"],
    ["ST_HOME", "Healthy & idle \u2014 listening for a checklist trigger word"],
    ["ST_RUN", "Reading a checklist \u2014 listening for the active item's advance word"],
]
story.append(make_table(sm, [1.3*inch, 5.4*inch], font_styles={(i,0): cellmono for i in range(1,len(sm))}))
story.append(Spacer(1,6))
story.append(Paragraph("Per the FAA-aligned safety rule, <font name='Mono' size='8'>checklist_store_load()</font> returns a specific fault code on any problem and leaves the table empty; the device never presents a partial or stale list. The UI/fault clips live in internal SPIFFS (not the card) so it can still speak a fault with no card inserted.", bodyj))
fc = [
    ["Fault code", "Trigger"],
    ["STORE_OK", "SD mounted, JSON parsed + validated, audio present (healthy)"],
    ["FAULT_NO_CARD", "SD not detected / mount failed"],
    ["FAULT_NO_AIRCRAFT", "no aircraft folder (or config.txt target missing)"],
    ["FAULT_NO_JSON", "checklists.json missing or unreadable"],
    ["FAULT_PARSE", "JSON malformed"],
    ["FAULT_VALIDATION", "schema / voice-rule violation, empty data, etc."],
    ["FAULT_AUDIO_MISSING", "a referenced read-aloud clip is absent"],
    ["FAULT_NO_MEMORY", "allocation failed while loading"],
]
story.append(make_table(fc, [1.9*inch, 4.8*inch], font_styles={(i,0): cellmono for i in range(1,len(fc))}))

# ============ 9. PROCESSOR SELECTION ============
story.append(PageBreak())
story.append(Paragraph("9 &nbsp; Processor Selection", h1))
story.append(Paragraph("9.1 &nbsp; What this application actually needs", h3))
story.append(Paragraph("This is <b>not</b> a general dictation device. The workload is narrow and well bounded:", body))
need = [
    ["Requirement", "Implication"],
    ["<b>Small, fixed vocabulary</b>", "~13 checklist triggers + a handful of universal advance words = well under the ~200-command MultiNet cap. No large-vocabulary STT needed."],
    ["<b>Offline, no connectivity</b>", "A safety/training device should not depend on WiFi, BT, or cloud. Connectivity is a liability, not a feature."],
    ["<b>Deterministic + safe</b>", "Must revert to a safe (unopened) state on any fault; single-chip, well-understood toolchain reduces failure surface."],
    ["<b>Dark-cockpit annunciation</b>", "A few GPIO + I2S in/out + SD. No high-end peripherals required."],
    ["<b>Low cost, mature tooling</b>", "Demo/training hardware; reproducible with off-the-shelf parts."],
]
story.append(make_table(need, [1.9*inch, 4.8*inch]))
story.append(Spacer(1,5))
story.append(Paragraph("The net: command-recognition on a fixed grammar, not open-ended transcription. That keeps an MCU-class part firmly in scope and makes a Linux SBC overkill.", bodyj))

story.append(Paragraph("9.2 &nbsp; Recommendation", h3))
story.append(callout("Keep the ESP32-S3 as the baseline; consider the ESP32-P4 only if you want more headroom. ESP-SR (v2.1+) explicitly supports S3 and P4 for English MultiNet, running wake word + AEC/NS + intent on a single chip. The classic ESP32 is no longer supported by current speech algorithms and should be avoided.", "info"))
story.append(Spacer(1,4))
story.append(ListFlowable([
    ListItem(Paragraph("<b>ESP32-S3 (recommended baseline):</b> Xtensa LX7 dual-core @240 MHz with AI vector instructions, 512 KB SRAM, WiFi+BLE, ~$8\u201315. Rated the best AI/voice part in the ESP line, most mature tooling, runs <font name='Mono' size='8'>mn6_en/mn7_en</font>. The firmware, wiring diagram, and BOM are already built around it. " + A("Espressif ESP-SR", "https://docs.espressif.com/projects/esp-sr/en/latest/esp32s3/index.html") + ", " + A("espboards.dev", "https://www.espboards.dev/blog/esp32-soc-options/") + ".", body), leftIndent=6),
    ListItem(Paragraph("<b>ESP32-P4 (upgrade path):</b> dual-core RISC-V up to <b>400 MHz</b> + AI instructions + a 40 MHz low-power core, 768 KB SRAM, ~2.5\u00d7 the compute of the S3, runs <font name='Mono' size='8'>mn7_en</font>. <b>No WiFi/BT</b> \u2014 for a safety device, arguably a plus (removes an attack/distraction surface). Trade-off: needs a companion radio for any connectivity, and slightly less mature tooling. Good if you later add a display or more audio processing. " + A("Espressif ESP32-P4", "https://www.espressif.com/en/products/socs/esp32-p4") + ", " + A("Elecrow P4 vs S3", "https://www.elecrow.com/blog/who-is-the-true-performance-king-esp32-p4-vs-esp32-s3.html") + ".", body), leftIndent=6),
], bulletType="bullet", leftIndent=14))
story.append(Paragraph("For this fixed-vocabulary workload the S3 has ample margin, so the P4 is a \u201cwant more headroom / future display\u201d upgrade rather than a necessity.", bodyj))

story.append(Paragraph("9.3 &nbsp; Alternatives Considered", h3))
alt = [
    ["Option", "What it is", "Verdict for this app"],
    ["<b>Syntiant NDP120</b> (Arduino Nicla Voice)", "Always-on Neural Decision Processor, ultra-low-power, embedded Cortex-M0", "Excellent for battery always-on wake-word; overkill here since we have panel power and need full command grammar + audio playback + SD."],
    ["<b>Picovoice Porcupine + Rhino</b>", "Wake-word + speech-to-intent, offline on Arm Cortex-M4", "Clean fit for fixed grammar, but requires a per-deployment AccessKey (license dependency) \u2014 undesirable for a self-contained demo."],
    ["<b>Fluent.ai</b>", "End-to-end speech-to-intent on Cortex-M4 @100 MHz, multilingual", "Good for productized multilingual intent; commercial licensing, less open tooling than ESP-SR."],
    ["<b>NXP i.MX RT600</b>", "Cortex-M33 @300 MHz + Cadence HiFi4 DSP @600 MHz, 4.5 MB SRAM", "Strong audio DSP, but more complex board + toolchain than needed for a fixed 13-checklist grammar."],
    ["<b>Raspberry Pi</b> (whisper.cpp / Vosk)", "Full offline STT on Linux", "Real large-vocabulary transcription, but Linux boot, higher power/cost, non-deterministic boot \u2014 overkill and less robust for a fixed-grammar safety device."],
]
story.append(make_table(alt, [1.8*inch, 2.3*inch, 2.6*inch]))
story.append(Spacer(1,6))
story.append(Paragraph("<b>Bottom line:</b> the ESP32-S3 remains the right baseline; the ESP32-P4 is the only \u201cstrictly better\u201d silicon in the same family and is worth it only if you want extra compute or a display. The dedicated voice chips (Syntiant, Picovoice, Fluent.ai) and the Pi solve problems this app doesn't have.", bodyj))

# ============ 10. microSD config ============
story.append(PageBreak())
story.append(Paragraph("10 &nbsp; microSD Configuration & JSON Schema", h1))
story.append(Paragraph("Checklist data is loaded from the card at boot. There is <b>no compiled-in fallback</b> \u2014 data comes only from the card. If the card has exactly one aircraft folder it loads automatically; <font name='Mono' size='8'>config.txt</font> is only needed when multiple folders exist.", bodyj))
layout = """/sdcard/
  config.txt                 (optional) one line:  AIRCRAFT=CJ2
  CJ2/
    checklists.json          the checklist data (schema below)
    audio/
      engine_fire_1.wav      one 16-bit/16 kHz/mono WAV per item "clip"
      engine_fire_2.wav
      ready.wav  complete.wav ..."""
story.append(mono_light(layout))
story.append(Spacer(1,6))
story.append(Paragraph("checklists.json schema", h3))
schema = """{
  "aircraft": "CJ2",
  "universal_advance": ["check", "checked", "complete", "next"],
  "checklists": [
    {
      "id": "engine_fire",
      "title": "Engine Fire",
      "triggers": ["engine fire"],
      "items": [
        { "clip": "engine_fire_1",
          "text": "Throttle ... idle",
          "advance": ["idle"] }
      ]
    }
  ]
}"""
story.append(mono_light(schema))
story.append(Spacer(1,6))
story.append(callout("Voice-phrase rule (all triggers, advance, universal_advance): lowercase letters and single spaces only \u2014 no digits or punctuation (MultiNet limitation). Spell numbers as words (\u201cv one\u201d). Limits: \u2264 MAX_ITEMS (12) items, \u2264 MAX_TRIGGERS (4) triggers, \u2264 MAX_ADVANCE (4) advance words per item. The loader validates the whole file and verifies every audio clip exists before going live; any violation = FAULT.", "warn"))

# ============ 11. CHECKLIST LIBRARY ============
import json as _json
data = _json.load(open("/home/user/workspace/cj2-checklist/firmware/sdcard_template/CJ2/checklists.json"))
story.append(PageBreak())
story.append(Paragraph("11 &nbsp; CJ2 Checklist Library", h1))
ua = ", ".join(data.get("universal_advance", []))
story.append(Paragraph(f"Aircraft <b>{data.get('aircraft')}</b> &nbsp;\u00b7&nbsp; {len(data['checklists'])} checklists. "
    f"Universal advance words (accepted on any item): <font name='Mono' size='8'>{ua}</font>.", body))
story.append(Paragraph("Numbers spelled as words for MultiNet (e.g. \u201cv one\u201d = V-one). Each item lists its read-aloud text and the spoken word(s) that advance it.", small))
story.append(Spacer(1,6))
for c in data["checklists"]:
    trg = "  \u00b7  ".join(c.get("triggers", []))
    block = [Paragraph(f"{c.get('title')}", S("clt", fontName="DM-B", fontSize=10, leading=13, textColor=TEALD, spaceBefore=2))]
    block.append(Paragraph(f"Triggers: <font name='Mono' size='7.6'>{trg}</font>", small))
    rows = [["#", "Read-aloud item", "Advance word(s)"]]
    for i, it in enumerate(c.get("items", []), 1):
        adv = " / ".join(it.get("advance", []))
        rows.append([str(i), it.get("text",""), adv])
    fsx = {(i,2): cellmono for i in range(1, len(rows))}
    fsx.update({(i,0): cellb for i in range(1, len(rows))})
    block.append(Spacer(1,3))
    block.append(make_table(rows, [0.35*inch, 4.35*inch, 2.0*inch], font_styles=fsx))
    block.append(Spacer(1,10))
    story.append(KeepTogether(block))

# ============ 12. WIRING DIAGRAM ============
story.append(PageBreak())
story.append(Paragraph("12 &nbsp; Wiring Diagram", h1))
img_path = "/home/user/workspace/cj2-checklist/firmware/docs/wiring_diagram.png"
from PIL import Image as PILImage
iw, ih = PILImage.open(img_path).size
maxw = PAGE_W - ML - MR
disp_w = maxw
disp_h = ih * (disp_w / iw)
# keep within page height
maxh = PAGE_H - MT - MB - 0.6*inch
if disp_h > maxh:
    disp_h = maxh
    disp_w = iw * (disp_h / ih)
story.append(Image(img_path, width=disp_w, height=disp_h))
story.append(Paragraph("Color-coded schematic: ESP32-S3 + INMP441 mic + MAX98357A amp + microSD + Applied Avionics split-legend annunciator with the lamp-driver sub-circuit and dark-cockpit state table.", cap))

# ============ 13. SOURCES ============
story.append(PageBreak())
story.append(Paragraph("13 &nbsp; Source References", h1))
sources = [
    ("INMP441 microphone datasheet", "Farnell / InvenSense", "https://www.farnell.com/datasheets/1824785.pdf"),
    ("MAX98357A amplifier datasheet", "Analog Devices", "https://www.analog.com/media/en/technical-documentation/data-sheets/max98357a-max98357b.pdf"),
    ("MAX98357A breakout guide", "Adafruit", "https://cdn-learn.adafruit.com/downloads/pdf/adafruit-max98357-i2s-class-d-mono-amp.pdf"),
    ("ESP32-S3 GPIO drive current", "Espressif forum", "https://esp32.com/viewtopic.php?t=20097"),
    ("ESP32-S3 GPIO reference", "Espressif docs", "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/gpio.html"),
    ("ESP32-S3 reserved/strapping pins (R8 octal)", "Arduino forum summary", "https://forum.arduino.cc/t/advice-on-using-all-pins-of-an-esp32-s3-devkit/1294310"),
    ("microSD operating current", "Arduino forum", "https://forum.arduino.cc/t/sd-card-how-to-reduce-the-power-consumption/145975"),
    ("VIVISUN lamp voltage options", "Applied Avionics", "https://www.appliedavionics.com/led-lighted-pushbutton-switches.html"),
    ("Annunciation color / dark-cockpit guidance", "FAA AC 25-11B", "https://www.faa.gov/documentlibrary/media/advisory_circular/ac_25-11b.pdf"),
    ("Avionics display design article", "AEA Avionics News", "https://aea.net/AvionicsNews/ANArchives/DesignDisplayOct03.pdf"),
    ("ESP-SR speech recognition framework", "Espressif docs", "https://docs.espressif.com/projects/esp-sr/en/latest/esp32s3/index.html"),
    ("ESP32 SoC options for AI/voice", "espboards.dev", "https://www.espboards.dev/blog/esp32-soc-options/"),
    ("ESP32-P4 product page", "Espressif", "https://www.espressif.com/en/products/socs/esp32-p4"),
    ("ESP32-P4 vs ESP32-S3 performance", "Elecrow", "https://www.elecrow.com/blog/who-is-the-true-performance-king-esp32-p4-vs-esp32-s3.html"),
    ("Syntiant NDP120 Neural Decision Processor", "Syntiant", "https://www.syntiant.com/ndp120"),
    ("Keyword spotting on microcontrollers", "Picovoice", "https://picovoice.ai/blog/keyword-spotting-on-microcontrollers/"),
]
src_rows = [["#", "Reference", "Source"]]
for i, (title, pub, url) in enumerate(sources, 1):
    src_rows.append([str(i), title, Paragraph(A(pub, url), cell)])
fss = {(i,0): cellb for i in range(1, len(src_rows))}
story.append(make_table(src_rows, [0.4*inch, 3.9*inch, 2.4*inch], font_styles=fss))
story.append(Spacer(1, 16))
story.append(callout("DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS. Checklist text reproduced for demonstration/training only. Repository: github.com/flas-tech/cj2-voice-emergency-checklist (MIT License).", "warn"))

# ================= PAGE TEMPLATES =================
TITLE = "CJ2 Voice Emergency Checklist"
SUBTITLE = "Technical Data Packet"

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # top teal band
    canvas.setFillColor(HEADER_BG)
    canvas.rect(0, PAGE_H - 3.1*inch, PAGE_W, 3.1*inch, fill=1, stroke=0)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 3.18*inch, PAGE_W, 0.08*inch, fill=1, stroke=0)
    # kicker
    canvas.setFillColor(colors.HexColor("#BCE2E7"))
    canvas.setFont("DM-M", 11)
    canvas.drawString(ML, PAGE_H - 1.15*inch, "ESP32-S3  \u00b7  ESP-SR OFFLINE SPEECH  \u00b7  AVIONICS PROTOTYPE")
    # title
    canvas.setFillColor(colors.white)
    canvas.setFont("DM-B", 33)
    canvas.drawString(ML, PAGE_H - 1.95*inch, "CJ2 Voice Emergency")
    canvas.drawString(ML, PAGE_H - 2.45*inch, "Checklist")
    canvas.setFont("DM-M", 15)
    canvas.setFillColor(colors.HexColor("#BCE2E7"))
    canvas.drawString(ML, PAGE_H - 2.85*inch, "Technical Data Packet")
    # body meta
    canvas.setFillColor(INK)
    canvas.setFont("DM", 11)
    y = PAGE_H - 3.9*inch
    lines = [
        "Cessna Citation CJ2 (CE 525A)  \u2014  bench / training prototype",
        "Voice-driven, fully offline emergency-checklist reader",
        "Hardware reference, firmware behavior, processor selection,",
        "checklist library, and wiring diagram.",
    ]
    for ln in lines:
        canvas.drawString(ML, y, ln); y -= 0.28*inch
    # warning box
    canvas.setFillColor(colors.HexColor("#FBF1E9"))
    canvas.roundRect(ML, 2.05*inch, PAGE_W - ML - MR, 0.95*inch, 6, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.rect(ML, 2.05*inch, 0.05*inch, 0.95*inch, fill=1, stroke=0)
    canvas.setFillColor(AMBER)
    canvas.setFont("DM-B", 11.5)
    canvas.drawString(ML + 0.25*inch, 2.68*inch, "DEMO / TRAINING USE ONLY \u2014 NOT FOR ACTUAL FLIGHT OPERATIONS")
    canvas.setFillColor(INK)
    canvas.setFont("DM", 8.8)
    canvas.drawString(ML + 0.25*inch, 2.42*inch, "Not airworthy, not certified. Must never be installed in or relied upon aboard an aircraft.")
    canvas.drawString(ML + 0.25*inch, 2.24*inch, "Checklist text reproduced for demonstration/training only.")
    # footer
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(0.6)
    canvas.line(ML, 1.5*inch, PAGE_W - MR, 1.5*inch)
    canvas.setFillColor(MUTED); canvas.setFont("DM", 9)
    canvas.drawString(ML, 1.25*inch, "Repository:  github.com/flas-tech/cj2-voice-emergency-checklist")
    canvas.drawString(ML, 1.05*inch, "Generated June 10, 2026  \u00b7  Perplexity Computer")
    canvas.restoreState()

def header_footer(canvas, doc):
    canvas.saveState()
    # header
    canvas.setFont("DM", 7.5); canvas.setFillColor(FAINT)
    canvas.drawString(ML, PAGE_H - 0.55*inch, TITLE + "  \u00b7  Technical Data Packet")
    canvas.setStrokeColor(BORDER); canvas.setLineWidth(0.5)
    canvas.line(ML, PAGE_H - 0.65*inch, PAGE_W - MR, PAGE_H - 0.65*inch)
    # footer
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
    title="CJ2 Voice Emergency Checklist \u2014 Technical Data Packet",
    author="Perplexity Computer",
)
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[frame_full], onPage=draw_cover),
    PageTemplate(id="toc", frames=[frame_main], onPage=header_footer),
    PageTemplate(id="main", frames=[frame_main], onPage=header_footer),
])
doc.build(story)
print("BUILT", OUT, os.path.getsize(OUT), "bytes")
