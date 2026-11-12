"""Slides 15-20: BMC model, LTPI, I3C_PCIe, big picture, comparison, takeaways."""
from topo_common import *
from pptx.enum.shapes import MSO_SHAPE


def bmc_model(d):
    s = d.slide("BMC model: local BMC per board  →  one system BMC",
                "The biggest topology change from Birch Stream to OKS", SEC["jc"],
                notes="On Birch Stream each modular motherboard had a local BMC; one acted as the legacy BMC and "
                      "communicated with the non-legacy BMCs. OKS has exactly one BMC for 1S, 2S and 4S; for "
                      "multi-HPM systems the aggregator provides the mux/hub/glue paths to each HPM. The bottom "
                      "cards are our interpretation of what that means for OpenBMC work.")
    panel(s, 0.45, 1.35, 5.95, 3.85, "Birch Stream: local BMC on each modular board", BLUE)
    for i, (role, t) in enumerate((("Legacy BMC", "primary"), ("Non-legacy BMC", "secondary"))):
        x = 0.65 + i * 3.1
        container(s, x, 1.95, 2.35, 3.0, "Modular MB / HPM%d" % i, line=NAVY, size=12)
        box(s, x + 0.15, 2.5, 2.05, 0.8, "**%s**\n(%s)" % (role, t), fill=BMC_C, size=12)
        box(s, x + 0.3, 3.85, 1.75, 0.7, "**CPU**", fill=NAVY, size=13)
        bus(s, x + 1.17, 3.3, x + 1.17, 3.85, SMB, w=2.5)
    bus(s, 2.85, 2.9, 3.9, 2.9, DARK, head=True, tail=True, w=2.5)
    tag(s, 2.92, 2.48, "BMC ↔ BMC", WHITE, w=0.92, fg=DARK, size=9)

    box(s, 6.5, 2.95, 0.4, 0.6, shape=MSO_SHAPE.RIGHT_ARROW, fill=rgb("4A9FD8"))

    panel(s, 6.98, 1.35, 5.9, 3.85, "OKS: one BMC for 1S / 2S / 4S", I3C)
    box(s, 8.43, 1.95, 3.0, 0.65, "**Single system BMC**", fill=BMC_C, size=14)
    bus(s, 9.93, 2.6, 9.93, 2.95, DARK, w=3)
    box(s, 7.3, 2.95, 5.25, 0.6, "**Aggregator** — mux · hub · glue", fill=AGG_C, size=13)
    for i, n in enumerate(("HPM0", "HPM1", "HPMn")):
        x = 7.3 + i * 1.8
        bus(s, x + 0.82, 3.55, x + 0.82, 3.85, DARK, w=2.5)
        container(s, x, 3.85, 1.65, 1.1, n + "  (no BMC)", line=NAVY, size=10)
        box(s, x + 0.3, 4.3, 1.05, 0.5, "CPU", fill=NAVY, size=12, bold=True)

    lab(s, 0.45, 5.3, "**What changes for us** (interpretation)", NAVY, w=6, size=13)
    cards = [("Firmware", "One BMC image and config manages every HPM"),
             ("Topology", "Address collisions solved by aggregator mux / hub"),
             ("Debug", "Bus numbering depends on aggregator channel per HPM")]
    for i, (h, t) in enumerate(cards):
        x = 0.45 + i * 4.2
        box(s, x, 5.68, 1.2, 0.8, "**%s**" % h, fill=I3C, size=12, shape=RECT)
        box(s, x + 1.2, 5.68, 2.8, 0.8, t, fill=WHITE, fg=DARK, size=12, line=EDGE, shape=RECT)
    source(s, SRC_JC)


def ltpi(d):
    s = d.slide("OKS: SMBus is NOT tunnelled through LTPI",
                "Removing dual-node support freed I2C channels on the DC-SCM connector", SEC["jc"],
                notes="The JC spec states OKS does not tunnel SMBus through LTPI. Reason: after dual-node support was "
                      "removed, additional I2C channels became available on the DC-SCM connector, so there is no "
                      "longer a need to tunnel a specific I2C lane through LTPI. Do NOT say LTPI disappears — only "
                      "that SMBus is not carried over it.")
    panel(s, 0.45, 1.35, 5.95, 4.25, "Earlier DC-SCM approach", GREY)
    box(s, 2.2, 1.95, 2.4, 0.6, "**DC-SCM · BMC**", fill=BMC_C, size=13)
    bus(s, 3.4, 2.55, 3.4, 2.85, SMB)
    box(s, 1.7, 2.85, 3.4, 0.8, "**LTPI link**\nI2C lane tunnelled inside", fill=PALE, fg=DARK, size=12, line=GREY,
        lw=2, shape=RECT)
    bus(s, 3.4, 3.65, 3.4, 3.95, SMB)
    box(s, 2.2, 3.95, 2.4, 0.6, "HPM-side LTPI endpoint", fill=AGG_C, size=11)
    bus(s, 3.4, 4.55, 3.4, 4.85, SMB)
    ep(s, 2.2, 4.85, 2.4, 0.55, "I2C / SMBus target", SMB, size=11)

    box(s, 6.5, 3.2, 0.4, 0.6, shape=MSO_SHAPE.RIGHT_ARROW, fill=rgb("4A9FD8"))

    panel(s, 6.98, 1.35, 5.9, 4.25, "OKS: dedicated I2C channels", I2C)
    box(s, 7.3, 1.95, 2.8, 0.6, "**DC-SCM · BMC**", fill=BMC_C, size=13)
    box(s, 7.3, 2.95, 5.3, 0.5, "DC-SCM connector", fill=LIGHT, fg=DARK, size=12, bold=True, line=NAVY)
    for i in range(5):
        x = 7.6 + i * 0.55
        c = I2C if i % 2 == 0 else SMB
        bus(s, x, 2.55, x, 2.95, c, w=2.5)
        bus(s, x, 3.45, x, 4.55, c, w=2.5)
    lab(s, 10.25, 3.55, "**direct I2C channels**", I2C, w=2.4, size=12)
    tag(s, 10.25, 3.98, "LTPI still present — not carrying SMBus", PALE, w=2.55, fg=DARK, size=8)
    box(s, 7.3, 4.55, 5.3, 0.75, "**Aggregator / HPM**", fill=AGG_C, size=14)

    steps = ["Dual-node support removed", "Spare I2C channels on DC-SCM connector", "No need to tunnel I2C via LTPI",
             "Direct, simpler SMBus/I2C paths"]
    for i, t in enumerate(steps):
        x = 0.45 + i * 3.2
        box(s, x, 5.8, 2.85, 0.65, t, fill=[GREY, I2C, I2C, NAVY][i], size=12, bold=True)
        if i:
            arrow(s, x - 0.33, 6.125, x - 0.04, 6.125, color=GREY, width=2)
    source(s, SRC_JC)


def i3c_pcie(d):
    s = d.slide("OKS: SMB_PCIe deprecated in favour of I3C_PCIe",
                "PCIe CEM and SNIA EDSFF management devices move to I3C", SEC["jc"],
                notes="This is the cleanest SMBus-to-I3C example. The JC spec deprecates SMB_PCIe in OKS in favour "
                      "of I3C_PCIe for PCIe CEM / SNIA EDSFF management devices. It is not a rename: I3C gives "
                      "dynamic addressing, in-band interrupts and more bandwidth for MCTP to PCIe, CXL and storage "
                      "devices — the same problems SNIA describes with mux-heavy SMBus trees.")
    panel(s, 0.45, 1.35, 5.95, 3.7, "Before: SMB_PCIe", SMB)
    tag(s, 4.75, 1.41, "DEPRECATED", RED, w=1.45, size=10)
    box(s, 2.2, 1.95, 2.4, 0.6, "**BMC**", fill=BMC_C, size=14)
    bus(s, 3.4, 2.55, 3.4, 3.05, SMB)
    lab(s, 3.55, 2.62, "SMB_PCIe", SMB, w=1.3, size=11)
    box(s, 2.7, 3.05, 1.4, 0.5, "MUX", fill=GREY, size=12, bold=True)
    for i, t in enumerate(("CEM slot", "CEM slot", "EDSFF", "EDSFF")):
        x = 0.65 + i * 1.42
        bus(s, 3.4, 3.55, x + 0.65, 4.2, SMB, w=2.5)
        ep(s, x, 4.2, 1.3, 0.55, t, SMB, size=11)

    box(s, 6.5, 2.9, 0.4, 0.6, shape=MSO_SHAPE.RIGHT_ARROW, fill=rgb("4A9FD8"))

    panel(s, 6.98, 1.35, 5.9, 3.7, "OKS: I3C_PCIe", I3C)
    box(s, 8.73, 1.95, 2.4, 0.6, "**BMC**", fill=BMC_C, size=14)
    bus(s, 9.93, 2.55, 9.93, 3.4, I3C)
    lab(s, 10.08, 2.75, "I3C_PCIe", I3C, w=1.3, size=11)
    bus(s, 7.25, 3.4, 12.6, 3.4, I3C)
    for i, t in enumerate(("PCIe CEM", "PCIe CEM", "EDSFF", "EDSFF")):
        x = 7.25 + i * 1.35
        bus(s, x + 0.6, 3.4, x + 0.6, 4.2, I3C, w=2.5)
        ep(s, x, 4.2, 1.2, 0.55, t, I3C, size=11)

    cards = [("More bandwidth", "Richer MCTP traffic for PCIe / CXL / storage devices"),
             ("In-band interrupts", "Devices raise events without polling or extra wires"),
             ("Fewer muxes", "Dynamic addressing avoids per-slot address collisions")]
    for i, (h, t) in enumerate(cards):
        x = 0.45 + i * 4.2
        box(s, x, 5.2, 4.0, 0.4, h, fill=I3C, size=13, bold=True, shape=RECT)
        box(s, x, 5.6, 4.0, 0.85, t, fill=WHITE, fg=DARK, size=12, line=EDGE, shape=RECT)
    source(s, SRC_JC + "  ·  SNIA public material")


def big_picture(d):
    s = d.slide("The big picture: BHS / AVC  →  OKS / JC", "The one diagram to remember", SEC["evo"],
                notes="If you only have two minutes, use this slide. Left: BHS/AVC is SMBus-rich, BMC per board, with "
                      "I3C appearing for CPU management (I3C_MNG). Right: OKS/JC centralises on one BMC, uses direct "
                      "I2C channels instead of LTPI tunnelling, an aggregator for JC2, and I3C_PCIe for PCIe "
                      "sideband. Exact physical connectivity must come from schematics/RPAS.")
    panel(s, 0.45, 1.35, 5.85, 4.25, "BHS / AVC", BLUE)
    box(s, 2.05, 1.95, 2.65, 0.55, "**GNR CPU**", fill=NAVY, size=14)
    ep(s, 0.7, 2.85, 2.1, 0.55, "I2C RTC", I2C, size=12, bold=True)
    box(s, 3.95, 2.85, 2.1, 0.55, "I3C_MNG → MCTP", fill=I3C, size=12, bold=True)
    bus(s, 2.7, 2.5, 1.75, 2.85, I2C, w=2.5)
    bus(s, 4.1, 2.5, 5.0, 2.85, I3C, w=2.5)
    box(s, 2.05, 3.75, 2.65, 0.55, "**BMC** (per board)", fill=BMC_C, size=13)
    bus(s, 1.75, 3.4, 2.6, 3.75, I2C, w=2.5)
    bus(s, 5.0, 3.4, 4.2, 3.75, MCTP, w=2.5)
    for i, (t, c) in enumerate((("PMBus\nPSU / VR", PMB), ("Sensors", SMB), ("FPGA /\ndebug", SMB),
                                ("Host debug", SMB))):
        x = 0.65 + i * 1.4
        bus(s, 3.375, 4.3, x + 0.62, 4.75, c, w=2)
        ep(s, x, 4.75, 1.25, 0.65, t, c, size=10)

    box(s, 6.45, 3.15, 0.4, 0.6, shape=MSO_SHAPE.RIGHT_ARROW, fill=rgb("4A9FD8"))

    panel(s, 7.03, 1.35, 5.85, 4.25, "OKS / JC", I3C)
    box(s, 8.63, 1.95, 2.65, 0.55, "**Single BMC** (DC-SCM)", fill=BMC_C, size=13)
    ep(s, 7.25, 2.85, 2.6, 0.7, "Direct I2C channels\n(no SMBus over LTPI)", I2C, size=11)
    box(s, 10.1, 2.85, 2.55, 0.7, "**I3C_PCIe**", fill=I3C, size=13)
    bus(s, 9.3, 2.5, 8.55, 2.85, I2C, w=2.5)
    bus(s, 10.6, 2.5, 11.35, 2.85, I3C, w=2.5)
    box(s, 7.25, 3.85, 2.6, 0.55, "**Aggregator** (JC2)", fill=AGG_C, size=12)
    bus(s, 8.55, 3.55, 8.55, 3.85, I2C, w=2.5)
    for i, n in enumerate(("HPM0", "HPM1", "HPMn")):
        x = 7.25 + i * 0.9
        bus(s, x + 0.4, 4.4, x + 0.4, 4.75, DARK, w=2)
        container(s, x, 4.75, 0.8, 0.65, n, line=NAVY, size=10)
    bus(s, 11.375, 3.55, 11.375, 4.75, I3C, w=2.5)
    ep(s, 10.1, 4.75, 2.55, 0.65, "PCIe CEM / EDSFF", I3C, size=11)
    note(s, 0.45, 5.75, 12.43, 0.72, "**BHS/AVC:** SMBus-rich, BMC per board, I3C arrives for CPU mgmt   ➜   "
         "**OKS/JC:** one BMC + aggregator, direct I2C, I3C for PCIe sideband", size=13)
    legend(s)


def comparison(d):
    s = d.slide("Side-by-side comparison", "What is documented for each platform", SEC["evo"],
                notes="Read row by row. 'Confirm in JC RPAS' marks items not covered by the retrieved sources — "
                      "don't guess them in the meeting.")
    table(s, 0.45, 1.35, 12.43, [
        ["Area", "GNR / BHS · AVC", "OKS JC1 (1S)", "OKS JC2 (2S / 4S)"],
        ["BMC architecture", "Local BMC per modular board (legacy + non-legacy)", "Single system BMC",
         "Single system BMC"],
        ["Aggregator", "No", "Not needed (direct to HPM)", "Yes — between DC-SCM and HPMs"],
        ["Mux / hub / glue", "Muxes on AVC host-debug and PMBUS2 VR paths", "Simple single-HPM connection",
         "Provided by aggregator"],
        ["BMC shared SMBus", "Removed (mux → level translator)", "N/A — centralised BMC", "N/A — centralised BMC"],
        ["RTC", "I2C RTC, CPU + BMC ports @ 400 kHz", "Confirm in JC RPAS", "Confirm in JC RPAS"],
        ["CPU mgmt / MCTP", "I3C_MNG = MCTP path (PECI repl., telemetry, SPDM)", "MCTP in OKS OpenBMC stack",
         "MCTP via single BMC"],
        ["PCIe sideband", "SMB_PCIe (SMBus)", "I3C_PCIe", "I3C_PCIe"],
        ["SMBus over LTPI", "Earlier DC-SCM: I2C lane tunnelled", "Not tunnelled", "Not tunnelled"],
    ], col_w=[2.2, 4.33, 2.8, 3.1], row_h=0.56, size=12)
    source(s, SRC_BHS + " · " + SRC_AVC + " · Johnson City RPAS 0v9 · OpenBMC BHS/OKS Guide", x=0.45, w=12.43)


def takeaways(d):
    s = d.slide("5 things to remember", "…and what to validate next", SEC["evo"],
                notes="Close with the five points, then the open items. Emphasise #5: SMB_PCIe -> I3C_PCIe and no "
                      "SMBus over LTPI are the clearest signals that I3C is becoming the main management bus.")
    items = [("I2C is the base bus; SMBus is its management-oriented derivative", I2C),
             ("BHS adds **I3C_MNG** — the CPU's MCTP path when PCIe is unavailable", I3C),
             ("AVC splits SMBus into **debug, sensor, PMBus/VR and FPGA** branches", SMB),
             ("OKS centralises on **one BMC**; JC2 adds an aggregator (mux / hub / glue)", AGG_C),
             ("OKS: **no SMBus over LTPI**; **SMB_PCIe → I3C_PCIe**", I3C)]
    for i, (t, c) in enumerate(items):
        y = 1.4 + i * 0.98
        box(s, 0.45, y, 0.8, 0.8, str(i + 1), fill=c, size=22, bold=True, shape=OVAL)
        box(s, 1.4, y, 6.6, 0.8, t, fill=WHITE, fg=DARK, size=14, line=EDGE, align=LEFT, shape=RECT)
    panel(s, 8.35, 1.4, 4.53, 4.72, "Next steps / open items", NAVY)
    bullets(s, 8.5, 2.0, 4.3, 4.1, ["Copy exact physical connectivity from schematics / RPAS",
                                    "Confirm JC RTC and CPU-management (I3C) topology",
                                    "Map each bus to OpenBMC I2C/I3C bus numbers and configs",
                                    "Validate aggregator mux/hub channels for 2S vs 4S",
                                    "Q&A / discussion"], size=15, gap=14)
    note(s, 0.45, 6.25, 12.43, 0.45, "Trend: **SMBus/I2C** stays for simple devices — **I3C** takes over "
         "MCTP-class management traffic.", size=13, fill=rgb("ECE6F6"), accent=I3C)


def build(d):
    for f in (bmc_model, ltpi, i3c_pcie, big_picture, comparison, takeaways):
        f(d)
