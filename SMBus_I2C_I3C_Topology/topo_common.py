"""Shared styling for the SMBus/I2C/I3C topology deck (reuses OpenBMC deck helpers)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "OpenBMC_Presentation"))

from deck_helpers import *  # noqa: F401,F403
from deck_helpers import box, text, arrow, rgb, RECT, GREY, DARK, WHITE, NAVY, TEAL, BLUE, PURPLE, ORANGE, GREEN, RED, LIGHT, LEFT, MIDDLE, TOP, RIGHT, CENTER
from pptx.enum.dml import MSO_LINE_DASH_STYLE

I2C, SMB, I3C, PMB, MCTP = TEAL, BLUE, PURPLE, ORANGE, GREEN
BMC_C = rgb("2C3E50")
AGG_C = rgb("455A64")
PANEL = rgb("F7FAFC")
EDGE = rgb("D5DEE8")

SEC = {
    "basics": "1 · Bus basics",
    "bhs": "2 · GNR / BHS",
    "avc": "3 · Avenue City (AVC)",
    "jc": "4 · OKS Johnson City",
    "evo": "5 · Evolution & takeaways",
}
SRC_BHS = "BHS_SP_PC_Architecture_Definition.pptx"
SRC_AVC = "avc-rpas-v0.9 4.pdf"
SRC_JC = "Johnson City Reference Platform Architecture Specification_0v9.pdf"
SRC_OBMC = "861949_OpenBMC_BHS_OKS_Integration_Guide_Rev_1_0.pdf"


def dashed(sh):
    sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return sh


def bus(s, x1, y1, x2, y2, c, label=None, head=False, tail=False, dash=False, lw=None, loff=0.0, w=3.5, lsize=12):
    return arrow(s, x1, y1, x2, y2, color=c, width=w, head=head, tail=tail, dash=dash,
                 label=("**%s**" % label) if label else None, lsize=lsize, lcolor=c, lw=lw, loff=loff)


def lab(s, x, y, t, c=DARK, w=2.4, align=LEFT, size=12, h=0.34):
    return text(s, x, y, w, h, t, size=size, color=c, align=align, anchor=MIDDLE)


def ep(s, x, y, w, h, t, c, size=12, bold=False, dash=False):
    sh = box(s, x, y, w, h, t, fill=WHITE, fg=DARK, size=size, line=c, lw=2, bold=bold)
    return dashed(sh) if dash else sh


def container(s, x, y, w, h, t, line=NAVY, fill=LIGHT, dash=False, size=12):
    sh = box(s, x, y, w, h, t, fill=fill, fg=DARK, size=size, bold=True, line=line, anchor=TOP, lw=1.5)
    return dashed(sh) if dash else sh


def panel(s, x, y, w, h, title, c=NAVY, size=14):
    box(s, x, y, w, h, fill=PANEL, line=EDGE, shape=RECT)
    box(s, x, y, w, 0.42, title, fill=c, size=size, bold=True, shape=RECT)


def tag(s, x, y, t, fill, w=None, size=10, fg=WHITE):
    w = w or 0.085 * len(t) + 0.35
    return box(s, x, y, w, 0.3, t, fill=fill, fg=fg, size=size, bold=True)


def removed(s, x, y, w, h, t, size=12):
    sh = box(s, x, y, w, h, t, fill=rgb("F2F2F2"), fg=GREY, size=size, line=GREY, lw=1.5)
    dashed(sh)
    tag(s, x + w - 1.2, y - 0.31, "\u2715 REMOVED", RED, w=1.2, size=9)
    return sh


def legend(s, x=0.45, y=6.6, items=None):
    items = items or [("I2C", I2C), ("SMBus", SMB), ("I3C", I3C), ("PMBus", PMB), ("MCTP", MCTP)]
    for name, c in items:
        arrow(s, x, y + 0.15, x + 0.4, y + 0.15, color=c, width=3.5, head=False)
        text(s, x + 0.45, y, 1.2, 0.3, name, size=10, color=DARK, anchor=MIDDLE)
        x += 0.62 + 0.085 * len(name) + 0.25


def source(s, t, x=5.4, w=7.5):
    text(s, x, 6.6, w, 0.32, "Source: " + t, size=9, color=GREY, align=RIGHT, anchor=MIDDLE)
