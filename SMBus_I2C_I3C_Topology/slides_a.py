"""Slides 1-7: title, storyline, bus basics, BHS overview, shared-SMBus removal."""
from topo_common import *
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE


def title_slide(d):
    s = d.raw("Opening. Goal: show the SMBus / I2C / I3C topology for GNR/BHS, Avenue City and OKS JC1/JC2 "
              "as ONE architectural transition (BHS/AVC -> OKS/JC), not three unrelated buses.")
    box(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=RECT)
    box(s, 0, 5.0, 13.333, 0.06, fill=rgb("4A9FD8"), shape=RECT)
    text(s, 0.8, 1.1, 11.7, 0.45, "PLATFORM MANAGEMENT BUS ARCHITECTURE", size=16, color=rgb("8FC1EA"), bold=True)
    text(s, 0.8, 1.6, 11.7, 1.0, "SMBus / I2C / I3C Topology", size=46, color=WHITE, bold=True)
    text(s, 0.8, 2.65, 11.7, 0.6, "From GNR / BHS and Avenue City to OKS Johnson City (JC1 / JC2)", size=22,
         color=rgb("BFD7EE"))
    labels = ["GNR / BHS", "Avenue City", "OKS JC1 · 1S", "OKS JC2 · 2S/4S"]
    cols = [BLUE, TEAL, PURPLE, PURPLE]
    for i, (t, c) in enumerate(zip(labels, cols)):
        x = 0.8 + i * 3.05
        box(s, x, 3.7, 2.6, 0.75, t, fill=c, size=17, bold=True)
        if i:
            arrow(s, x - 0.42, 4.075, x - 0.05, 4.075, color=rgb("8FC1EA"), width=2.5)
    text(s, 0.8, 5.3, 11.7, 0.4, "Team walkthrough  ·  November 2026", size=15, color=WHITE)
    text(s, 0.8, 5.8, 11.7, 0.7, "Based on: BHS SP architecture definition · AVC RPAS v0.9 · Johnson City RPAS v0.9 · "
         "OpenBMC BHS/OKS Integration Guide Rev 1.0", size=12, color=rgb("BFD7EE"))
    text(s, 0.8, 6.85, 11.7, 0.35, "Intel Confidential — internal use only", size=10, color=rgb("8FA3B8"))


def storyline(d):
    s = d.slide("Storyline: one transition, not three separate buses",
                "Follow the management architecture from BHS / AVC to OKS / JC", SEC["basics"],
                notes="Walk the five chapters left to right. Then explain the colour code: every diagram uses the "
                      "same colours, so the audience can recognise the bus type without reading labels. "
                      "Dashed = optional/conceptual, red tag = removed in that generation.")
    steps = ["**1  Bus basics**\nI2C · SMBus · I3C\nslides 3–5", "**2  GNR / BHS**\nRTC · I3C_MNG · MCTP\nslides 6–9",
             "**3  Avenue City**\nSMBus branches\nslides 10–13", "**4  OKS / JC**\nsingle BMC · aggregator\nslides 14–17",
             "**5  Evolution**\nbig picture · takeaways\nslides 18–20"]
    cols = [rgb("4A9FD8"), BLUE, TEAL, PURPLE, NAVY]
    for i, t in enumerate(steps):
        x = 0.45 + i * 2.52
        box(s, x, 1.45, 2.3, 1.15, t, fill=cols[i], size=13)
        if i:
            arrow(s, x - 0.2, 2.02, x - 0.03, 2.02, color=GREY, width=2)

    panel(s, 0.45, 2.95, 5.6, 3.55, "How to read the diagrams", NAVY)
    rows = [("I2C", I2C, "general-purpose 2-wire bus"), ("SMBus", SMB, "system-management bus (I2C-derived)"),
            ("I3C", I3C, "MIPI I3C management bus"), ("PMBus", PMB, "power commands over SMBus"),
            ("MCTP", MCTP, "management transport (logical layer)")]
    for i, (n, c, t) in enumerate(rows):
        y = 3.55 + i * 0.47
        arrow(s, 0.75, y + 0.17, 1.35, y + 0.17, color=c, width=4, head=False)
        lab(s, 1.5, y, "**%s** — %s" % (n, t), w=4.4, size=13)
    y = 3.55 + 5 * 0.47
    arrow(s, 0.75, y + 0.17, 1.35, y + 0.17, color=GREY, width=2.5, head=False, dash=True)
    lab(s, 1.5, y, "optional / conceptual path", w=2.6, size=13)
    tag(s, 4.1, y + 0.02, "\u2715 REMOVED", RED, w=1.2, size=9)

    panel(s, 6.35, 2.95, 6.5, 3.55, "Source documents", NAVY)
    table(s, 6.5, 3.5, 6.2, [
        ["Document", "Used for"],
        [SRC_BHS, "GNR/BHS: RTC, I3C_MNG, shared SMBus"],
        [SRC_AVC, "AVC SMBus / PMBus / FPGA nets"],
        ["Johnson City RPAS 0v9", "OKS JC1/JC2, aggregator, LTPI, I3C_PCIe"],
        ["861949 OpenBMC BHS/OKS Guide", "OpenBMC / MCTP integration"],
        ["Public: I2C, SMBus, MIPI I3C, SNIA", "Protocol background"],
    ], col_w=[3.2, 3.0], row_h=0.48, size=11)


def _mini_bus(s, x, y, w, c, title, sub, ctrl, tgts, items):
    box(s, x, y, w, 0.55, title, fill=c, size=20, bold=True)
    text(s, x, y + 0.58, w, 0.32, sub, size=11, color=GREY, align=CENTER)
    cy = y + 1.0
    box(s, x + w / 2 - 0.85, cy, 1.7, 0.45, ctrl, fill=NAVY, size=12)
    l1, l2 = cy + 0.75, cy + 0.9
    bus(s, x + 0.6, l1, x + w - 0.15, l1, c, w=2.5)
    bus(s, x + 0.6, l2, x + w - 0.15, l2, c, w=2.5)
    text(s, x + 0.05, l1 - 0.13, 0.55, 0.25, "SDA", size=8, color=c, bold=True)
    text(s, x + 0.05, l2 - 0.08, 0.55, 0.25, "SCL", size=8, color=c, bold=True)
    bus(s, x + w / 2, cy + 0.45, x + w / 2, l1, c, w=2)
    n = len(tgts)
    step = (w - 0.75) / n
    for i, t in enumerate(tgts):
        tx = x + 0.6 + i * step
        bus(s, tx + step / 2 - 0.06, l2, tx + step / 2 - 0.06, cy + 1.25, c, w=2)
        ep(s, tx, cy + 1.25, step - 0.12, 0.5, t, c, size=10)
    bullets(s, x, cy + 1.95, w, 2.4, items, size=13, gap=5, mark=c)


def basics(d):
    s = d.slide("I2C, SMBus and I3C — same wires, different rules",
                "Think of them as layers of one management fabric, not three unrelated networks", SEC["basics"],
                notes="I2C is the wiring and basic protocol. SMBus is I2C plus system-management discipline "
                      "(timeouts, PEC, alerts) — PMBus rides on it for power devices. I3C keeps a two-wire SDA/SCL "
                      "concept but is push-pull, faster, assigns addresses dynamically and lets targets interrupt "
                      "in-band. That is why newer management paths (MCTP, PCIe sideband) move to I3C.")
    _mini_bus(s, 0.45, 1.35, 4.0, I2C, "I2C", "general-purpose 2-wire bus", "Controller",
              ["EEPROM", "RTC", "Sensor"],
              ["Two wires: **SDA** data + **SCL** clock", "Open-drain with pull-ups", "100 kHz / 400 kHz / 1 MHz (Fm+)",
               "Static 7-bit target addresses", "**Platform use:** RTC, FRU EEPROM"])
    _mini_bus(s, 4.62, 1.35, 4.0, SMB, "SMBus", "I2C + system-management rules", "Host / BMC",
              ["Temp", "SPD", "PSU (PMBus)"],
              ["Derived from I2C, tighter limits", "Clock-low timeout → no hung bus", "PEC (CRC-8), SMBALERT#, ARP",
               "**PMBus** = power commands on SMBus", "**Platform use:** sensors, PSU/VR, debug"])
    _mini_bus(s, 8.79, 1.35, 4.0, I3C, "I3C", "MIPI I3C management bus", "I3C Controller",
              ["MCTP EP", "Telemetry", "Legacy I2C"],
              ["Same 2-wire idea, push-pull", "12.5 MHz SDR (HDR modes faster)", "Dynamic addressing",
               "In-band interrupts (IBI)", "**Platform use:** MCTP, PCIe sideband"])


def compare(d):
    s = d.slide("At a glance: what each bus adds", "Public protocol background — not platform specific",
                SEC["basics"],
                notes="Use the table only to anchor vocabulary. Key rows: addressing (static vs dynamic), alerts "
                      "(extra wire vs in-band) and speed. Those three rows explain the OKS move to I3C later.")
    table(s, 0.45, 1.4, 12.43, [
        ["Attribute", "I2C", "SMBus", "I3C"],
        ["Relationship", "Base 2-wire bus", "I2C-derived, system-management rules", "MIPI successor, I2C-compatible"],
        ["Typical speed", "100 kHz / 400 kHz / 1 MHz", "10–100 kHz (SMBus 3.x up to 1 MHz)", "12.5 MHz SDR, HDR higher"],
        ["Addressing", "Static 7-bit", "Static 7-bit + ARP", "Dynamic address assignment"],
        ["Alerts / interrupts", "None (needs GPIO)", "SMBALERT# side-band wire", "In-band interrupt (IBI)"],
        ["Error handling", "None", "PEC (CRC-8), clock-low timeout", "Parity, controller-owned clock"],
        ["Drive", "Open-drain", "Open-drain", "Push-pull (open-drain for legacy)"],
        ["Hot-join", "No", "No", "Yes"],
        ["Platform role", "RTC, FRU EEPROM, simple devices", "Sensors, SPD, PMBus PSU/VR, debug",
         "I3C_MNG (MCTP), I3C_PCIe, telemetry"],
    ], col_w=[2.3, 3.1, 3.5, 3.53], row_h=0.5, size=12)
    note(s, 0.45, 6.0, 12.43, 0.5, "Rule of thumb: **I2C** = the wiring · **SMBus** = management discipline on that "
         "wiring · **I3C** = faster, interrupt-capable successor", size=13)


def why_i3c(d):
    s = d.slide("Why the industry moves sideband management to I3C",
                "Mux-heavy SMBus/I2C trees struggle with MCTP, async and large-message traffic", SEC["basics"],
                notes="Left: identical devices share the same SMBus address, so each one needs its own mux channel. "
                      "Every access = select mux + transaction; no in-band way for a device to raise attention. "
                      "Right: I3C assigns dynamic addresses and supports in-band interrupts, so a flat bus or hub "
                      "works and MCTP gets more bandwidth. SNIA public material describes exactly this problem.")
    panel(s, 0.45, 1.35, 6.05, 5.15, "SMBus / I2C: mux tree", SMB)
    box(s, 2.55, 1.95, 1.85, 0.55, "BMC", fill=BMC_C, size=14, bold=True)
    bus(s, 3.475, 2.5, 3.475, 3.0, SMB)
    box(s, 2.75, 3.0, 1.45, 0.5, "MUX", fill=GREY, size=13, bold=True)
    for i in range(4):
        x = 0.7 + i * 1.45
        bus(s, 3.475, 3.5, x + 0.65, 4.15, SMB, w=2.5)
        ep(s, x, 4.15, 1.3, 0.55, "EP\n(addr A)", SMB, size=10)
    bullets(s, 0.7, 4.9, 5.6, 1.6, ["Same address on every slot → one mux channel each",
                                     "Mux select = extra transactions + firmware state",
                                     "No in-band alert → polling or extra wires",
                                     "Slow for large / asynchronous MCTP messages"], size=12, gap=3, mark=SMB)

    panel(s, 6.83, 1.35, 6.05, 5.15, "I3C: flat bus (hubs where needed)", I3C)
    box(s, 8.93, 1.95, 1.85, 0.55, "BMC", fill=BMC_C, size=14, bold=True)
    bus(s, 9.855, 2.5, 9.855, 3.35, I3C)
    bus(s, 7.1, 3.35, 12.6, 3.35, I3C)
    for i in range(4):
        x = 7.1 + i * 1.4
        bus(s, x + 0.62, 3.35, x + 0.62, 4.15, I3C, w=2.5)
        ep(s, x, 4.15, 1.25, 0.55, "EP\n(dyn addr %d)" % (i + 1), I3C, size=10)
    arrow(s, 12.42, 4.1, 12.42, 3.45, color=I3C, width=1.5, dash=True)
    lab(s, 11.95, 3.6, "**IBI**", I3C, w=0.45, size=10, align=CENTER)
    bullets(s, 7.08, 4.9, 5.6, 1.6, ["Dynamic addressing → no address collisions",
                                     "In-band interrupts → targets signal the BMC",
                                     "More bandwidth for MCTP / telemetry",
                                     "Fewer muxes, simpler firmware"], size=12, gap=3, mark=I3C)
    source(s, "SNIA public material on SMBus/I2C vs I3C for MCTP — diagram is illustrative")


def bhs_overview(d):
    s = d.slide("GNR / BHS: management buses around the CPU",
                "Three changes to remember: I2C RTC · I3C_MNG + MCTP · shared SMBus removed", SEC["bhs"],
                notes="This is the BHS map; the next three slides zoom in. Left: the RTC is an I2C device "
                      "reachable from both the CPU and the BMC. Right: the new I3C_MNG interface carries MCTP to the "
                      "BMC. Centre: the old BMC Shared SMBus is gone — its mux replaced by a level translator.")
    box(s, 4.9, 1.45, 3.5, 0.75, "GNR Processor (BHS)", fill=NAVY, size=16, bold=True)
    ep(s, 0.9, 3.35, 2.8, 0.8, "**I2C RTC device**\n2 × I2C ports · 400 kHz", I2C)
    removed(s, 5.15, 3.4, 3.0, 0.75, "BMC Shared SMBus\nmux → level translator")
    box(s, 9.6, 3.35, 2.8, 0.8, "**MCTP**\nover I3C", fill=MCTP, size=13)
    box(s, 4.9, 5.35, 3.5, 0.85, "**BMC** (DC-SCM)\nOpenBMC management stack", fill=BMC_C, size=13)
    bus(s, 5.3, 2.2, 2.3, 3.35, I2C)
    bus(s, 2.3, 4.15, 5.3, 5.35, I2C)
    bus(s, 8.0, 2.2, 11.0, 3.35, I3C)
    bus(s, 11.0, 4.15, 8.0, 5.35, MCTP)
    lab(s, 2.2, 2.3, "**I2C (CPU port)**", I2C, w=1.9, align=RIGHT, size=13)
    lab(s, 1.85, 4.9, "**I2C (BMC port)**", I2C, w=1.9, align=RIGHT, size=13)
    lab(s, 9.4, 2.3, "**I3C_MNG**", I3C, w=1.9, size=13)
    lab(s, 9.6, 4.9, "**MCTP**", MCTP, w=1.9, size=13)
    bus(s, 6.65, 2.2, 6.65, 3.4, GREY, dash=True, w=2)
    bus(s, 6.65, 4.15, 6.65, 5.35, GREY, dash=True, w=2)
    lab(s, 0.9, 4.2, "details → slide 8", GREY, w=1.4, size=10)
    lab(s, 5.15, 4.2, "details → slide 7", GREY, w=1.4, size=10)
    lab(s, 11.1, 4.2, "details → slide 9", GREY, w=1.4, size=10)
    legend(s, items=[("I2C", I2C), ("I3C", I3C), ("MCTP", MCTP)])
    source(s, SRC_BHS + "  ·  functional view, not a schematic")


def bhs_shared(d):
    s = d.slide("BHS change ①: BMC Shared SMBus removed",
                "The mux that arbitrated bus ownership is replaced by a level translator", SEC["bhs"],
                notes="A mux decides WHO drives a bus segment — it needs a select signal and ownership hand-off. "
                      "A level translator only bridges voltage domains — no ownership switching. Removing the shared "
                      "SMBus therefore simplifies BMC firmware and removes a class of 'wrong owner / stuck mux' bugs. "
                      "Endpoints on the left are generic; take exact connectivity from the BHS architecture deck.")
    panel(s, 0.45, 1.35, 5.95, 4.65, "Before: shared SMBus behind a mux", GREY)
    box(s, 0.8, 2.05, 2.0, 0.6, "BMC", fill=BMC_C, size=14, bold=True)
    box(s, 4.0, 2.05, 2.0, 0.6, "Second bus owner", fill=GREY, size=12)
    box(s, 2.65, 3.05, 1.6, 0.55, "MUX", fill=GREY, size=13, bold=True)
    bus(s, 1.8, 2.65, 3.1, 3.05, SMB, w=2.5)
    bus(s, 5.0, 2.65, 3.8, 3.05, SMB, w=2.5)
    bus(s, 3.45, 3.6, 3.45, 4.1, SMB)
    bus(s, 0.8, 4.1, 6.0, 4.1, SMB)
    lab(s, 0.8, 3.68, "**shared SMBus segment**", SMB, w=2.4, size=12)
    for i in range(3):
        bus(s, 1.5 + i * 1.75, 4.1, 1.5 + i * 1.75, 4.45, SMB, w=2)
        ep(s, 0.85 + i * 1.75, 4.45, 1.3, 0.5, "Shared device", SMB, size=10)
    bullets(s, 0.7, 5.1, 5.6, 0.9, ["Mux decides who owns the bus", "Needs select GPIO + ownership hand-off"],
            size=12, gap=2, mark=GREY)

    box(s, 6.55, 3.35, 0.35, 0.55, shape=MSO_SHAPE.RIGHT_ARROW, fill=rgb("4A9FD8"))

    panel(s, 6.98, 1.35, 5.9, 4.65, "BHS SP: level translator instead", BLUE)
    box(s, 8.95, 2.05, 2.0, 0.6, "BMC", fill=BMC_C, size=14, bold=True)
    bus(s, 9.95, 2.65, 9.95, 3.05, SMB)
    box(s, 8.75, 3.05, 2.4, 0.6, "**Level translator**\nvoltage shift only", fill=TEAL, size=11)
    bus(s, 9.95, 3.65, 9.95, 4.45, SMB)
    ep(s, 9.0, 4.45, 1.9, 0.5, "Target device(s)", SMB, size=10)
    removed(s, 7.25, 2.2, 1.45, 0.6, "Shared\nSMBus", size=10)
    bullets(s, 7.2, 5.1, 5.6, 0.9, ["No ownership switching — only voltage bridged",
                                    "Simpler BMC firmware, fewer failure modes"], size=12, gap=2, mark=BLUE)
    note(s, 0.45, 6.1, 12.43, 0.42, "Diagram explains mux vs. translator; copy exact endpoints from " + SRC_BHS,
         size=11)


def build(d):
    for f in (title_slide, storyline, basics, compare, why_i3c, bhs_overview, bhs_shared):
        f(d)
