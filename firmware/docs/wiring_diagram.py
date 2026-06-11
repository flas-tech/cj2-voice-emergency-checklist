#!/usr/bin/env python3
"""
Generate the CJ2 Voice Emergency Checklist DIY wiring diagram (SVG).
Schematic-style block diagram: ESP32-S3 in the center, peripherals around it,
color-coded nets, and the Applied Avionics split-legend annunciator switch with
its lamp-driver circuit. Pin numbers match firmware/main/board_pins.h.

Run:  python3 wiring_diagram.py   ->  wiring_diagram.svg
"""

W, H = 1600, 1180

# ---- palette ----
BG      = "#0e1320"
PANEL   = "#1a2236"
PANEL2  = "#232d47"
EDGE    = "#3a4663"
INK     = "#e8edf6"
SUB     = "#9fb0cf"
ESP     = "#2a3a5e"
ESPED   = "#4f6aa0"

# net colors
C_3V3   = "#ff5d5d"   # red
C_5V    = "#ff9f43"   # orange
C_GND   = "#5b6577"   # gray
C_I2S_M = "#37d39a"   # green (mic I2S)
C_I2S_S = "#36b3ff"   # blue  (speaker I2S)
C_SD    = "#c98bff"   # purple (SD)
C_CTRL  = "#ffd84d"   # yellow (buttons/select)
C_LED   = "#ff7ac0"   # pink  (legend lamps)

parts = []
def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def rect(x,y,w,h,fill,stroke=EDGE,rx=10,sw=1.5):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def text(x,y,s,size=15,fill=INK,anchor="start",weight="400",mono=False,ls="0"):
    fam = "ui-monospace,Menlo,Consolas,monospace" if mono else \
          "Inter,Segoe UI,Helvetica,Arial,sans-serif"
    parts.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
                 f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" '
                 f'letter-spacing="{ls}">{esc(s)}</text>')

def wire(pts,color,wd=3.0,dash=None):
    d = "M " + " L ".join(f"{x},{y}" for x,y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    parts.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{wd}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{da}/>')

def dot(x,y,color,r=4.5):
    parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')

def pin(x,y,label,color,side="left",size=13):
    dot(x,y,color)
    if side=="left":  text(x-10,y+4,label,size,SUB,"end",mono=True)
    else:             text(x+10,y+4,label,size,SUB,"start",mono=True)

# ================= background =================
parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
# title
text(40,52,"CJ2 Voice Emergency Checklist — DIY Wiring Diagram", 30, INK, weight="700")
text(40,80,"ESP32-S3 + INMP441 mic + MAX98357A amp + microSD + Applied Avionics split-legend annunciator switch",
     16, SUB)
text(40,102,"Pin numbers match firmware/main/board_pins.h   •   DEMO / TRAINING ONLY — NOT FOR FLIGHT", 13, C_5V, weight="600")

# ================= ESP32-S3 (center) =================
ex,ey,ew,eh = 640, 250, 320, 620
rect(ex,ey,ew,eh,ESP,ESPED,rx=16,sw=2.5)
text(ex+ew/2,ey+38,"ESP32-S3", 26, INK,"middle",weight="700")
text(ex+ew/2,ey+62,"DevKitC-1  N16R8", 14, SUB,"middle")
text(ex+ew/2,ey+82,"(PSRAM required for ESP-SR)", 12, C_5V,"middle")

# left-side ESP pins (x = ex)
LX = ex
esp_left = [
    (300,"3V3",  C_3V3),
    (335,"5V",   C_5V),
    (370,"GND",  C_GND),
    (430,"G4  BCLK", C_I2S_M),
    (465,"G5  WS",   C_I2S_M),
    (500,"G6  DIN",  C_I2S_M),
    (560,"G7  CLK",  C_SD),
    (595,"G9  CMD",  C_SD),
    (630,"G8  D0",   C_SD),
    (700,"G10 SEL",  C_CTRL),
    (735,"G0  PTT",  C_CTRL),
]

# right-side ESP pins (x = ex+ew)
RX = ex+ew
esp_right = [
    (430,"G15 BCLK", C_I2S_S),
    (465,"G16 LRC",  C_I2S_S),
    (500,"G17 DIN",  C_I2S_S),
    (600,"G21 OFF",  C_LED),
    (635,"G14 FLT",  C_LED),
    (700,"G48 STA",  C_CTRL),
]
for y,lab,col in esp_right:
    pin(RX,y,lab,col,"right")

# left pin labels sit just inside, to the LEFT of the pins
for y,lab,col in esp_left:
    dot(LX,y,col)
    text(LX-12,y+4,lab,13,SUB,"end",mono=True)

# ================= MICROPHONE (top-left) =================
mx,my,mw,mh = 70, 250, 300, 190
rect(mx,my,mw,mh,PANEL,rx=12)
text(mx+16,my+30,"INMP441 MIC", 18, INK,weight="700")
text(mx+16,my+50,"I2S MEMS  -  1.8 to 3.3 V  -  ~2.5 mA", 12, SUB)
mp = [(my+95,"VDD",C_3V3),(my+120,"GND",C_GND),(my+145,"SCK",C_I2S_M),
      (my+165,"WS",C_I2S_M),(my+185,"SD",C_I2S_M)]
MPX = mx+mw
for (y,lab,col) in mp:
    dot(MPX,y,col); text(MPX-12,y+4,lab,12,SUB,"end",mono=True)
text(mx+16,my+mh-8,"L/R to GND (left ch)  -  SD: 100k to GND", 11, C_5V)

# ================= microSD (left, lower) =================
sx,sy,sw_,sh = 70, 470, 300, 175
rect(sx,sy,sw_,sh,PANEL,rx=12)
text(sx+16,sy+30,"microSD CARD", 18, INK,weight="700")
text(sx+16,sy+50,"SDMMC 1-bit  -  3.3 V  -  FAT32", 12, SUB)
sdp=[(sy+82,"CLK",C_SD),(sy+105,"CMD",C_SD),(sy+128,"D0/DAT0",C_SD),
     (sy+151,"VDD",C_3V3),(sy+170,"GND",C_GND)]
SPX=sx+sw_
for (y,lab,col) in sdp:
    dot(SPX,y,col); text(SPX-12,y+4,lab,12,SUB,"end",mono=True)

# ================= SPEAKER AMP (top-right) =================
ax,ay,aw,ah = 1230, 250, 300, 210
rect(ax,ay,aw,ah,PANEL,rx=12)
text(ax+16,ay+30,"MAX98357A AMP", 18, INK,weight="700")
text(ax+16,ay+50,"Class-D  -  2.5 to 5.5 V  -  <=650 mA pk", 12, SUB)
amp=[(ay+82,"VIN",C_5V),(ay+105,"GND",C_GND),(ay+128,"BCLK",C_I2S_S),
     (ay+151,"LRC",C_I2S_S),(ay+174,"DIN",C_I2S_S)]
for (y,lab,col) in amp:
    dot(ax,y,col); text(ax+12,y+4,lab,12,SUB,"start",mono=True)
text(ax+16,ay+ah-30,"SD pin: float = mono", 11, C_5V)
text(ax+16,ay+ah-12,"GAIN: NC = 9 dB (default)", 11, C_5V)
# speaker symbol
spk_x, spk_y = ax+aw+10, ay+150
parts.append(f'<path d="M {spk_x},{spk_y-14} h14 l18,-18 v60 l-18,-18 h-14 z" '
             f'fill="{PANEL2}" stroke="{EDGE}" stroke-width="1.5"/>')
text(spk_x+6, spk_y+44, "4–8 Ω", 11, SUB, "middle")
wire([(ax+aw, ay+82),(spk_x-4, ay+82),(spk_x-4, spk_y-30),(spk_x+6,spk_y-30)], C_5V, 2)  # decorative

# ================= ANNUNCIATOR SWITCH (right, lower) =================
gx,gy,gw,gh = 1150, 540, 400, 470
rect(gx,gy,gw,gh,PANEL,rx=14)
text(gx+18,gy+30,"APPLIED AVIONICS", 16, INK,weight="700")
text(gx+18,gy+50,"VIVISUN / Korry split-legend switch", 12, SUB)
text(gx+18,gy+68,"Dark cockpit (FAA AC 25-11)", 11, C_5V)

# legend faceplate
fx,fy,fw,fh = gx+24, gy+86, 170, 120
rect(fx,fy,fw,fh,"#0b0f18","#5a6b8c",rx=8,sw=2)
parts.append(f'<line x1="{fx}" y1="{fy+fh/2}" x2="{fx+fw}" y2="{fy+fh/2}" stroke="#5a6b8c" stroke-width="2"/>')
text(fx+fw/2, fy+34, "VOICE CHKLST", 13, "#dfe6f2","middle",weight="700")
text(fx+fw/2, fy+50, "OFF", 15, "#ffffff","middle",weight="800")
text(fx+fw/2, fy+92, "VOICE CHKLST", 13, "#ffcf6b","middle",weight="700")
text(fx+fw/2, fy+108,"FAULT", 15, "#ffb02e","middle",weight="800")
text(fx-2, fy-6, "TOP = white", 10, "#cfd8ea")
text(fx-2, fy+fh+16, "BOTTOM = amber", 10, "#ffcf6b")

# state table
tx,ty = gx+210, gy+92
text(tx,ty,"STATE  to  LEGEND", 12, INK, weight="700")
rows=[("IN + OK","dark","dark"),("IN + fault","dark","AMBER"),("OUT","WHITE","dark")]
text(tx,ty+22,"Sel.",11,SUB); text(tx+78,ty+22,"OFF",11,SUB); text(tx+140,ty+22,"FAULT",11,SUB)
for i,(s,o,f) in enumerate(rows):
    yy=ty+44+i*22
    text(tx,yy,s,11,INK,mono=True)
    text(tx+78,yy,o,11,("#ffffff" if o!="dark" else SUB))
    text(tx+140,yy,f,11,("#ffb02e" if f!="dark" else SUB))

# lamp-driver sub-circuit
dvx,dvy,dvw,dvh = gx+24, gy+230, gw-48, 210
rect(dvx,dvy,dvw,dvh,PANEL2,rx=10)
text(dvx+14,dvy+24,"LAMP DRIVER (per legend half)", 13, INK,weight="700")
text(dvx+14,dvy+44,"GPIO cannot drive a 28 V lamp directly - use a", 11, SUB)
text(dvx+14,dvy+60,"low-side N-MOSFET / NPN per half.", 11, SUB)
# simple driver schematic
bx = dvx+30; by = dvy+150
# lamp supply rail
text(bx-6, by-82, "+V lamp (5 or 28 V)", 11, C_5V)
wire([(bx,by-72),(bx+220,by-72)], C_5V, 2.5)
# lamp
parts.append(f'<circle cx="{bx+110}" cy="{by-50}" r="16" fill="none" stroke="{C_LED}" stroke-width="2.5"/>')
parts.append(f'<path d="M {bx+99},{by-61} l22,22 M {bx+121},{by-61} l-22,22" stroke="{C_LED}" stroke-width="2"/>')
text(bx+132, by-46, "legend lamp", 10, C_LED)
wire([(bx+110,by-72),(bx+110,by-66)], C_5V, 2.5)        # rail to lamp
wire([(bx+110,by-34),(bx+110,by-10)], C_LED, 2.5)       # lamp to drain
# MOSFET
parts.append(f'<rect x="{bx+96}" y="{by-10}" width="30" height="40" rx="4" fill="{ESP}" stroke="{ESPED}"/>')
text(bx+111, by+14, "Q", 12, INK,"middle",weight="700")
wire([(bx+110,by+30),(bx+110,by+52)], C_GND, 2.5)       # source to GND
text(bx+118, by+50, "GND", 10, SUB)
# gate from GPIO via resistor
wire([(bx-2,by+10),(bx+96,by+10)], C_LED, 2.5)
parts.append(f'<rect x="{bx+34}" y="{by+3}" width="34" height="14" fill="{PANEL}" stroke="{EDGE}"/>')
text(bx+51, by+14, "1k", 9, SUB,"middle")
text(bx-8, by+8, "GPIO21/G14", 10, C_LED, "end")
text(bx+30, by+38, "pulldown 10k to GND (off-state)", 9, SUB)

# ================= SELECT SWITCH + PTT (bottom-left) =================
swx,swy,sww,swh = 70, 700, 300, 150
rect(swx,swy,sww,swh,PANEL,rx=12)
text(swx+16,swy+28,"DISCRETE INPUTS", 16, INK,weight="700")
text(swx+16,swy+52,"SELECT  G10 to GND when IN", 12, C_CTRL,mono=True)
text(swx+16,swy+74,"(active-low, internal pull-up)", 11, SUB)
text(swx+16,swy+100,"PTT  G0/BOOT to GND", 12, C_CTRL,mono=True)
text(swx+16,swy+120,"(hold to talk; active-low)", 11, SUB)
SWPX=swx+sww
dot(SWPX,swy+52,C_CTRL); dot(SWPX,swy+100,C_CTRL)

# ================= power rail box (bottom center) =================
px,py,pw,ph = 470, 920, 700, 200
rect(px,py,pw,ph,PANEL,rx=12)
text(px+18,py+28,"POWER & GROUND", 16, INK,weight="700")
pwr=[("3V3 (red)","ESP32-S3 3V3 -> mic VDD, microSD VDD", C_3V3),
     ("5V  (orange)","USB/VIN -> amp VIN (best output); lamp rail separate", C_5V),
     ("GND (gray)","common ground - ALL devices + lamp driver source", C_GND)]
for i,(a,b,c) in enumerate(pwr):
    yy=py+58+i*34
    dot(px+28,yy-4,c,6); text(px+44,yy,a,13,INK,weight="700")
    text(px+210,yy,b,12,SUB)
text(px+18,py+ph-14,"Budget: logic + peripherals < 250 mA; amp adds up to ~650 mA peak at 5V/4ohm - size USB >= 1 A.",
     11, C_5V)

# ===================================================================
#                           WIRES
# ===================================================================
# Mic I2S to ESP left pins (G4/G5/G6)
wire([(MPX,my+145),(560,my+145),(560,430),(LX,430)], C_I2S_M)  # SCK->BCLK G4
wire([(MPX,my+165),(575,my+165),(575,465),(LX,465)], C_I2S_M)  # WS  G5
wire([(MPX,my+185),(590,my+185),(590,500),(LX,500)], C_I2S_M)  # SD->DIN G6
# Mic power
wire([(MPX,my+95),(420,my+95),(420,300),(LX,300)], C_3V3)      # VDD->3V3
wire([(MPX,my+120),(405,my+120),(405,370),(LX,370)], C_GND)    # GND

# microSD to ESP (G7/G9/G8)
wire([(SPX,sy+82),(560,sy+82),(560,560),(LX,560)], C_SD)       # CLK G7
wire([(SPX,sy+105),(545,sy+105),(545,595),(LX,595)], C_SD)     # CMD G9
wire([(SPX,sy+128),(530,sy+128),(530,630),(LX,630)], C_SD)     # D0 G8
wire([(SPX,sy+151),(420,sy+151),(420,300)], C_3V3)             # SD VDD -> 3V3 net
wire([(SPX,sy+170),(405,sy+170),(405,370)], C_GND)             # SD GND

# Select + PTT to ESP
wire([(SWPX,swy+52),(560,swy+52),(560,700),(LX,700)], C_CTRL)  # SELECT G10
wire([(SWPX,swy+100),(545,swy+100),(545,735),(LX,735)], C_CTRL)# PTT G0

# Amp I2S to ESP right pins (G15/G16/G17)
wire([(RX,430),(1180,430),(1180,ay+128),(ax,ay+128)], C_I2S_S) # BCLK G15
wire([(RX,465),(1165,465),(1165,ay+151),(ax,ay+151)], C_I2S_S) # LRC  G16
wire([(RX,500),(1150,500),(1150,ay+174),(ax,ay+174)], C_I2S_S) # DIN  G17
# Amp power
wire([(ax,ay+82),(1190,ay+82),(1190,335),(RX+0,335)], C_5V)    # decorative to 5V (drawn to right edge)
# route 5V/GND from ESP right to amp more cleanly:
wire([(RX,335),(1200,335),(1200,ay+82),(ax,ay+82)], C_5V)      # 5V to VIN
wire([(RX,370),(1215,370),(1215,ay+105),(ax,ay+105)], C_GND)   # GND

# Legend lamps: GPIO21/G14 -> driver gates (pink), drains to lamps already drawn
# Route from ESP right pins (G21 @600, G14 @635) down to the driver block gate input.
gate_x = gx+24+30-8  # approx bx-8 of first driver instance
wire([(RX,600),(1080,600),(1080,gy+230+160),(gx+24,gy+230+160)], C_LED)  # G21 OFF -> driver
wire([(RX,635),(1095,635),(1095,gy+230+178),(gx+24+18,gy+230+178)], C_LED, 2.6, dash="6 5") # G14 FLT (2nd half)
text(1072, 592, "G21 -> OFF half", 10, C_LED, "end")
text(1108, 760, "G14 -> FAULT half (2nd driver)", 10, C_LED, "start")

# Status LED note (G48 onboard)
text(RX+12, 690, "G48 = onboard RGB (status)", 11, SUB)

# ---- legend / key ----
kx,ky = 40, H-150
keys=[("3.3 V",C_3V3),("5 V",C_5V),("GND",C_GND),("Mic I2S",C_I2S_M),
      ("Speaker I2S",C_I2S_S),("microSD",C_SD),("Control in",C_CTRL),("Legend lamp",C_LED)]
text(kx,ky-12,"NET KEY",13,INK,weight="700")
for i,(lab,col) in enumerate(keys):
    yy=ky+ (i//4)*26
    xx=kx + (i%4)*150
    parts.append(f'<line x1="{xx}" y1="{yy}" x2="{xx+26}" y2="{yy}" stroke="{col}" stroke-width="4" stroke-linecap="round"/>')
    text(xx+34,yy+4,lab,12,SUB)

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n' \
      + "\n".join(parts) + "\n</svg>\n"

import os
out = os.path.join(os.path.dirname(__file__), "wiring_diagram.svg")
with open(out,"w") as f: f.write(svg)
print("wrote", out, len(svg), "bytes")
