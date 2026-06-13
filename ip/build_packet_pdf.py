#!/usr/bin/env python3
"""Build a combined provisional filing packet PDF: cover + spec + figures."""
import re, os, urllib.request
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak,
                                Image, HRFlowable)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

IP = "/home/user/workspace/cj2-checklist/ip"
FIGDIR = os.path.join(IP, "figures")
OUT = os.path.join(IP, "Provisional_Filing_Packet.pdf")

# --- fonts ---
FONTS = {
    "DMSans": "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf",
    "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
}
body_font, head_font = "Helvetica", "Helvetica-Bold"
try:
    for name, url in FONTS.items():
        p = f"/tmp/{name}.ttf"
        if not os.path.exists(p):
            urllib.request.urlretrieve(url, p)
        pdfmetrics.registerFont(TTFont(name, p))
    body_font, head_font = "Inter", "DMSans"
except Exception as e:
    print("font fallback:", e)

styles = getSampleStyleSheet()
TEAL = colors.HexColor("#01696F")
INK = colors.HexColor("#28251D")
MUTED = colors.HexColor("#7A7974")

def S(name, **kw):
    return ParagraphStyle(name, **kw)

h1 = S("h1", fontName=head_font, fontSize=15, textColor=TEAL, spaceBefore=16, spaceAfter=6, leading=18)
h2 = S("h2", fontName=head_font, fontSize=12, textColor=INK, spaceBefore=10, spaceAfter=4, leading=15)
body = S("body", fontName=body_font, fontSize=9.5, textColor=INK, leading=14, spaceAfter=6, alignment=TA_JUSTIFY)
bullet = S("bullet", parent=body, leftIndent=14, bulletIndent=4)
cap = S("cap", fontName=body_font, fontSize=8, textColor=MUTED, leading=11, alignment=TA_CENTER, spaceBefore=4, spaceAfter=14)
title_style = S("title", fontName=head_font, fontSize=20, textColor=INK, leading=26, alignment=TA_CENTER, spaceAfter=10)
sub_style = S("sub", fontName=body_font, fontSize=11, textColor=MUTED, leading=15, alignment=TA_CENTER, spaceAfter=6)

def md_inline(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)
    return t

story = []
# ---- cover ----
story.append(Spacer(1, 1.4*inch))
story.append(Paragraph("U.S. PROVISIONAL PATENT APPLICATION", sub_style))
story.append(Paragraph("Filing Packet (Draft)", S("sb2", parent=sub_style, fontSize=9, textColor=TEAL)))
story.append(Spacer(1, 0.3*inch))
story.append(Paragraph("Offline Voice-Driven Advisory Checklist Reader Using a Galvanically-Isolated Receive-Only Audio-Panel Tap and a Dedicated Galvanically-Isolated Audio-Panel Output Channel, with a Dual-Removable-Card Fail-Safe Configuration Architecture", title_style))
story.append(Spacer(1, 0.3*inch))
story.append(HRFlowable(width="40%", color=TEAL, thickness=1.2))
story.append(Spacer(1, 0.3*inch))
for line in ["<b>Inventor:</b> Michael Gravalec",
             "<b>Applicant:</b> Flite Line Aviation Services, LLC",
             "<b>Filing type:</b> 35 U.S.C. § 111(b) — Provisional",
             "<b>Project reference:</b> CheckM8 (docket CHECKM8-PROV-001)"]:
    story.append(Paragraph(line, S("ci", parent=body, alignment=TA_CENTER, spaceAfter=4)))
story.append(Spacer(1, 0.5*inch))
story.append(Paragraph("DRAFT — not yet filed. Prepared as a working packet; not legal advice. "
                       "Verify all fields and have a registered patent practitioner review before filing.",
                       S("warn", parent=cap, fontSize=8.5)))
story.append(PageBreak())

# ---- specification ----
with open(os.path.join(IP, "provisional_patent_application.md")) as f:
    lines = f.readlines()

buf = []
def flush():
    global buf
    if buf:
        txt = " ".join(buf).strip()
        if txt:
            story.append(Paragraph(md_inline(txt), body))
        buf = []

for ln in lines:
    s = ln.rstrip("\n")
    if s.strip() == "---":
        flush(); continue
    if s.startswith("# "):
        flush(); story.append(Paragraph(md_inline(s[2:]), h1)); continue
    if s.startswith("## "):
        flush(); story.append(Paragraph(md_inline(s[3:]), h1)); continue
    if s.startswith("### "):
        flush(); story.append(Paragraph(md_inline(s[4:]), h2)); continue
    if re.match(r"^\s*[-*]\s+", s):
        flush()
        item = re.sub(r"^\s*[-*]\s+", "", s)
        story.append(Paragraph("• " + md_inline(item), bullet)); continue
    if re.match(r"^\s*\d+\.\s+", s):
        flush()
        story.append(Paragraph(md_inline(s.strip()), bullet)); continue
    if s.strip() == "":
        flush(); continue
    buf.append(s)
flush()

# ---- figures ----
story.append(PageBreak())
story.append(Paragraph("DRAWINGS", h1))
story.append(Paragraph("FIG. 1 – FIG. 14. Informal drawings (acceptable for a provisional application under 37 CFR 1.81).", cap))
figs = sorted([f for f in os.listdir(FIGDIR) if re.match(r"FIG_\d+\.png", f)])
for fn in figs:
    img = Image(os.path.join(FIGDIR, fn))
    maxw, maxh = 6.8*inch, 7.6*inch
    iw, ih = img.drawWidth, img.drawHeight
    sc = min(maxw/iw, maxh/ih)
    img.drawWidth, img.drawHeight = iw*sc, ih*sc
    story.append(img)
    story.append(PageBreak())

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(body_font, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(letter[0]/2, 0.45*inch,
        f"Provisional Patent Application — DRAFT — Page {doc.page}   |   NOT LEGAL ADVICE")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.85*inch, rightMargin=0.85*inch,
                        topMargin=0.85*inch, bottomMargin=0.75*inch,
                        title="Provisional Patent Application Filing Packet",
                        author="Perplexity Computer")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("Wrote", OUT, os.path.getsize(OUT), "bytes")
