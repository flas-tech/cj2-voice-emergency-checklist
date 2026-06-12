#!/usr/bin/env python3
"""
CJ2 Voice Emergency Checklist — Prototype Baseboard Gerber Generator
====================================================================
DEMO/TRAINING ONLY — NOT FOR ACTUAL FLIGHT OPERATIONS.

Generates a fab-ready RS-274X Gerber layer set + Excellon drill file for a
2-layer, ~100 x 80 mm custom prototype baseboard. The ESP32-S3-DevKitC-1 and
the codec/DAC breakouts plug into 2.54mm header SOCKETS on this board; the
custom analog circuitry (isolation transformers, line driver, lamp-driver
MOSFETs, connectors, power) is placed on the PCB itself.

Layers emitted (KiCad/JLCPCB naming):
  - <name>-Edge_Cuts.gbr   board outline
  - <name>-F_Cu.gbr        top copper
  - <name>-B_Cu.gbr        bottom copper
  - <name>-F_Mask.gbr      top soldermask
  - <name>-B_Mask.gbr      bottom soldermask
  - <name>-F_Silkscreen.gbr top silk
  - <name>-B_Silkscreen.gbr bottom silk
  - <name>.drl            Excellon drill (PTH)

All coordinates in millimeters. Origin bottom-left. RS-274X, metric, leading
zero omission, absolute, 4.6 format (used as 3.3 effective resolution).
"""

import os, math, datetime

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gerbers")
NAME = "cj2_voice_checklist_proto"
os.makedirs(OUT, exist_ok=True)

# ----- board geometry -----
BW, BH = 100.0, 80.0          # board width / height mm
M = 4.0                        # courtyard margin from edge for parts

# ============================================================
# Gerber writer helpers (RS-274X)
# ============================================================
def fmt(v):
    """4.6 format integer string for a mm value."""
    return f"{int(round(v * 1e6)):d}"

def coord(x, y):
    return f"X{fmt(x)}Y{fmt(y)}"

class Gerber:
    def __init__(self, layer_desc):
        self.lines = []
        self.aperture_defs = []
        self.aps = {}          # key -> Dnn
        self.next_d = 10
        self.layer_desc = layer_desc

    def aperture(self, key, body):
        if key not in self.aps:
            d = self.next_d
            self.next_d += 1
            self.aps[key] = f"D{d}"
            self.aperture_defs.append(f"%AD{self.aps[key]}{body}*%")
        return self.aps[key]

    def circle(self, dia):
        return self.aperture(f"C{dia}", f"C,{dia:.4f}")

    def rect(self, w, h):
        return self.aperture(f"R{w}x{h}", f"R,{w:.4f}X{h:.4f}")

    def select(self, d):
        self.lines.append(f"{d}*")

    def flash(self, x, y):
        self.lines.append(f"{coord(x,y)}D03*")

    def move(self, x, y):
        self.lines.append(f"{coord(x,y)}D02*")

    def draw(self, x, y):
        self.lines.append(f"{coord(x,y)}D01*")

    def line(self, x1, y1, x2, y2, width):
        d = self.circle(width)
        self.select(d)
        self.move(x1, y1)
        self.draw(x2, y2)

    def polyline(self, pts, width):
        d = self.circle(width)
        self.select(d)
        self.move(*pts[0])
        for p in pts[1:]:
            self.draw(*p)

    def rect_outline(self, x, y, w, h, width):
        self.polyline([(x,y),(x+w,y),(x+w,y+h),(x,y+h),(x,y)], width)

    def pad_rect(self, x, y, w, h):
        d = self.rect(w, h)
        self.select(d)
        self.flash(x, y)

    def pad_circle(self, x, y, dia):
        d = self.circle(dia)
        self.select(d)
        self.flash(x, y)

    def render(self):
        hdr = []
        hdr.append("%FSLAX46Y46*%")
        hdr.append("%MOMM*%")
        hdr.append(f"G04 {self.layer_desc} - CJ2 Voice Emergency Checklist proto - DEMO ONLY*")
        hdr.append("%LPD*%")
        body = hdr + self.aperture_defs + self.lines + ["M02*"]
        return "\n".join(body) + "\n"

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.render())

# ============================================================
# Excellon drill writer
# ============================================================
class Excellon:
    def __init__(self):
        self.tools = {}   # dia -> Tnn
        self.holes = {}   # Tnn -> [(x,y)]
        self.next_t = 1

    def tool(self, dia):
        key = round(dia, 4)
        if key not in self.tools:
            t = f"T{self.next_t:02d}"
            self.next_t += 1
            self.tools[key] = t
            self.holes[t] = []
        return self.tools[key]

    def hole(self, x, y, dia):
        t = self.tool(dia)
        self.holes[t].append((x, y))

    def render(self):
        L = ["M48", "; CJ2 Voice Emergency Checklist proto drill - DEMO ONLY",
             "METRIC,TZ", "FMAT,2"]
        for dia, t in sorted(self.tools.items(), key=lambda kv: kv[1]):
            L.append(f"{t}C{dia:.3f}")
        L.append("%")
        L.append("G90")
        L.append("M71")
        for dia, t in sorted(self.tools.items(), key=lambda kv: kv[1]):
            L.append(t)
            for (x, y) in self.holes[t]:
                L.append(f"X{x:.3f}Y{y:.3f}")
        L.append("M30")
        return "\n".join(L) + "\n"

    def save(self, path):
        with open(path, "w") as f:
            f.write(self.render())

# ============================================================
# Footprint primitives
# ============================================================
# Layers
edge = Gerber("Edge.Cuts")
fcu  = Gerber("F.Cu top copper")
bcu  = Gerber("B.Cu bottom copper")
fmask= Gerber("F.Mask")
bmask= Gerber("B.Mask")
fsilk= Gerber("F.Silkscreen")
bsilk= Gerber("B.Silkscreen")
drl  = Excellon()

PADS = []   # collect (x,y,name) for routing reference / netlist export

def thru_pad(x, y, drill, pad_dia=None, square=False, name=""):
    """Through-hole pad: copper top+bottom, mask top+bottom, drill."""
    if pad_dia is None:
        pad_dia = drill + 0.6
    for g in (fcu, bcu):
        if square:
            g.pad_rect(x, y, pad_dia, pad_dia)
        else:
            g.pad_circle(x, y, pad_dia)
    for g in (fmask, bmask):
        if square:
            g.pad_rect(x, y, pad_dia + 0.1, pad_dia + 0.1)
        else:
            g.pad_circle(x, y, pad_dia + 0.1)
    drl.hole(x, y, drill)
    PADS.append((x, y, name))

def header(x, y, n, rows=1, pitch=2.54, name="", silk=True, horiz=True):
    """2.54mm header. Returns list of pad coords. Pin1 square."""
    coords = []
    for r in range(rows):
        for i in range(n):
            if horiz:
                px = x + i * pitch
                py = y + r * pitch
            else:
                px = x + r * pitch
                py = y + i * pitch
            sq = (i == 0 and r == 0)
            thru_pad(px, py, 1.0, 1.8, square=sq, name=f"{name}{i+1+r*n}")
            coords.append((px, py))
    if silk:
        x0 = x - 1.27; y0 = y - 1.27
        if horiz:
            w = n * pitch; h = rows * pitch
        else:
            w = rows * pitch; h = n * pitch
        fsilk.rect_outline(x0, y0, w, h, 0.15)
        # pin1 marker
        fsilk.line(x0-0.6, y0, x0-0.6, y0+1.0, 0.15)
    return coords

def soic_like(cx, cy, npins_side, pitch=1.27, body_w=4.0, name=""):
    """Generic dual-row SMD-ish part rendered as small thru pads for proto."""
    pads = []
    span = (npins_side - 1) * pitch
    for i in range(npins_side):
        py = cy - span/2 + i * pitch
        thru_pad(cx - body_w/2, py, 0.7, 1.3, name=f"{name}L{i+1}")
        thru_pad(cx + body_w/2, py, 0.7, 1.3, name=f"{name}R{i+1}")
        pads.append((cx - body_w/2, py)); pads.append((cx + body_w/2, py))
    fsilk.rect_outline(cx-body_w/2-1, cy-span/2-1, body_w+2, span+2, 0.15)
    return pads

def transformer(cx, cy, name=""):
    """6-pin 600:600 isolation transformer footprint (2x3, 5.08mm body)."""
    pads = []
    for r in range(2):
        for i in range(3):
            px = cx - 5.08 + i*5.08
            py = cy - 2.54 + r*5.08
            thru_pad(px, py, 0.9, 1.6, square=(i==0 and r==0), name=f"{name}{i+1+r*3}")
            pads.append((px, py))
    fsilk.rect_outline(cx-7.6, cy-5.0, 15.2, 10.0, 0.15)
    return pads

def mosfet_sot23(cx, cy, name=""):
    """SOT-23 lamp driver, proto as 3 thru pads."""
    pads = []
    for i,(dx,dy) in enumerate([(-1.0,-1.1),(1.0,-1.1),(0.0,1.1)]):
        thru_pad(cx+dx, cy+dy, 0.7, 1.2, name=f"{name}{i+1}")
        pads.append((cx+dx, cy+dy))
    fsilk.rect_outline(cx-1.6, cy-1.8, 3.2, 3.6, 0.15)
    return pads

def resistor(cx, cy, name="", horiz=True, lead=5.0):
    """Axial through-hole resistor/cap, 2 pads."""
    if horiz:
        p1=(cx-lead/2, cy); p2=(cx+lead/2, cy)
    else:
        p1=(cx, cy-lead/2); p2=(cx, cy+lead/2)
    thru_pad(*p1, 0.8, 1.5, name=f"{name}A")
    thru_pad(*p2, 0.8, 1.5, name=f"{name}B")
    fsilk.line(p1[0], p1[1], p2[0], p2[1], 0.12)
    return [p1, p2]

def sd_slot(x, y, name=""):
    """Simplified microSD: 9 pads in a row + silk box."""
    pads = []
    for i in range(9):
        px = x + i*1.1
        thru_pad(px, y, 0.7, 1.1, name=f"{name}{i+1}")
        pads.append((px, y))
    fsilk.rect_outline(x-2, y-3, 13, 14, 0.15)
    return pads

def mount_hole(x, y):
    """M2.5 mounting hole, non-plated, ring on silk."""
    drl.hole(x, y, 2.7)
    # keepout ring on top copper as annular for mechanical (no net)
    fsilk.polyline([(x+3*math.cos(a), y+3*math.sin(a)) for a in
                    [i*math.pi/12 for i in range(25)]], 0.15)

def label(g, x, y, text, h=1.4):
    """Crude vector text using line segments (uppercase) on a silk layer."""
    draw_text(g, x, y, text, h)

# ---- minimal vector font (segment-based, uppercase + few symbols) ----
FONT = {
 'A':[(0,0,0.5,2),(0.5,2,1,0),(0.2,0.9,0.8,0.9)],
 'B':[(0,0,0,2),(0,2,0.7,1.6),(0.7,1.6,0,1),(0,1,0.8,0.6),(0.8,0.6,0,0)],
 'C':[(1,1.7,0.2,2),(0.2,2,0,1.2),(0,1.2,0,0.8),(0,0.8,0.2,0),(0.2,0,1,0.3)],
 'D':[(0,0,0,2),(0,2,0.7,1.7),(0.7,1.7,0.9,1),(0.9,1,0.7,0.3),(0.7,0.3,0,0)],
 'E':[(1,0,0,0),(0,0,0,2),(0,2,1,2),(0,1,0.7,1)],
 'F':[(0,0,0,2),(0,2,1,2),(0,1,0.7,1)],
 'G':[(1,1.7,0.2,2),(0.2,2,0,1),(0,1,0.2,0),(0.2,0,1,0.2),(1,0.2,1,1),(1,1,0.5,1)],
 'H':[(0,0,0,2),(1,0,1,2),(0,1,1,1)],
 'I':[(0.5,0,0.5,2),(0,0,1,0),(0,2,1,2)],
 'J':[(1,2,1,0.4),(1,0.4,0.6,0),(0.6,0,0.1,0.3)],
 'K':[(0,0,0,2),(0,1,1,2),(0,1,1,0)],
 'L':[(0,2,0,0),(0,0,1,0)],
 'M':[(0,0,0,2),(0,2,0.5,1),(0.5,1,1,2),(1,2,1,0)],
 'N':[(0,0,0,2),(0,2,1,0),(1,0,1,2)],
 'O':[(0,0.3,0,1.7),(0,1.7,0.3,2),(0.3,2,0.7,2),(0.7,2,1,1.7),(1,1.7,1,0.3),(1,0.3,0.7,0),(0.7,0,0.3,0),(0.3,0,0,0.3)],
 'P':[(0,0,0,2),(0,2,0.8,1.7),(0.8,1.7,0.8,1.2),(0.8,1.2,0,1)],
 'Q':[(0,0.3,0,1.7),(0,1.7,0.3,2),(0.3,2,0.7,2),(0.7,2,1,1.7),(1,1.7,1,0.3),(1,0.3,0.7,0),(0.7,0,0.3,0),(0.3,0,0,0.3),(0.6,0.5,1,0)],
 'R':[(0,0,0,2),(0,2,0.8,1.7),(0.8,1.7,0.8,1.2),(0.8,1.2,0,1),(0.3,1,1,0)],
 'S':[(1,1.7,0.2,2),(0.2,2,0,1.5),(0,1.5,1,0.6),(1,0.6,0.8,0),(0.8,0,0,0.3)],
 'T':[(0,2,1,2),(0.5,2,0.5,0)],
 'U':[(0,2,0,0.3),(0,0.3,0.3,0),(0.3,0,0.7,0),(0.7,0,1,0.3),(1,0.3,1,2)],
 'V':[(0,2,0.5,0),(0.5,0,1,2)],
 'W':[(0,2,0.25,0),(0.25,0,0.5,1),(0.5,1,0.75,0),(0.75,0,1,2)],
 'X':[(0,0,1,2),(0,2,1,0)],
 'Y':[(0,2,0.5,1),(1,2,0.5,1),(0.5,1,0.5,0)],
 'Z':[(0,2,1,2),(1,2,0,0),(0,0,1,0)],
 '0':[(0,0.3,0,1.7),(0,1.7,0.3,2),(0.3,2,0.7,2),(0.7,2,1,1.7),(1,1.7,1,0.3),(1,0.3,0.7,0),(0.7,0,0.3,0),(0.3,0,0,0.3),(0,0,1,2)],
 '1':[(0.3,1.6,0.5,2),(0.5,2,0.5,0),(0.2,0,0.8,0)],
 '2':[(0,1.7,0.3,2),(0.3,2,0.8,2),(0.8,2,1,1.5),(1,1.5,0,0),(0,0,1,0)],
 '3':[(0,2,1,2),(1,2,0.4,1.1),(0.4,1.1,1,0.6),(1,0.6,0.7,0),(0.7,0,0,0.3)],
 '4':[(0.8,0,0.8,2),(0.8,2,0,0.7),(0,0.7,1,0.7)],
 '5':[(1,2,0,2),(0,2,0,1.1),(0,1.1,0.7,1.2),(0.7,1.2,1,0.7),(1,0.7,0.7,0),(0.7,0,0,0.2)],
 '6':[(0.9,1.8,0.4,2),(0.4,2,0,1),(0,1,0,0.3),(0,0.3,0.3,0),(0.3,0,0.7,0),(0.7,0,1,0.3),(1,0.3,1,0.7),(1,0.7,0.7,1),(0.7,1,0,0.9)],
 '7':[(0,2,1,2),(1,2,0.3,0)],
 '8':[(0.3,1,0,1.4),(0,1.4,0.3,2),(0.3,2,0.7,2),(0.7,2,1,1.4),(1,1.4,0.7,1),(0.7,1,0.3,1),(0.3,1,0,0.5),(0,0.5,0.3,0),(0.3,0,0.7,0),(0.7,0,1,0.5),(1,0.5,0.7,1)],
 '9':[(1,1,0.3,0.9),(0.3,0.9,0,1.3),(0,1.3,0.3,2),(0.3,2,0.7,2),(0.7,2,1,1.3),(1,1.3,1,0),(1,0,0.2,0.2)],
 '.':[(0.4,0,0.5,0.1)],
 '-':[(0.1,1,0.9,1)],
 '/':[(0,0,1,2)],
 '_':[(0,0,1,0)],
 ':':[(0.4,0.4,0.5,0.5),(0.4,1.4,0.5,1.5)],
 '+':[(0.5,0.4,0.5,1.6),(0,1,1,1)],
 '>':[(0.2,1.6,0.8,1),(0.8,1,0.2,0.4)],
 '(':[(0.6,2,0.2,1),(0.2,1,0.6,0)],
 ')':[(0.4,2,0.8,1),(0.8,1,0.4,0)],
 ' ':[],
}

def draw_text(g, x, y, text, h=1.4, width=0.15):
    sx = h/2.0
    cx = x
    for ch in text.upper():
        segs = FONT.get(ch, FONT[' '] if ch==' ' else FONT.get('-',[]))
        for (x1,y1,x2,y2) in segs:
            g.line(cx+x1*sx, y+y1*(h/2), cx+x2*sx, y+y2*(h/2), width)
        cx += sx*1.0 + sx*0.5
    return cx

# ============================================================
# PLACEMENT  (functional zones)
# ============================================================
# Board outline
edge.rect_outline(0, 0, BW, BH, 0.1)

# Mounting holes (4 corners, 4mm in)
for (mx,my) in [(4,4),(BW-4,4),(4,BH-4),(BW-4,BH-4)]:
    mount_hole(mx,my)

# ---- ESP32-S3-DevKitC-1 socket: two 1x22 header rows, ~25.4mm apart ----
# DevKitC-1 is ~25.4mm wide between pin rows, 0.1" pitch, 22 pins/side.
ESP_X = 33.0; ESP_Y = 20.0
row_pitch = 22.86   # 0.9 inch between header rows (DevKitC-1)
espL = header(ESP_X, ESP_Y, 22, rows=1, name="ESPL", horiz=False)
espR = header(ESP_X+row_pitch, ESP_Y, 22, rows=1, name="ESPR", horiz=False)
draw_text(fsilk, ESP_X-2.5, ESP_Y+22*2.54+0.5, "ESP32-S3 DEVKITC-1 (N16R8)", 1.2)
draw_text(fsilk, ESP_X-2.5, ESP_Y-3.5, "U1", 1.6)

# ---- Audio INPUT chain (left edge): J2 -> T1 -> R1/RC -> PCM1808 (U2) ----
J2 = header(6, 60, 3, name="J2", horiz=False)
draw_text(fsilk, 9, 60+3*2.54+0.5, "J2 AUDIO IN (RX ISO)", 1.2)
T1 = transformer(18, 62, name="T1")
draw_text(fsilk, 11, 68, "T1 600:600 IN ISO", 1.1)
R1 = resistor(28, 64, name="R1")
draw_text(fsilk, 27, 66, "R1", 1.0)
RC1 = resistor(28, 60, name="RC1", horiz=True)
draw_text(fsilk, 27, 58.5, "RC1", 1.0)
U2 = soic_like(72, 64, 4, name="U2")  # PCM1808 ADC breakout area
draw_text(fsilk, 66, 70, "U2 PCM1808 ADC", 1.1)

# ---- Audio OUTPUT chain (right edge): PCM5102A (U3) -> T2 -> J3 ----
U3 = soic_like(72, 30, 4, name="U3")  # PCM5102A DAC breakout area
draw_text(fsilk, 66, 36, "U3 PCM5102A DAC", 1.1)
T2 = transformer(86, 24, name="T2")
draw_text(fsilk, 79, 30, "T2 600:600 OUT ISO", 1.1)
J3 = header(94, 14, 3, name="J3", horiz=False)
draw_text(fsilk, 84, 14+3*2.54+0.5, "J3 AUDIO OUT COM3 ISO", 1.1)

# ---- microSD slots (bottom center) ----
SD1 = sd_slot(34, 6, name="SD1")
draw_text(fsilk, 34, 11.5, "SD1 CONFIG", 1.1)
SD2 = sd_slot(50, 6, name="SD2")
draw_text(fsilk, 50, 11.5, "SD2 DATA", 1.1)

# ---- Lamp drivers Q1/Q2 + gate/pulldown resistors (lower-left) ----
Q1 = mosfet_sot23(12, 30, name="Q1")
draw_text(fsilk, 9, 33, "Q1 OFF/WHT", 1.0)
Q2 = mosfet_sot23(12, 22, name="Q2")
draw_text(fsilk, 9, 25, "Q2 FAULT/AMB", 1.0)
R2 = resistor(18, 31, name="R2"); draw_text(fsilk,17.5,33,"R2",0.9)
R3 = resistor(18, 23, name="R3"); draw_text(fsilk,17.5,25,"R3",0.9)
R4 = resistor(6, 30, name="R4", horiz=False); draw_text(fsilk,3.5,30,"R4",0.9)
R5 = resistor(6, 22, name="R5", horiz=False); draw_text(fsilk,3.5,22,"R5",0.9)

# ---- SD bus pull-ups R6/R7 ----
R6 = resistor(28, 12, name="R6", horiz=False); draw_text(fsilk,29,12,"R6",0.9)
R7 = resistor(31, 12, name="R7", horiz=False); draw_text(fsilk,32,12,"R7",0.9)

# ---- Annunciator / legend (SW1) + bench LEDs D1/D2 (top-right) ----
SW1 = header(70, 72, 4, name="SW1", horiz=True)
draw_text(fsilk, 70, 76, "SW1 ANNUNCIATOR (VIVISUN)", 1.0)
D1 = resistor(90, 70, name="D1", horiz=False); draw_text(fsilk,91,70,"D1 WHT",0.9)
D2 = resistor(94, 70, name="D2", horiz=False); draw_text(fsilk,95,70,"D2 AMB",0.9)

# ---- PTT button SW2 (lower-left edge) ----
SW2 = header(6, 12, 2, name="SW2", horiz=False)
draw_text(fsilk, 8, 12, "SW2 PTT", 1.0)

# ---- Main I/O connector J1 (bottom edge) ----
J1 = header(60, 4, 9, name="J1", horiz=True)
draw_text(fsilk, 60, 1.0, "J1 MAIN I/O (SEL/LEGENDS/PTT/PWR)", 1.0)

# ---- Power section: USB-C in (PWR1) + bulk cap C9 + decoupling C1..C8 ----
PWR1 = header(90, 50, 2, name="PWR1", horiz=False)
draw_text(fsilk, 86, 50+2*2.54+0.5, "PWR1 5V IN", 1.0)
C9 = resistor(82, 50, name="C9", horiz=False); draw_text(fsilk,83.5,50,"C9 100uF",0.9)
# decoupling caps scattered near devices
deco_pos = [(40,40),(48,40),(56,40),(64,40),(56,28),(64,52),(40,52),(48,52)]
for i,(dx,dy) in enumerate(deco_pos):
    resistor(dx, dy, name=f"C{i+1}", horiz=True, lead=3.0)
    draw_text(fsilk, dx-1, dy+1.2, f"C{i+1}", 0.8)

# ============================================================
# COPPER POURS / GROUND + key traces (simplified prototype routing)
# ============================================================
# Bottom-layer ground reference frame (perimeter ring) + a few fills
bcu.rect_outline(2, 2, BW-4, BH-4, 1.2)   # ground ring on bottom
# Top power rail (3V3 distribution spine across device zone)
fcu.line(38, 44, 90, 44, 0.8)             # 3V3 spine
fcu.line(38, 44, 38, 40, 0.6)

# A representative set of signal traces (illustrative routing for proto):
def trace_top(a, b, w=0.4):
    fcu.line(a[0],a[1],b[0],b[1],w)
def trace_bot(a, b, w=0.4):
    bcu.line(a[0],a[1],b[0],b[1],w)

# Audio IN: J2 -> T1 primary
trace_top(J2[0], T1[0]); trace_top(J2[2], T1[2])
# T1 secondary -> R1 -> RC1 -> U2 (ADC)
trace_top(T1[3], R1[0]); trace_top(R1[1], RC1[0]); trace_top(RC1[1], U2[0])
trace_top(T1[5], U2[2])
# U2 -> ESP I2S in (AIN: BCLK4/LRCLK5/DIN6/MCLK3) routed to right ESP row
trace_bot(U2[5], espR[3]); trace_bot(U2[6], espR[4])
trace_bot(U2[7], espR[5]); trace_bot(U2[4], espR[2])
# ESP I2S out (AOUT: BCLK15/LRCLK16/DOUT17) -> U3 DAC
trace_bot(espR[14], U3[0]); trace_bot(espR[15], U3[1]); trace_bot(espR[16], U3[2])
# U3 -> T2 primary -> J3 secondary
trace_top(U3[5], T2[0]); trace_top(U3[7], T2[2])
trace_top(T2[3], J3[0]); trace_top(T2[5], J3[2])
# Lamp drivers: ESP G21/G14 -> R2/R3 gate -> Q1/Q2
trace_top(espL[20], R2[1]); trace_top(R2[0], Q1[0])
trace_top(espL[13], R3[1]); trace_top(R3[0], Q2[0])
# SD bus: ESP G7/G9/G8 -> SD1/SD2 (shared 1-bit)
trace_bot(espR[6], SD1[0]); trace_bot(espR[8], SD1[1]); trace_bot(espR[7], SD1[2])
trace_bot(espR[6], SD2[0]); trace_bot(espR[8], SD2[1]); trace_bot(espR[7], SD2[2])
# Power: PWR1 -> C9 -> 3V3 spine entry
trace_top(PWR1[0], C9[0]); trace_top(C9[1], (82,44))

# ============================================================
# TOP-LEVEL SILK: title block + warnings + COM3 callouts
# ============================================================
draw_text(fsilk, 6, BH-9, "CJ2 VOICE EMERGENCY CHECKLIST - PROTO BASEBOARD", 1.5, 0.18)
draw_text(fsilk, 6, BH-12.5, "REV A  2-LAYER  100X80MM", 1.2)
draw_text(fsilk, 6, BH-16, "DEMO/TRAINING ONLY - NOT FOR FLIGHT OPS", 1.2, 0.16)
draw_text(bsilk, 6, 6, "GND POUR / BOTTOM", 1.4)
draw_text(fsilk, 40, 64, "I2S IN", 1.0)
draw_text(fsilk, 40, 30, "I2S OUT (COM3)", 1.0)

# ============================================================
# SAVE
# ============================================================
edge.save(os.path.join(OUT, f"{NAME}-Edge_Cuts.gbr"))
fcu.save(os.path.join(OUT, f"{NAME}-F_Cu.gbr"))
bcu.save(os.path.join(OUT, f"{NAME}-B_Cu.gbr"))
fmask.save(os.path.join(OUT, f"{NAME}-F_Mask.gbr"))
bmask.save(os.path.join(OUT, f"{NAME}-B_Mask.gbr"))
fsilk.save(os.path.join(OUT, f"{NAME}-F_Silkscreen.gbr"))
bsilk.save(os.path.join(OUT, f"{NAME}-B_Silkscreen.gbr"))
drl.save(os.path.join(OUT, f"{NAME}.drl"))

print("Gerber + drill written to", OUT)
print("Pads placed:", len(PADS))
print("Drill tools:", {f"{d:.3f}mm": t for d,t in drl.tools.items()})
