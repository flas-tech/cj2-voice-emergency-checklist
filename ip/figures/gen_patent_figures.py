#!/usr/bin/env python3
"""
Generate informal patent drawings (FIG. 1-14) for the provisional application:
"Offline Voice-Driven Advisory Checklist Reader ..."

USPTO-style informal drawings: black line-art on white, sans-serif labels,
figure number + title, reference numerals. Acceptable as informal drawings
with a provisional (37 CFR 1.81 allows informal drawings for provisionals).

Outputs: individual PNGs + a combined PDF (patent_figures.pdf).
Pure matplotlib so no external assets are required.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages
import os

OUT = os.path.dirname(os.path.abspath(__file__))
LW = 1.4
EDGE = "black"
FACE = "white"
FONT = 9
TFONT = 11

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "svg.fonttype": "none",
})


def new_fig(num, title):
    fig, ax = plt.subplots(figsize=(11, 8.5))  # US Letter landscape
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    ax.text(50, 97, f"FIG. {num}", ha="center", va="top",
            fontsize=TFONT + 3, fontweight="bold")
    ax.text(50, 93.3, title, ha="center", va="top", fontsize=TFONT, style="italic")
    return fig, ax


def box(ax, x, y, w, h, label, ref=None, fc=FACE, rounded=True, fs=FONT):
    if rounded:
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15,rounding_size=1.2",
                           linewidth=LW, edgecolor=EDGE, facecolor=fc)
    else:
        p = Rectangle((x, y), w, h, linewidth=LW, edgecolor=EDGE, facecolor=fc)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
            fontsize=fs, wrap=True)
    if ref is not None:
        ax.text(x + w + 0.6, y + h + 0.6, ref, ha="left", va="bottom",
                fontsize=fs - 1, fontweight="bold")
    return (x, y, w, h)


def arrow(ax, x1, y1, x2, y2, style="-|>", dashed=False, lw=LW):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                        mutation_scale=14, linewidth=lw, color=EDGE,
                        linestyle="--" if dashed else "-",
                        shrinkA=2, shrinkB=2)
    ax.add_patch(a)


def cx(b):  # center x
    return b[0] + b[2] / 2

def cy(b):
    return b[1] + b[3] / 2

def right(b):
    return (b[0] + b[2], b[1] + b[3] / 2)

def left(b):
    return (b[0], b[1] + b[3] / 2)

def top(b):
    return (b[0] + b[2] / 2, b[1] + b[3])

def bot(b):
    return (b[0] + b[2] / 2, b[1])


def iso_marker(ax, x, y, label="ISO"):
    """draw a small isolation-barrier symbol (two vertical bars)."""
    ax.plot([x, x], [y - 3, y + 3], color=EDGE, lw=LW)
    ax.plot([x + 1.4, x + 1.4], [y - 3, y + 3], color=EDGE, lw=LW)
    ax.text(x + 0.7, y - 4.4, label, ha="center", va="top", fontsize=FONT - 2,
            fontweight="bold")


figs = []

# ----------------------------------------------------------------------------
# FIG. 1 - System block diagram (dual isolated channels)
# ----------------------------------------------------------------------------
fig, ax = new_fig(1, "System Block Diagram — Dual Galvanically-Isolated Channels")
ap = box(ax, 3, 42, 16, 16, "AIRCRAFT\nAUDIO PANEL", "10", fc="#f2f2f2")
# input chain
iso_in = box(ax, 26, 64, 13, 11, "INPUT\nISOLATION\nBARRIER", "22")
adc = box(ax, 44, 64, 13, 11, "AUDIO\nCODEC / ADC", "24")
mcu = box(ax, 62, 38, 22, 30, "MICROCONTROLLER (SoC)\n\nAFE / VAD (32)\nWake word (34)\nBounded-grammar\nrecognizer (36)\nPlayback sequencer (38)", "30", fc="#eef4fb")
dac = box(ax, 44, 22, 13, 11, "I2S DAC /\nLINE DRIVER", "26")
iso_out = box(ax, 26, 22, 13, 11, "OUTPUT\nISOLATION\nBARRIER", "28")
# cards + annunciator
cfg = box(ax, 88, 60, 10, 9, "CONFIG\nCARD (slot1)", "50", fc="#fdf6e3")
data = box(ax, 88, 48, 10, 9, "DATA\nCARD (slot2)", "52", fc="#fdf6e3")
ann = box(ax, 88, 34, 10, 9, "ANNUN-\nCIATOR", "60", fc="#fbeeee")
sel = box(ax, 88, 22, 10, 9, "SELECT /\nPTT in", "62")

# input path arrows (receive only -> into MCU)
arrow(ax, right(ap)[0], 52, left(iso_in)[0], cy(iso_in))
ax.text(31, 76.5, "receive-only tap", ha="center", fontsize=FONT - 1)
arrow(ax, right(iso_in)[0], cy(iso_in), left(adc)[0], cy(adc))
arrow(ax, right(adc)[0], cy(adc), left(mcu)[0], 62)
iso_marker(ax, 24, 56)
# output path arrows (MCU -> panel COM3)
arrow(ax, left(mcu)[0], 45, right(dac)[0], cy(dac))
arrow(ax, left(dac)[0], cy(dac), right(iso_out)[0], cy(iso_out))
arrow(ax, left(iso_out)[0], cy(iso_out), 19, 47)
ax.text(31, 19, "dedicated COM3-style out", ha="center", fontsize=FONT - 1)
iso_marker(ax, 24, 44)
# cards/annun
arrow(ax, left(cfg)[0], cy(cfg), right(mcu)[0], 60, style="<->")
arrow(ax, left(data)[0], cy(data), right(mcu)[0], 52, style="<->")
arrow(ax, right(mcu)[0], 44, left(ann)[0], cy(ann))
arrow(ax, left(sel)[0], cy(sel), right(mcu)[0], 41)
ax.text(50, 8,
        "Two electrically-separate, galvanically-isolated channels: receive-only INPUT tap (22/24) and dedicated isolated OUTPUT (26/28).",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 2 - Analog input embodiment
# ----------------------------------------------------------------------------
fig, ax = new_fig(2, "Analog Audio-Input Embodiment (Receive-Only, Isolated)")
b1 = box(ax, 5, 50, 17, 14, "Audio-panel\nheadphone/line\noutput", "10")
b2 = box(ax, 27, 50, 16, 14, "High-impedance\nparallel tap", "21")
b3 = box(ax, 48, 50, 16, 14, "600\u03a9 audio\nisolation\ntransformer", "22")
b4 = box(ax, 69, 50, 14, 14, "Series R +\nanti-alias\nnetwork", "23")
b5 = box(ax, 84, 32, 13, 14, "Codec\nline-in (ADC)", "24")
for a, b in [(b1, b2), (b2, b3), (b3, b4)]:
    arrow(ax, right(a)[0], cy(a), left(b)[0], cy(b))
arrow(ax, bot(b4)[0], b4[1], cx(b5), top(b5)[1])
iso_marker(ax, cx(b3) - 0.7, 47)
ax.text(50, 20, "High-impedance parallel tap loads the panel negligibly; transformer (22) blocks any back-feed via the input path.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 3 - Digital input embodiment
# ----------------------------------------------------------------------------
fig, ax = new_fig(3, "Digital Audio-Input Embodiment (Buffered, Receive-Only)")
b1 = box(ax, 6, 48, 18, 16, "Source codec\n(near audio panel)", "10")
b2 = box(ax, 30, 48, 18, 16, "Buffer\n(receive-only)", "21b")
b3 = box(ax, 54, 48, 18, 16, "Codec / ADC\n(I\u00b2S in)", "24")
b4 = box(ax, 54, 24, 18, 14, "MCU generates\nBCLK/WS/MCLK\n(ADC only)", "25")
for a, b in [(b1, b2), (b2, b3)]:
    arrow(ax, right(a)[0], cy(a), left(b)[0], cy(b))
arrow(ax, top(b4)[0], top(b4)[1], bot(b3)[0], b3[1])
ax.text(40, 70, "data: panel \u2192 device only", ha="center", fontsize=FONT - 1)
ax.text(50, 14, "All clocks generated locally for the ADC; no data line is driven back toward any aircraft bus.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 4 - Dual-card architecture
# ----------------------------------------------------------------------------
fig, ax = new_fig(4, "Dual-Card Configuration Architecture & Cross-Card Check")
cfg = box(ax, 8, 55, 30, 26, "CONFIGURATION CARD (slot 1)\n\n\u2022 schema version\n\u2022 AIRCRAFT ID\n\u2022 audio source (analog/digital)\n\u2022 VOX params\n\u2022 fitted-hardware options\n\u2022 install provenance\n(write-protected)", "50", fc="#fdf6e3", fs=FONT - 1)
data = box(ax, 62, 55, 30, 26, "DATA CARD (slot 2)\n\n\u2022 per-aircraft folder\n\u2022 checklist manifest\n  (AIRCRAFT ID, titles,\n   trigger phrases, items)\n\u2022 advance vocabulary\n\u2022 read-aloud clips", "52", fc="#fdf6e3", fs=FONT - 1)
chk = box(ax, 35, 28, 30, 14, "CROSS-CARD\nCONSISTENCY CHECK\nconfig.AIRCRAFT_ID == data.AIRCRAFT_ID ?", "54", fc="#eef4fb", fs=FONT - 1)
arrow(ax, bot(cfg)[0], cfg[1], 42, top(chk)[1])
arrow(ax, bot(data)[0], data[1], 58, top(chk)[1])
ok = box(ax, 18, 8, 24, 11, "MATCH \u2192 load active set", "56")
bad = box(ax, 58, 8, 24, 11, "MISMATCH \u2192 FAULT\n(present nothing)", "58", fc="#fbeeee")
arrow(ax, 45, bot(chk)[1], cx(ok), top(ok)[1])
arrow(ax, 55, bot(chk)[1], cx(bad), top(bad)[1])
ax.text(8, 88, "Installation authority (config) is separated from content authority (data).",
        ha="left", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 5 - Revert-to-unopened state machine
# ----------------------------------------------------------------------------
fig, ax = new_fig(5, "Boot / Validation State Machine — \u201cRevert-to-Unopened\u201d")
boot = box(ax, 8, 80, 30, 8, "POWER-UP / BOOT", "100", fc="#f2f2f2")
steps = [
    ("Config card present\n& readable?", "101"),
    ("Config manifest\nschema-valid?", "102"),
    ("Data card present\n& mountable?", "103"),
    ("Data manifest valid\n& non-empty?", "104"),
    ("All referenced\nclips present?", "105"),
    ("Cross-card AIRCRAFT ID\nconsistent?", "106"),
    ("(opt.) integrity /\nsignature valid?", "107"),
]
y = 69
prev_b = boot
for label, ref in steps:
    b = box(ax, 8, y, 30, 7, label, ref, fc="#eef4fb", fs=FONT - 1)
    arrow(ax, cx(prev_b), prev_b[1], cx(b), top(b)[1])
    # NO branch -> fault
    arrow(ax, right(b)[0], cy(b), 66, cy(b), dashed=True)
    ax.text(52, cy(b) + 1.1, "no", fontsize=FONT - 2)
    prev_b = b
    y -= 8.7
fault = box(ax, 66, 20, 28, 24, "FAULT STATE\n\n\u2022 in-memory checklist\n  store held EMPTY\n\u2022 amber legend\n\u2022 never present partial/\n  stale/mismatched data", "120", fc="#fbeeee", fs=FONT - 1)
okstate = box(ax, 8, y - 0.5, 30, 8, "STORE OK\n\u2192 ready (selected-in: dark)", "110", fc="#eafaef")
arrow(ax, cx(prev_b), prev_b[1], cx(okstate), top(okstate)[1])
ax.text(31, prev_b[1] - 1.7, "all yes", fontsize=FONT - 2)
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 6 - Dark-cockpit annunciator state table
# ----------------------------------------------------------------------------
fig, ax = new_fig(6, "Dark-Cockpit Annunciator States & Power-Up Lamp Test")
rows = [
    ("Selected-IN, healthy", "DARK (nothing shown)", "#ffffff"),
    ("Any fault", "AMBER 'FAULT' legend", "#f5b301"),
    ("Selected-OUT", "WHITE 'OFF'; fault inhibited", "#e8e8e8"),
    ("Power-up lamp test", "All legends ON briefly", "#cccccc"),
]
x0, y0, w, hrow = 14, 66, 72, 10
ax.text(x0 + 18, y0 + hrow + 3, "CONDITION", ha="center", fontsize=FONT, fontweight="bold")
ax.text(x0 + 54, y0 + hrow + 3, "ANNUNCIATOR", ha="center", fontsize=FONT, fontweight="bold")
for i, (cond, ann, color) in enumerate(rows):
    yy = y0 - i * hrow
    ax.add_patch(Rectangle((x0, yy), 36, hrow, fill=False, lw=LW, edgecolor=EDGE))
    ax.add_patch(Rectangle((x0 + 36, yy), 36, hrow, facecolor=color, lw=LW, edgecolor=EDGE))
    ax.text(x0 + 18, yy + hrow / 2, cond, ha="center", va="center", fontsize=FONT - 1)
    ax.text(x0 + 54, yy + hrow / 2, ann, ha="center", va="center", fontsize=FONT - 1)
ax.text(50, 16, "A power-up lamp test verifies the indicator so a failed lamp cannot masquerade as a healthy/dark state.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 7 - Interaction flow
# ----------------------------------------------------------------------------
fig, ax = new_fig(7, "Interaction Flow — Hands-Free (VOX) with PTT Override")
b1 = box(ax, 35, 80, 30, 8, "Crew speaks\nchecklist name", "200")
b2 = box(ax, 35, 70, 30, 8, "Recognizer matches\ntrigger phrase (36)", "201")
b3 = box(ax, 35, 58, 30, 9, "Play item clip via\nisolated OUTPUT (26/28)", "202")
b4 = box(ax, 35, 45, 30, 9, "Await advance word\n/ readback (VAD-gated)", "203")
dec = box(ax, 37, 30, 26, 11, "Recognized?", "204", fc="#eef4fb")
b5 = box(ax, 70, 31, 22, 9, "Next item /\nend of list", "205", fc="#eafaef")
ptt = box(ax, 6, 45, 22, 9, "PTT held =\nforce-listen override", "206", fc="#fdf6e3")
for a, b in [(b1, b2), (b2, b3), (b3, b4)]:
    arrow(ax, bot(a)[0], a[1], top(b)[0], top(b)[1])
arrow(ax, bot(b4)[0], b4[1], top(dec)[0], top(dec)[1])
arrow(ax, right(dec)[0], cy(dec), left(b5)[0], cy(b5))
ax.text(67, cy(dec) + 1.2, "yes", fontsize=FONT - 2)
arrow(ax, top(b5)[0], top(b5)[1], right(b3)[0], cy(b3))
arrow(ax, left(dec)[0], cy(dec), 30, cy(dec), dashed=True)
ax.text(33, cy(dec) - 1.6, "no \u2192 re-prompt", fontsize=FONT - 2)
arrow(ax, right(ptt)[0], cy(ptt), left(b4)[0], cy(b4), dashed=True)
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 8 - Card integrity / authentication
# ----------------------------------------------------------------------------
fig, ax = new_fig(8, "Card Integrity / Authentication Embodiment")
card = box(ax, 8, 60, 30, 20, "CARD CONTENTS\nmanifest + clips\n+ SIGNATURE/HMAC/HASH", "70", fc="#fdf6e3", fs=FONT - 1)
recompute = box(ax, 45, 62, 24, 14, "Recompute hash /\nverify signature\nvs. public key (72)", "71", fc="#eef4fb")
key = box(ax, 45, 80, 24, 8, "Public key in firmware\nor write-protected config", "72")
ok = box(ax, 78, 70, 18, 9, "Valid \u2192 proceed\n(see FIG. 5)", "73", fc="#eafaef")
bad = box(ax, 78, 52, 18, 11, "Invalid \u2192 FAULT\n(present nothing)", "74", fc="#fbeeee")
arrow(ax, right(card)[0], cy(card), left(recompute)[0], cy(recompute))
arrow(ax, bot(key)[0], key[1], top(recompute)[0], top(recompute)[1])
arrow(ax, right(recompute)[0], 71, left(ok)[0], cy(ok))
arrow(ax, right(recompute)[0], 65, left(bad)[0], cy(bad))
ax.text(50, 38, "Tampered, corrupted, or unauthenticated cards are rejected under the revert-to-unopened rule.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 9 - Tamper-evident audit log (hash chain)
# ----------------------------------------------------------------------------
fig, ax = new_fig(9, "Tamper-Evident Configuration / Audit Log (Hash-Chained)")
entries = [
    ("Entry 0\nINSTALL\nshop/date/WO\nhash(genesis)", "80"),
    ("Entry 1\nCONFIG CHG\nshop/date/WO\nhash(Entry0)", "81"),
    ("Entry 2\nCONTENT REV\nrev id/date\nhash(Entry1)", "82"),
    ("Entry n\n...\nhash(Entry n-1)", "83"),
]
x = 7
for i, (lab, ref) in enumerate(entries):
    b = box(ax, x, 50, 19, 22, lab, ref, fc="#fdf6e3", fs=FONT - 1)
    if i > 0:
        arrow(ax, x - 3, 61, x, 61)
    x += 23
ax.text(50, 38, "Each entry includes a hash over the prior entry; deletion, reordering, or back-dating is detectable by recomputing the chain.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 10 - Multi-aircraft fleet data card
# ----------------------------------------------------------------------------
fig, ax = new_fig(10, "Multi-Aircraft (Fleet) Data Card with Active-Set Selection")
data = box(ax, 8, 40, 34, 42,
           "DATA CARD (one physical card)\n\n[ /N123AB  set ]\n[ /N456CD  set ]\n[ /CJ2-type set ]\n[ /N789EF  set ]", "52", fc="#fdf6e3", fs=FONT - 1)
cfg = box(ax, 52, 64, 30, 13, "CONFIG CARD\nactive AIRCRAFT ID = N456CD", "50", fc="#fdf6e3", fs=FONT - 1)
sel = box(ax, 52, 44, 30, 12, "SELECT set whose ID ==\nconfig AIRCRAFT ID", "90", fc="#eef4fb", fs=FONT - 1)
act = box(ax, 52, 26, 30, 11, "ACTIVE SET = N456CD", "91", fc="#eafaef")
none = box(ax, 52, 10, 30, 11, "no match / ambiguous\n\u2192 FAULT (FIG. 5)", "92", fc="#fbeeee")
arrow(ax, right(data)[0], 61, left(cfg)[0], cy(cfg))
arrow(ax, bot(cfg)[0], cfg[1], top(sel)[0], top(sel)[1])
arrow(ax, right(data)[0], 50, left(sel)[0], cy(sel))
arrow(ax, bot(sel)[0], sel[1], top(act)[0], top(act)[1])
arrow(ax, 60, sel[1], 60, top(none)[1], dashed=True)
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 11 - Output-injection safeguards
# ----------------------------------------------------------------------------
fig, ax = new_fig(11, "Active Output-Injection Safeguards (Non-Interference)")
seq = box(ax, 6, 60, 20, 13, "Playback\nsequencer (38)", "38", fc="#eef4fb")
gate = box(ax, 33, 58, 20, 16, "OUTPUT GATE\n(inhibit / mute\nlogic)", "300", fc="#eef4fb")
outp = box(ax, 60, 60, 18, 13, "DAC + iso\nOUTPUT (26/28)", "26/28")
panel = box(ax, 84, 60, 13, 13, "AUDIO\nPANEL", "10", fc="#f2f2f2")
arrow(ax, right(seq)[0], cy(seq), left(gate)[0], cy(gate))
arrow(ax, right(gate)[0], cy(gate), left(outp)[0], cy(outp))
arrow(ax, right(outp)[0], cy(outp), left(panel)[0], cy(panel))
# safeguard inputs
key = box(ax, 12, 38, 24, 9, "(a) COM keying / PTT\nsense \u2192 inhibit", "301")
mof = box(ax, 12, 26, 24, 9, "(b) fault \u2192 mute", "302", fc="#fbeeee")
st = box(ax, 50, 38, 24, 9, "(c) power-up output\nisolation self-test", "303")
wd = box(ax, 50, 26, 24, 9, "(d) playback watchdog\nstall \u2192 mute + fault", "304")
for b in (key, mof):
    arrow(ax, top(b)[0], top(b)[1], cx(gate), gate[1])
for b in (st, wd):
    arrow(ax, top(b)[0], top(b)[1], cx(gate), gate[1])
ax.text(50, 14, "Non-interference is an actively enforced, testable behavior \u2014 not merely a passive consequence of the transformer.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 12 - No-mask audio arbitration
# ----------------------------------------------------------------------------
fig, ax = new_fig(12, "\u201cNo-Mask\u201d Audio Arbitration vs. Required Communications")
tap = box(ax, 6, 62, 22, 12, "Receive tap (22/24)\n/ VAD (32)", "310", fc="#eef4fb")
det = box(ax, 33, 60, 24, 16, "Required-radio /\nATC audio\ndetector", "311", fc="#eef4fb")
arb = box(ax, 63, 60, 30, 16, "ARBITER:\nduck / pause / defer\nadvisory audio,\nthen resume/repeat", "312", fc="#eef4fb")
arrow(ax, right(tap)[0], cy(tap), left(det)[0], cy(det))
arrow(ax, right(det)[0], cy(det), left(arb)[0], cy(arb))
pol = box(ax, 63, 40, 30, 11, "policy (thresholds, hangover)\nfrom removable media", "313", fc="#fdf6e3")
arrow(ax, top(pol)[0], top(pol)[1], bot(arb)[0], arb[1])
ax.text(50, 26, "Advisory read-aloud yields to required communications so a checklist item is delivered intelligibly and never talks over ATC.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 13 - Readback verification
# ----------------------------------------------------------------------------
fig, ax = new_fig(13, "Crew Readback Verification (Challenge & Response)")
read = box(ax, 35, 80, 30, 8, "Read item (e.g.\n\u201cGEAR\u201d) via OUTPUT", "320")
exp = box(ax, 8, 66, 24, 11, "Expected response\nfrom DATA card\n(e.g. \u201cUP\u201d)", "321", fc="#fdf6e3")
wait = box(ax, 35, 66, 30, 9, "Await spoken readback\n(bounded grammar)", "322", fc="#eef4fb")
dec = box(ax, 37, 50, 26, 11, "Readback == expected?", "323", fc="#eef4fb")
adv = box(ax, 70, 51, 22, 9, "YES \u2192 advance", "324", fc="#eafaef")
re = box(ax, 8, 32, 30, 11, "NO / out-of-grammar \u2192\nre-prompt / repeat /\nannunciate mismatch", "325", fc="#fbeeee")
arrow(ax, bot(read)[0], read[1], top(wait)[0], top(wait)[1])
arrow(ax, right(exp)[0], cy(exp), left(wait)[0], cy(wait))
arrow(ax, bot(wait)[0], wait[1], top(dec)[0], top(dec)[1])
arrow(ax, right(dec)[0], cy(dec), left(adv)[0], cy(adv))
arrow(ax, left(dec)[0], cy(dec), top(re)[0], top(re)[1], dashed=True)
arrow(ax, left(re)[0], cy(re), 4, cy(re))
ax.text(4, cy(re) - 3, "loop back to 320", fontsize=FONT - 2)
ax.text(50, 22, "Items may be configured to accept a generic advance word OR a specific verified readback.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# FIG. 14 - Alternate isolation embodiments
# ----------------------------------------------------------------------------
fig, ax = new_fig(14, "Interchangeable Isolation-Barrier Embodiments (Either Channel)")
opts = [
    ("(a) MAGNETIC /\nTRANSFORMER\nbarrier", "330"),
    ("(b) OPTICAL\nisolation\n(opto / optical link)", "331"),
    ("(c) CAPACITIVE\ndigital isolator", "332"),
    ("(d) TRANSFORMER-\nCOUPLED DIGITAL\nisolator", "333"),
]
x = 6
for lab, ref in opts:
    b = box(ax, x, 50, 21, 22, lab, ref, fc="#eef4fb", fs=FONT - 1)
    iso_marker(ax, cx(b) - 0.7, 46)
    x += 23.5
ax.text(50, 34, "Input and output barriers remain INDEPENDENT \u2014 no shared conductive path \u2014 regardless of which isolation means is used.",
        ha="center", fontsize=FONT - 1, style="italic")
ax.text(50, 27, "Reciting alternatives expressly protects the dual-isolated-channel architecture against substitute-technology design-arounds.",
        ha="center", fontsize=FONT - 1, style="italic")
figs.append(fig)

# ----------------------------------------------------------------------------
# Save individual PNGs + combined PDF
# ----------------------------------------------------------------------------
pdf_path = os.path.join(OUT, "patent_figures.pdf")
with PdfPages(pdf_path) as pdf:
    for i, f in enumerate(figs, 1):
        png = os.path.join(OUT, f"FIG_{i:02d}.png")
        f.savefig(png, dpi=150, bbox_inches="tight", facecolor="white")
        pdf.savefig(f, facecolor="white")
        plt.close(f)
print(f"Wrote {len(figs)} figures + {pdf_path}")
print(os.listdir(OUT))
