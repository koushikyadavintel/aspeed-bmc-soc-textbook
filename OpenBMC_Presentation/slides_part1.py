"""Part 1: opening, what a BMC is, OpenBMC overview, hardware context."""
from deck_helpers import *

SEC = "Introduction"


def build(d):
    # 1. Title
    s = d.raw("Welcome everyone. Today's goal: understand how OpenBMC is put together, from the "
              "wires on the motherboard up to the Redfish API, so that when something breaks you "
              "know which layer to look at.")
    box(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=RECT)
    box(s, 0, 4.55, 13.333, 0.06, fill=SKY, shape=RECT)
    text(s, 0.8, 1.6, 11.7, 1.2, "OpenBMC Architecture", size=54, color=WHITE, bold=True)
    text(s, 0.8, 2.75, 11.7, 0.8, "From hardware wires to Redfish: how the BMC software stack works",
         size=24, color=rgb("BFD7EE"))
    flow(s, 0.8, 3.7, ["Hardware", "Kernel", "systemd", "D-Bus", "Daemons", "Redfish / IPMI"],
         1.75, 0.6, gap=0.3, colors=[TEAL, GREEN, PURPLE, ORANGE, BLUE, SKY], size=13)
    text(s, 0.8, 4.9, 11.7, 0.5, "Team knowledge session", size=18, color=WHITE)
    text(s, 0.8, 5.4, 11.7, 0.5, "Presenter:  ____________        Date:  ____________", size=16,
         color=rgb("BFD7EE"))

    # 2. Agenda
    s = d.slide("Agenda", "Seven parts, bottom-up: each layer builds on the one below", SEC,
                "Walk through the agenda. We go bottom-up on purpose: hardware first, then boot, then "
                "the D-Bus backbone, then the daemons, then the external APIs. We finish with real "
                "end-to-end flows, how a board port is built, and how to debug.")
    parts = [("1", "What is a BMC and OpenBMC", "Problem, history, the big picture", TEAL),
             ("2", "Hardware & boot", "SoC wiring, flash, U-Boot, device tree, kernel", GREEN),
             ("3", "systemd & D-Bus", "Service lifecycle, object model, ObjectMapper", PURPLE),
             ("4", "Function daemons", "Inventory, sensors, fans, power, logs, updates", ORANGE),
             ("5", "External interfaces", "bmcweb / Redfish, IPMI, KVM, console", BLUE),
             ("6", "End-to-end flows", "Read a sensor, power on, raise an alert", RED),
             ("7", "Build, port, debug", "Yocto layers, board bring-up, troubleshooting", NAVY)]
    for i, (n, t, sub, c) in enumerate(parts):
        y = 1.4 + i * 0.78
        box(s, 0.9, y, 0.62, 0.62, n, fill=c, size=20, bold=True, shape=OVAL)
        box(s, 1.7, y, 10.7, 0.62, fill=LIGHT, shape=ROUND)
        text(s, 1.85, y + 0.04, 4.4, 0.55, t, size=18, bold=True, anchor=MIDDLE)
        text(s, 6.2, y + 0.04, 6.1, 0.55, sub, size=15, color=GREY, anchor=MIDDLE)

    # 3. What is a BMC
    s = d.slide("What is a BMC?", "A small, independent computer that manages the big computer", SEC,
                "A server has two computers inside. The host runs customer workloads. The BMC is a "
                "separate ARM system-on-chip with its own memory, flash, network port and Linux. It is "
                "powered from standby power, so it is alive whenever the server is plugged in, even "
                "when the host is off or its OS has crashed. That independence is the whole point.")
    box(s, 0.6, 1.45, 5.3, 3.9, fill=PALE, line=BLUE, shape=ROUND)
    text(s, 0.6, 1.55, 5.3, 0.5, "HOST", size=22, bold=True, color=BLUE, align=CENTER)
    for i, t in enumerate(["x86 / ARM server CPUs", "Large DRAM, PCIe devices", "BIOS / UEFI firmware",
                           "Customer OS + workloads"]):
        box(s, 1.0, 2.15 + i * 0.75, 4.5, 0.6, t, fill=WHITE, fg=DARK, line=SKY, size=15)
    box(s, 7.4, 1.45, 5.3, 3.9, fill=MINT, line=GREEN, shape=ROUND)
    text(s, 7.4, 1.55, 5.3, 0.5, "BMC", size=22, bold=True, color=GREEN, align=CENTER)
    for i, t in enumerate(["ARM SoC (e.g. ASPEED, Nuvoton)", "Own DRAM + SPI flash / eMMC",
                           "Own management NIC", "Embedded Linux = OpenBMC"]):
        box(s, 7.8, 2.15 + i * 0.75, 4.5, 0.6, t, fill=WHITE, fg=DARK, line=GREEN, size=15)
    arrow(s, 7.35, 2.7, 5.95, 2.7, color=GREEN, width=3, label="controls & observes", lsize=13)
    arrow(s, 5.95, 4.1, 7.35, 4.1, color=BLUE, width=3, label="in-band messages", lsize=13)
    note(s, 0.6, 5.6, 12.1, 1.2,
         "**Key idea:** the BMC runs on **standby power**. It works when the host is powered off, hung, "
         "or has no OS installed — that is exactly when operators need it most.", size=16)

    # 4. What does it do
    s = d.slide("What does a BMC do?", "Six jobs every data-center operator relies on", SEC,
                "These six jobs are the requirements. Every OpenBMC daemon we will see later exists to "
                "serve one of these. Monitoring and power control are the core. Remote console means "
                "nobody walks to the data center. Firmware update and logs keep the fleet healthy.")
    tiles = [("Monitor", "Temperatures, voltages, currents, fan speeds, power draw", TEAL),
             ("Control power", "Power on/off, reset, power-cycle the host remotely", GREEN),
             ("Cool", "Drive fans from thermal readings (closed-loop control)", SKY),
             ("Inventory", "Which CPUs, DIMMs, PSUs, drives are present; serial numbers", PURPLE),
             ("Remote access", "Serial console, graphical KVM, virtual media (ISO mount)", BLUE),
             ("Update & log", "Firmware updates, event logs, alerts to management tools", ORANGE)]
    for i, (t, sub, c) in enumerate(tiles):
        x, y = 0.6 + (i % 3) * 4.1, 1.45 + (i // 3) * 2.75
        box(s, x, y, 3.85, 2.5, fill=LIGHT, shape=ROUND)
        box(s, x, y, 3.85, 0.75, t, fill=c, size=20, bold=True, shape=RECT)
        text(s, x + 0.2, y + 0.9, 3.45, 1.5, sub, size=16, align=CENTER, anchor=MIDDLE)

    # 5. What is OpenBMC
    s = d.slide("What is OpenBMC?", "An open-source Linux distribution and framework for BMCs", SEC,
                "OpenBMC is not one program. It is a Yocto-built Linux distribution plus a large set "
                "of small daemons that talk over D-Bus, with Redfish and IPMI on top. It started at a "
                "Facebook hackathon in 2014 and has been a Linux Foundation project since 2018, with "
                "contributions from many server and silicon vendors. Compare it with traditional "
                "closed BMC firmware on the right.")
    box(s, 3.0, 3.2, 2.6, 1.2, "OpenBMC", fill=NAVY, size=24, bold=True)
    spokes = [("Linux distro built with Yocto", 0.4, 1.45), ("Linux kernel + U-Boot", 4.65, 1.45),
              ("Many small single-purpose daemons", 0.4, 5.45), ("D-Bus object model as the API", 4.65, 5.45),
              ("Redfish + IPMI front ends", 0.4, 3.45)]
    for t, x, y in spokes:
        box(s, x, y, 2.4 if x < 1 and y == 3.45 else 3.5, 0.75, t, fill=PALE, fg=DARK, line=BLUE, size=14)
    arrow(s, 2.15, 2.2, 3.4, 3.2, head=False)
    arrow(s, 6.4, 2.2, 5.2, 3.2, head=False)
    arrow(s, 2.15, 5.45, 3.4, 4.4, head=False)
    arrow(s, 6.4, 5.45, 5.2, 4.4, head=False)
    arrow(s, 2.8, 3.8, 3.0, 3.8, head=False)
    table(s, 8.4, 1.45, 4.5, [["Traditional BMC", "OpenBMC"],
                              ["Closed vendor code", "Open source, upstream"],
                              ["One monolith", "Small daemons"],
                              ["Hard to customize", "Config-driven per board"],
                              ["Vendor fixes only", "Community + your fixes"],
                              ["Opaque internals", "Inspect with busctl, journalctl"]],
          col_w=[2.25, 2.25], row_h=0.62, size=13)
    text(s, 8.4, 5.4, 4.5, 1.3, "2014: started at a Facebook hackathon\n2018: Linux Foundation project\n"
         "Today: used across many server vendors", size=13, color=GREY)

    # 6. Big picture
    s = d.slide("The big picture: seven layers", "Keep this slide in mind — every later slide zooms into one layer",
                SEC, "This is the map for the rest of the talk. Requests from users come in at the top. "
                "Hardware sits at the bottom. The D-Bus layer in the middle is the contract every "
                "daemon agrees on. If you remember one picture from today, make it this one.")
    layers = [("7  External interfaces:  bmcweb (Redfish, Web UI)  ·  ipmid / netipmid  ·  SSH", BLUE),
              ("6  Function daemons:  sensors · inventory · power state · fans · logging · update", ORANGE),
              ("5  D-Bus system bus + ObjectMapper   (contract = phosphor-dbus-interfaces)", PURPLE),
              ("4  systemd:  starts, orders and restarts every daemon", rgb("8E5BB5")),
              ("3  Linux kernel + device tree:  drivers for I2C, GPIO, hwmon, PECI, KCS, MCTP", GREEN),
              ("2  Boot:  SoC boot ROM → U-Boot → FIT image (kernel + device tree)", TEAL),
              ("1  Flash:  u-boot · env · kernel · read-only rootfs · writable overlay", NAVY)]
    stack(s, 0.6, 1.4, 8.6, layers, h=0.66, gap=0.1, size=14)
    arrow(s, 9.7, 1.5, 9.7, 6.6, color=BLUE, width=3)
    text(s, 9.95, 1.5, 2.7, 1.2, "Requests flow down\n(\"read sensor\",\n\"power on\")", size=14)
    arrow(s, 12.85, 6.6, 12.85, 1.5, color=GREEN, width=3)
    text(s, 9.95, 5.4, 2.8, 1.2, "Data and events\nflow up", size=14, align=RIGHT)
    note(s, 9.95, 3.2, 2.7, 1.6, "**Layer 5 is the heart:** daemons never call each other directly.",
         size=14, fill=LILAC, accent=PURPLE)

    # 7. Hardware context
    s = d.slide("Hardware context: what the BMC is wired to", "Software's job: turn all these wires into one clean API",
                SEC, "Go around the hub. I2C/I3C reaches sensors, voltage regulators, PSUs and FRU EEPROMs. "
                "GPIOs press the power button and read power-good. PWM and tach drive fans. PECI or APML "
                "reads CPU temperatures. eSPI/LPC carries KCS for in-band IPMI. PCIe carries the VGA "
                "display for KVM and MCTP. USB gadget fakes a keyboard and a CD drive. UART is the host "
                "serial console. NC-SI or a dedicated NIC is the management network.")
    box(s, 5.0, 3.05, 3.3, 1.5, "BMC SoC\nARM cores · Linux", fill=NAVY, size=18, bold=True)
    spokes = [("SPI / eMMC\nBMC flash", 0.5, 1.4, TEAL), ("I2C / I3C\nsensors, VRs, PSUs, FRUs", 4.85, 1.4, GREEN),
              ("GPIO\npower btn, reset, PGOOD", 9.2, 1.4, ORANGE), ("PWM / Tach\nfans", 0.5, 3.3, SKY),
              ("PECI / APML\nCPU temps & errors", 9.2, 3.3, RED), ("eSPI / LPC (KCS)\nin-band IPMI", 0.5, 5.25, PURPLE),
              ("PCIe · USB · UART\nVGA, MCTP, KVM, console", 4.85, 5.25, BLUE),
              ("RGMII / NC-SI\nmanagement network", 9.2, 5.25, rgb("2E4057"))]
    for t, x, y, c in spokes:
        box(s, x, y, 3.6, 1.05, t, fill=c, size=14)
        bx, by = x + 1.8, y + 0.52
        tx = 5.0 if bx < 5 else (8.3 if bx > 8.3 else bx)
        ty = 3.05 if by < 3 else (4.55 if by > 4.6 else by)
        sx = x + 3.6 if bx < 5 else (x if bx > 8.3 else bx)
        sy = y + 1.05 if by < 3 else (y if by > 4.6 else by)
        arrow(s, sx, sy, tx, ty, color=c, width=2.5, head=False)

    # 8. Interface cheat sheet
    s = d.slide("Hardware link cheat sheet", "Which wire serves which management feature", SEC,
                "Use this as a reference table. The middle column is what the kernel exposes, which "
                "matters because OpenBMC daemons only ever talk to the kernel interface, never raw "
                "registers. The right column links each wire to the feature users see.")
    table(s, 0.5, 1.4, 12.3, [
        ["Link", "Talks to", "Kernel exposes", "Used for"],
        ["I2C / I3C", "Temp sensors, VRs, PSUs, FRU EEPROMs", "/dev/i2c-N, hwmon sysfs", "Sensors, inventory"],
        ["GPIO", "Power button, reset, power-good, presence", "/dev/gpiochipN (libgpiod)", "Power control, presence"],
        ["PWM / Tach", "Fans", "hwmon pwmN / fanN_input", "Fan control"],
        ["PECI / APML", "Host CPU", "/dev/peci-N, hwmon", "CPU & DIMM temps, errors"],
        ["KCS / BT over eSPI/LPC", "BIOS / host OS", "/dev/ipmi-kcsN", "In-band IPMI"],
        ["PCIe", "Host (VGA), devices (MCTP)", "Video engine, AF_MCTP sockets", "KVM, PLDM"],
        ["USB gadget", "Host USB port", "configfs gadget", "Virtual keyboard/mouse, ISO"],
        ["UART", "Host serial port", "/dev/ttySN", "Serial over LAN (SOL)"],
        ["NC-SI / NIC", "Network", "ethN", "Redfish, Web UI, IPMI LAN"],
    ], col_w=[2.2, 3.9, 3.2, 3.0], row_h=0.52, size=14, mono_cols=(2,))
