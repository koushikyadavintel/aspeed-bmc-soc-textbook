"""Slides 8-14: BHS RTC, BHS I3C_MNG, AVC topology, JC1 vs JC2."""
from topo_common import *


def bhs_rtc(d):
    s = d.slide("BHS change ②: I2C RTC shared by CPU and BMC",
                "Platform is bootable without a PCH, so a discrete I2C RTC supplies time", SEC["bhs"],
                notes="Without a PCH there is no PCH-hosted RTC, so BHS uses a common I2C RTC. It has two I2C "
                      "interfaces at 400 kHz: the primary faces the CPU, the secondary faces the BMC. The BMC side "
                      "has greater write privileges than the CPU side — worth highlighting for time-sync ownership.")
    box(s, 0.45, 2.3, 2.5, 1.2, "**GNR CPU**", fill=NAVY, size=18)
    container(s, 4.75, 1.8, 3.85, 2.2, "Common RTC device", line=I2C, fill=rgb("E6F4F3"), size=14)
    box(s, 4.95, 2.45, 1.6, 0.95, "**Primary**\nI2C port", fill=I2C, size=12)
    box(s, 6.8, 2.45, 1.6, 0.95, "**Secondary**\nI2C port", fill=I2C, size=12)
    box(s, 10.38, 2.3, 2.5, 1.2, "**BMC**", fill=BMC_C, size=18)
    bus(s, 2.95, 2.9, 4.95, 2.9, I2C, label="I2C · 400 kHz", lw=1.7)
    bus(s, 8.4, 2.9, 10.38, 2.9, I2C, label="I2C · 400 kHz", lw=1.7)
    tag(s, 3.0, 3.1, "lower write privilege", rgb("FFF4D6"), w=1.7, fg=DARK, size=9)
    tag(s, 8.64, 3.1, "higher write privilege", rgb("E3F4EC"), w=1.7, fg=DARK, size=9)
    cards = [("Why", "BHS can boot **without a PCH** → no PCH RTC → discrete I2C RTC"),
             ("Who", "**CPU** and **BMC** each get their own I2C interface to the same RTC"),
             ("Control", "**BMC (secondary)** port has greater write privileges than the CPU port")]
    for i, (h, t) in enumerate(cards):
        x = 0.45 + i * 4.2
        box(s, x, 4.45, 4.0, 0.42, h, fill=I2C, size=13, bold=True, shape=RECT)
        box(s, x, 4.87, 4.0, 1.1, t, fill=WHITE, fg=DARK, size=13, line=EDGE, shape=RECT)
    source(s, SRC_BHS)


def bhs_i3c(d):
    s = d.slide("BHS change ③: I3C_MNG — new CPU manageability interface",
                "MCTP access path when MCTP-over-PCIe is not available (early boot, crash)", SEC["bhs"],
                notes="I3C_MNG is new in BHS-AP. Normally the BMC can reach the CPU with MCTP over PCIe, but that "
                      "path does not exist in early boot or after a crash. I3C_MNG gives MCTP a path that works "
                      "then. Documented uses: replacing serial PECI, telemetry, and SPDM-based attestation / "
                      "PFR provisioning. This is the key 'SMBus-era to I3C-era' idea on BHS.")
    tag(s, 0.6, 1.4, "NEW in BHS-AP", I3C, w=1.6)
    chain = [("GNR CPU", NAVY), ("MCTP endpoint", MCTP), ("BMC", BMC_C), ("OpenBMC management stack", AGG_C)]
    for i, (t, c) in enumerate(chain):
        box(s, 0.6, 1.9 + i * 1.18, 3.3, 0.65, "**%s**" % t, fill=c, size=14)
    bus(s, 2.25, 2.55, 2.25, 3.08, I3C, head=True)
    lab(s, 2.4, 2.65, "I3C_MNG", I3C, w=1.4, size=12)
    bus(s, 2.25, 3.73, 2.25, 4.26, MCTP, head=True)
    lab(s, 2.4, 3.83, "MCTP messages", MCTP, w=1.7, size=12)
    bus(s, 2.25, 4.91, 2.25, 5.44, GREY, head=True, w=2.5)

    panel(s, 4.4, 1.4, 4.1, 4.95, "Which MCTP path?", NAVY)
    box(s, 4.65, 2.05, 3.6, 0.7, "**Runtime:** MCTP over PCIe", fill=LIGHT, fg=DARK, size=13, line=BLUE)
    lab(s, 4.65, 2.95, "Not available during:", RED, w=3.6, size=12)
    tag(s, 4.75, 3.35, "Early boot", RED, w=1.55, size=11)
    tag(s, 6.55, 3.35, "Crash / error", RED, w=1.55, size=11)
    bus(s, 6.45, 3.75, 6.45, 4.45, I3C, head=True)
    box(s, 4.65, 4.45, 3.6, 0.85, "**MCTP over I3C_MNG**\nstill reachable", fill=I3C, size=13)
    text(s, 4.65, 5.45, 3.6, 0.8, "I3C_MNG keeps the CPU manageable when PCIe is down", size=11, color=GREY,
         align=CENTER)

    cards = [("Serial PECI replacement", "CPU management access without the legacy PECI wire"),
             ("Telemetry", "CPU health, thermal and power data to the BMC"),
             ("SPDM attestation · PFR provisioning", "Platform security over MCTP")]
    for i, (h, t) in enumerate(cards):
        y = 1.4 + i * 1.68
        box(s, 8.85, y, 4.0, 0.45, h, fill=I3C, size=13, bold=True, shape=RECT)
        box(s, 8.85, y + 0.45, 4.0, 1.05, t, fill=WHITE, fg=DARK, size=13, line=EDGE, shape=RECT)
    source(s, SRC_BHS)


def avc_overview(d):
    s = d.slide("Avenue City: one BMC, many dedicated SMBus branches",
                "Debug, sensing, power and FPGA control each get their own bus", SEC["avc"],
                notes="AVC does not put everything on one giant I2C bus. The DC-SCM/BMC drives separate branches: "
                      "host debug (behind a mux), chassis sensors, temperature sensors, PMBUS1 for PSUs, PMBUS2 for "
                      "power telemetry and VRs (with its own mux), and FPGA debug/AVMM buses. Next three slides "
                      "zoom into each group.")
    box(s, 4.9, 1.35, 3.5, 0.7, "**DC-SCM / BMC**", fill=BMC_C, size=16)
    bus(s, 6.65, 2.05, 6.65, 2.5, DARK, w=3)
    centers = [0.45 + i * 2.08 + 0.975 for i in range(6)]
    bus(s, centers[0], 2.5, centers[-1], 2.5, DARK, w=3)
    cols = [
        ("SMB_HOST_DEBUG\nJ441", SMB, "MUX", "Host", "Debug"),
        ("SMB_CHASSIS_SENSOR\nJ417", SMB, None, "Chassis sensors", "Sensing"),
        ("SMB_TEMPSENSOR\nJ311", SMB, None, "Temperature sensors", "Sensing"),
        ("SMB_PMBUS1", PMB, None, "PSU", "Power"),
        ("SMB_PMBUS2\n+ VR branch", PMB, "MUX (VR)", "Power telemetry · VRs", "Power"),
        ("FPGA SMBus\nMain · Debug · AVMM", SMB, None, "Main FPGA ↔ Debug FPGA", "Control / debug"),
    ]
    for i, (name, c, mux, end, fn) in enumerate(cols):
        x, cx = 0.45 + i * 2.08, centers[i]
        bus(s, cx, 2.5, cx, 2.95, c)
        box(s, x, 2.95, 1.95, 0.85, "**%s**" % name, fill=c, size=11)
        if mux:
            bus(s, cx, 3.8, cx, 4.15, c)
            box(s, cx - 0.6, 4.15, 1.2, 0.45, mux, fill=GREY, size=11, bold=True)
            bus(s, cx, 4.6, cx, 5.05, c)
        else:
            bus(s, cx, 3.8, cx, 5.05, c)
        ep(s, x, 5.05, 1.95, 0.75, end, c, size=12)
        lab(s, x, 5.85, fn, GREY, w=1.95, align=CENTER, size=11, h=0.3)
    legend(s, items=[("SMBus", SMB), ("PMBus", PMB)])
    source(s, SRC_AVC + "  ·  listed nets are 3.3 V standby (STBY_LVC3)")


def avc_debug_sensor(d):
    s = d.slide("AVC: host-debug and sensor SMBus",
                "Host debug sits behind a mux; sensors have dedicated buses from DC-SCM", SEC["avc"],
                notes="Host debug: SMB_HOST_DEBUG on J441 is the host SMBus interface behind a mux. After BIOS POST "
                      "that interface is disconnected and access is through the MIPI60 SMBus. Sensors: chassis and "
                      "temperature sensors each have their own SMBus from the DC-SCM — easier isolation and debug.")
    panel(s, 0.45, 1.35, 6.0, 3.55, "Host-debug SMBus (J441)", SMB)
    box(s, 0.75, 1.95, 2.1, 0.6, "**BMC / debug**", fill=BMC_C, size=13)
    bus(s, 1.8, 2.55, 1.8, 2.95, SMB)
    box(s, 1.2, 2.95, 1.2, 0.5, "MUX", fill=GREY, size=12, bold=True)
    bus(s, 1.8, 3.45, 1.8, 3.95, SMB)
    lab(s, 1.95, 3.5, "① to POST", SMB, w=1.3, size=11)
    box(s, 0.75, 3.95, 2.1, 0.65, "**Host**", fill=NAVY, size=14)
    box(s, 4.0, 1.95, 2.2, 0.6, "**MIPI60** debug", fill=ORANGE, size=13)
    bus(s, 5.1, 2.55, 2.85, 4.27, SMB, dash=True)
    lab(s, 4.05, 3.35, "② after POST:\nMIPI60 SMBus", SMB, w=2.2, size=11, h=0.55)

    panel(s, 6.88, 1.35, 6.0, 3.55, "Sensor SMBus from DC-SCM", SMB)
    box(s, 8.83, 1.95, 2.1, 0.6, "**DC-SCM**", fill=BMC_C, size=14)
    bus(s, 9.4, 2.55, 8.35, 3.05, SMB)
    bus(s, 10.4, 2.55, 11.4, 3.05, SMB)
    box(s, 7.1, 3.05, 2.5, 0.5, "SMB_CHASSIS_SENSOR", fill=SMB, size=11, bold=True)
    box(s, 10.15, 3.05, 2.5, 0.5, "SMB_TEMPSENSOR", fill=SMB, size=11, bold=True)
    bus(s, 8.35, 3.55, 8.35, 3.95, SMB)
    bus(s, 11.4, 3.55, 11.4, 3.95, SMB)
    ep(s, 7.1, 3.95, 2.5, 0.65, "Chassis sensors", SMB, size=12)
    ep(s, 10.15, 3.95, 2.5, 0.65, "Temperature sensors", SMB, size=12)

    table(s, 0.45, 5.05, 12.43, [
        ["Net", "Voltage", "Conn.", "Function"],
        ["SMB_HOST_DEBUG_STBY_LVC3_SCL/SDA", "3.3 V", "J441", "Host SMBus behind MUX; after POST → MIPI60 SMBus"],
        ["SMB_CHASSIS_SENSOR_STBY_LVC3_SCL/SDA", "3.3 V", "J417", "Chassis sensor SMBus from DC-SCM"],
        ["SMB_TEMPSENSOR_STBY_LVC3_SCL/SDA", "3.3 V", "J311", "Temperature sensor SMBus from DC-SCM"],
    ], col_w=[4.5, 1.0, 1.0, 5.93], row_h=0.36, size=11, mono_cols=(0,))
    source(s, SRC_AVC, x=0.45, w=12.43)


def avc_pmbus(d):
    s = d.slide("AVC: PMBus power topology and the VR mux",
                "PMBus = power commands over SMBus wires; the VR bus can be handed to debug", SEC["avc"],
                notes="SMB_PMBUS1 is the PSU interface. SMB_PMBUS2 serves power telemetry and voltage regulators when "
                      "enabled. The VR branch goes through a mux: it connects either to BMC PMBUS2 or to the MIPI60 "
                      "debug PMBUS2. The mux select is controlled indirectly through the Debug FPGA. This explains "
                      "WHY the mux exists: so a debugger can own the VR bus without fighting the BMC.")
    panel(s, 0.45, 1.35, 6.0, 5.15, "BMC power buses", PMB)
    box(s, 2.3, 1.95, 2.4, 0.65, "**DC-SCM / BMC**", fill=BMC_C, size=14)
    bus(s, 2.9, 2.6, 1.7, 3.15, PMB)
    bus(s, 4.1, 2.6, 5.0, 3.15, PMB)
    box(s, 0.7, 3.15, 2.0, 0.55, "SMB_PMBUS1", fill=PMB, size=12, bold=True)
    box(s, 3.95, 3.15, 2.1, 0.55, "SMB_PMBUS2", fill=PMB, size=12, bold=True)
    bus(s, 1.7, 3.7, 1.7, 4.2, PMB)
    ep(s, 0.7, 4.2, 2.0, 0.65, "**PSU(s)**", PMB, size=13)
    bus(s, 4.5, 3.7, 3.85, 4.2, PMB)
    bus(s, 5.6, 3.7, 5.6, 4.2, PMB)
    ep(s, 2.95, 4.2, 1.8, 0.65, "Power telemetry", PMB, size=11)
    ep(s, 4.95, 4.2, 1.3, 0.65, "VR branch ▶", PMB, size=11, bold=True)
    bullets(s, 0.7, 5.1, 5.6, 1.4, ["**PMBUS1** — PSU SMBus interface",
                                    "**PMBUS2** — power telemetry + VRs (when enabled)"], size=12, gap=3, mark=PMB)

    panel(s, 6.88, 1.35, 6.0, 5.15, "VR path: BMC or debug owns the bus", PMB)
    ep(s, 7.1, 3.15, 1.6, 0.9, "**VRs**", PMB, size=14)
    bus(s, 8.7, 3.6, 9.55, 3.6, PMB)
    lab(s, 8.68, 3.2, "PMBUS2_VR", PMB, w=0.9, align=CENTER, size=9)
    box(s, 9.55, 3.1, 1.0, 1.0, "**MUX**", fill=GREY, size=13)
    bus(s, 10.55, 3.35, 11.0, 2.5, PMB)
    bus(s, 10.55, 3.85, 11.0, 4.7, PMB)
    box(s, 11.0, 2.15, 1.75, 0.7, "**BMC**\nPMBUS2", fill=BMC_C, size=12)
    box(s, 11.0, 4.35, 1.75, 0.7, "**MIPI60 debug**\nPMBUS2", fill=ORANGE, size=11)
    box(s, 9.3, 5.45, 1.5, 0.6, "**Debug FPGA**", fill=AGG_C, size=12)
    bus(s, 10.05, 5.45, 10.05, 4.1, DARK, head=True, dash=True, w=2)
    lab(s, 10.2, 4.75, "mux select\n(indirect)", DARK, w=1.2, size=10, h=0.5)
    source(s, SRC_AVC, x=0.45, w=12.43)


def avc_fpga(d):
    s = d.slide("AVC: SMBus for FPGA management and debug",
                "AVC's SMBus fabric also carries control-plane traffic, not just sensor reads", SEC["avc"],
                notes="Separate SMBus interfaces exist for the Platform Main FPGA debug, the Debug FPGA debug, and an "
                      "AVMM SMBus connecting Main and Debug FPGA. Tie-back to the previous slide: the Debug FPGA is "
                      "what (indirectly) drives the PMBUS2 VR mux select.")
    box(s, 5.15, 1.45, 3.0, 0.7, "**BMC / debug host**", fill=BMC_C, size=15)
    box(s, 1.2, 3.75, 3.3, 0.8, "**Platform Main FPGA**", fill=LIGHT, fg=DARK, size=15, line=NAVY, lw=1.5)
    box(s, 8.8, 3.75, 3.3, 0.8, "**Debug FPGA**", fill=LIGHT, fg=DARK, size=15, line=NAVY, lw=1.5)
    bus(s, 5.6, 2.15, 2.85, 3.75, SMB)
    bus(s, 7.7, 2.15, 10.45, 3.75, SMB)
    lab(s, 1.2, 2.45, "**Main FPGA debug SMBus**", SMB, w=3.0, align=RIGHT, size=13)
    lab(s, 9.0, 2.45, "**Debug FPGA debug SMBus**", SMB, w=3.2, size=13)
    bus(s, 4.5, 4.15, 8.8, 4.15, SMB, head=True, tail=True, label="AVMM SMBus", lw=2.4)
    ep(s, 8.8, 5.45, 3.3, 0.6, "PMBUS2 VR mux select (slide 12)", PMB, size=11, dash=True)
    bus(s, 10.45, 4.55, 10.45, 5.45, PMB, dash=True, head=True, w=2)
    note(s, 0.45, 5.3, 7.9, 1.1, "AVC's SMBus fabric covers **sensing**, **power**, **debug** and **FPGA control** — "
         "AVMM gives register-level access between the two FPGAs.", size=13)
    legend(s, items=[("SMBus", SMB), ("PMBus", PMB)])
    source(s, SRC_AVC)


def jc_topology(d):
    s = d.slide("OKS Johnson City: JC1 (1S) vs JC2 (2S / 4S)",
                "Same HPM design — the only structural difference is the aggregator board", SEC["jc"],
                notes="JC1 and JC2 use the same HPM design. JC1 (1S) connects the single DC-SCM directly to the HPM. "
                      "JC2 (2S/4S) inserts an aggregator board between the single DC-SCM and the HPMs; it supplies "
                      "the muxes, hubs and glue logic to create electrical paths from one BMC to every HPM.")
    panel(s, 0.45, 1.35, 4.6, 4.6, "JC1 · 1S", I3C)
    box(s, 1.15, 1.95, 3.2, 0.7, "**DC-SCM · BMC**", fill=BMC_C, size=14)
    for i, c in enumerate((I2C, SMB, I3C)):
        bus(s, 2.4 + i * 0.35, 2.65, 2.4 + i * 0.35, 4.0, c, w=3)
    lab(s, 3.35, 3.1, "I2C / SMBus / I3C\ndirect", DARK, w=1.6, size=10, h=0.5)
    container(s, 1.15, 4.0, 3.2, 1.65, "HPM", line=NAVY, size=14)
    box(s, 1.65, 4.6, 2.2, 0.7, "**CPU**", fill=NAVY, size=14)

    panel(s, 5.4, 1.35, 7.48, 4.6, "JC2 · 2S / 4S", I3C)
    box(s, 7.55, 1.95, 3.2, 0.7, "**DC-SCM · BMC**", fill=BMC_C, size=14)
    for i, c in enumerate((I2C, SMB, I3C)):
        bus(s, 8.8 + i * 0.35, 2.65, 8.8 + i * 0.35, 3.1, c, w=3)
    box(s, 5.75, 3.1, 6.8, 0.75, "**Aggregator board**  —  muxes · hubs · glue logic", fill=AGG_C, size=14)
    for i in range(4):
        x = 5.75 + i * 1.73
        bus(s, x + 0.72, 3.85, x + 0.72, 4.25, DARK, w=2.5)
        container(s, x, 4.25, 1.45, 1.4, "HPM%d" % i, line=NAVY, dash=i > 1, size=12)
        box(s, x + 0.2, 4.75, 1.05, 0.55, "CPU", fill=NAVY, size=12, bold=True)
    lab(s, 9.2, 5.62, "HPM2/3: 4S only", GREY, w=3.0, align=CENTER, size=10, h=0.28)
    note(s, 0.45, 6.05, 12.43, 0.48, "Key point: BMC count does **not** scale with sockets — the aggregator fans "
         "**one BMC** out to every HPM.", size=13)
    source(s, SRC_JC, x=0.45, w=12.43)


def build(d):
    for f in (bhs_rtc, bhs_i3c, avc_overview, avc_debug_sensor, avc_pmbus, avc_fpga, jc_topology):
        f(d)
