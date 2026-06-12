#!/usr/bin/env python3
"""
Minimal RS-274X + Excellon parser/renderer to verify the generated layers.
Produces a composite PCB preview PNG. Verification only (not a DRC).
"""
import os, re, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gerbers")
NAME = "cj2_voice_checklist_proto"

def parse_gerber(path):
    """Return dict: apertures, flashes [(x,y,ap)], draws [(x1,y1,x2,y2,ap)]."""
    aps = {}
    flashes, draws = [], []
    cur_ap = None
    x = y = 0.0
    px = py = 0.0
    with open(path) as f:
        txt = f.read()
    for line in txt.splitlines():
        line = line.strip()
        m = re.match(r"%ADD(\d+)([CR]),([\d.]+)(?:X([\d.]+))?\*%", line)
        if m:
            d = "D"+m.group(1); shape=m.group(2)
            a=float(m.group(3)); b=float(m.group(4)) if m.group(4) else a
            aps[d]=(shape,a,b); continue
        m = re.match(r"^(D\d+)\*$", line)
        if m: cur_ap=m.group(1); continue
        m = re.match(r"X(-?\d+)Y(-?\d+)D0([123])\*", line)
        if m:
            xi=int(m.group(1))/1e6; yi=int(m.group(2))/1e6; op=m.group(3)
            if op=="3": flashes.append((xi,yi,cur_ap))
            elif op=="1": draws.append((px,py,xi,yi,cur_ap)); px,py=xi,yi
            elif op=="2": px,py=xi,yi
            continue
    return aps, flashes, draws

def parse_drill(path):
    holes=[]; tools={}; cur=None
    with open(path) as f:
        for line in f:
            line=line.strip()
            m=re.match(r"(T\d+)C([\d.]+)",line)
            if m: tools[m.group(1)]=float(m.group(2)); continue
            m=re.match(r"^(T\d+)$",line)
            if m: cur=m.group(1); continue
            m=re.match(r"X(-?[\d.]+)Y(-?[\d.]+)",line)
            if m and cur: holes.append((float(m.group(1)),float(m.group(2)),tools[cur]))
    return holes

def draw_layer(ax, path, color, alpha=1.0, lw_scale=1.0):
    aps, flashes, draws = parse_gerber(path)
    for (x,y,ap) in flashes:
        shape,a,b = aps.get(ap,("C",0.3,0.3))
        if shape=="C":
            ax.add_patch(Circle((x,y), a/2, color=color, alpha=alpha, lw=0))
        else:
            ax.add_patch(Rectangle((x-a/2,y-b/2), a, b, color=color, alpha=alpha, lw=0))
    for (x1,y1,x2,y2,ap) in draws:
        shape,a,b = aps.get(ap,("C",0.2,0.2))
        ax.plot([x1,x2],[y1,y2], color=color, alpha=alpha,
                lw=max(0.4,a*2.6*lw_scale), solid_capstyle="round")
    return aps, flashes, draws

fig, ax = plt.subplots(figsize=(12, 9.6), dpi=150)
ax.set_facecolor("#0b3d0b")  # solder green

# layer stack (bottom -> top)
draw_layer(ax, f"{OUT}/{NAME}-B_Cu.gbr", "#1f6b1f", alpha=0.55)        # bottom copper
draw_layer(ax, f"{OUT}/{NAME}-F_Cu.gbr", "#c8902a", alpha=0.9)         # top copper
draw_layer(ax, f"{OUT}/{NAME}-F_Silkscreen.gbr", "#ffffff", alpha=0.95)
draw_layer(ax, f"{OUT}/{NAME}-B_Silkscreen.gbr", "#bbbbbb", alpha=0.4)

# drill holes (dark)
holes = parse_drill(f"{OUT}/{NAME}.drl")
for (x,y,d) in holes:
    ax.add_patch(Circle((x,y), d/2, color="#101010", zorder=5))

# board edge
aps,fl,dr = parse_gerber(f"{OUT}/{NAME}-Edge_Cuts.gbr")
for (x1,y1,x2,y2,ap) in dr:
    ax.plot([x1,x2],[y1,y2], color="#f5f5f5", lw=2.0, zorder=6)

ax.set_xlim(-4, 104); ax.set_ylim(-4, 84)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title("CJ2 Voice Emergency Checklist — Prototype Baseboard (Rev A, 2-layer, 100×80mm)\nGerber layer verification — DEMO/TRAINING ONLY",
             fontsize=11, color="#222")
plt.tight_layout()
plt.savefig(f"{OUT}/{NAME}_preview.png", dpi=150, bbox_inches="tight", facecolor="white")
print("preview ->", f"{OUT}/{NAME}_preview.png")
print("holes:", len(holes), " edge segs:", len(dr))
