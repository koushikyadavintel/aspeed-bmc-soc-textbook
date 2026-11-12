"""Part 6: Yocto layers, board porting, principles, debugging, takeaways."""
from deck_helpers import *

SEC = "Build, port, debug"


def build(d):
    # 39. Yocto layers
    s = d.slide("How an image is built: Yocto layers", "Generic at the bottom, your board at the top", SEC,
                "OpenBMC images are built with Yocto. Layers stack from generic to specific. Poky and "
                "OpenEmbedded give a generic Linux. meta-phosphor adds the common OpenBMC daemons and policies. "
                "The SoC layer adds U-Boot, kernel and flash layout for ASPEED or Nuvoton. The machine layer on "
                "top contains everything specific to your board. Higher layers override lower ones with bbappend "
                "files, so you customize without forking upstream.")
    layers = [("meta-<vendor>/meta-<machine>", "Your board: device tree, entity-manager JSON, daemon choices, fan config", ORANGE),
              ("meta-aspeed / meta-nuvoton", "SoC: U-Boot, kernel config, flash layout", TEAL),
              ("meta-phosphor", "Common OpenBMC daemons, systemd policies, image classes", PURPLE),
              ("poky / openembedded-core", "Generic Linux: toolchain, libc, systemd, busybox", NAVY)]
    for i, (t, sub, c) in enumerate(layers):
        y = 1.45 + i * 1.05
        box(s, 0.5, y, 4.2, 0.85, t, fill=c, size=14, bold=True, font=MONO)
        box(s, 4.8, y, 5.0, 0.85, sub, fill=LIGHT, fg=DARK, size=13, align=LEFT)
    arrow(s, 10.2, 5.5, 10.2, 1.5, color=ORANGE, width=3)
    text(s, 10.45, 2.6, 2.4, 1.6, "More specific\n→ overrides\nbelow via\n.bbappend", size=14)
    flow(s, 0.5, 5.85, ["bitbake obmc-phosphor-image", "image-bmc / .mtd", "Flash to BMC"], 3.8, 0.8, gap=0.45,
         colors=[BLUE, GREEN, RED], size=14)

    # 40. Porting a board
    s = d.slide("Porting OpenBMC to a new board", "What you edit, and in what order", SEC,
                "A board port is mostly configuration. Start with the device tree so the kernel sees the "
                "hardware, and check with the serial console and sysfs. Then pick daemons in the machine "
                "configuration. Then describe sensors and FRUs in entity-manager JSON, power sequencing in "
                "x86-power-control JSON or systemd units, and fan zones in pid-control JSON. Only custom OEM "
                "behaviour needs new code.")
    steps = [("1", "Device tree (.dts)", "Buses, chips, GPIO line names", "dmesg, /sys/class/hwmon"),
             ("2", "Machine .conf / image", "Which daemons, flash layout", "busctl list"),
             ("3", "entity-manager JSON", "Sensors, FRUs, PSUs, fans", "busctl tree ...EntityManager"),
             ("4", "Power sequencing", "GPIO JSON or obmc-* units", "Power on/off via Redfish"),
             ("5", "Fan control JSON", "Zones, setpoints, PID gains", "Fan RPM under load"),
             ("6", "OEM code (only if needed)", "ipmid providers, bmcweb options", "Your test suite")]
    box(s, 0.5, 1.4, 0.6, 0.5, "#", fill=NAVY, size=14, bold=True, shape=RECT)
    for x, w, t in [(1.1, 3.9, "Edit"), (5.0, 4.0, "Defines"), (9.0, 3.8, "Verify with")]:
        box(s, x, 1.4, w, 0.5, t, fill=NAVY, size=14, bold=True, shape=RECT)
    cols = [TEAL, GREEN, PURPLE, BLUE, SKY, ORANGE]
    for i, (n, e, df, v) in enumerate(steps):
        y = 2.0 + i * 0.78
        box(s, 0.5, y, 0.6, 0.68, n, fill=cols[i], size=16, bold=True, shape=RECT)
        box(s, 1.1, y, 3.9, 0.68, e, fill=LIGHT, fg=DARK, size=14, bold=True, shape=RECT, line=WHITE)
        box(s, 5.0, y, 4.0, 0.68, df, fill=LIGHT, fg=DARK, size=13, shape=RECT, line=WHITE)
        box(s, 9.0, y, 3.8, 0.68, v, fill=MINT, fg=DARK, size=12, shape=RECT, line=WHITE, font=MONO)
    text(s, 0.5, 6.7, 12.3, 0.35, "Rule: get each layer right before moving up — the same order as the boot.",
         size=13, color=GREY, align=CENTER)

    # 41. Principles
    s = d.slide("Eight design principles", "The 'why' behind everything we have seen", SEC,
                "If you remember these eight, you can predict how any new OpenBMC feature is built. D-Bus is the "
                "single source of truth; daemons are small; interfaces are contracts; discovery goes through "
                "the mapper; behaviour is configuration-driven; hardware is accessed only through the kernel; "
                "everything is asynchronous and event-driven; and the front ends are translators.")
    ps = [("1", "D-Bus is the single source of truth", PURPLE), ("2", "Small daemons, one job each", ORANGE),
          ("3", "Interfaces are the contract", BLUE), ("4", "Discover via the mapper, never hard-code", rgb("8E5BB5")),
          ("5", "Configuration over code (DTS, JSON)", GREEN), ("6", "Hardware only through kernel drivers", TEAL),
          ("7", "Async and event-driven (signals)", SKY), ("8", "Front ends are translators", RED)]
    for i, (n, t, c) in enumerate(ps):
        x, y = 0.5 + (i % 2) * 6.25, 1.45 + (i // 2) * 1.32
        box(s, x, y, 0.9, 1.1, n, fill=c, size=26, bold=True)
        box(s, x + 1.0, y, 5.0, 1.1, t, fill=LIGHT, fg=DARK, size=17, align=LEFT)

    # 42. Debug funnel
    s = d.slide("Debugging: follow the data down", "Find the first layer where the data is missing or wrong", SEC,
                "This is the single most useful debugging method. Start at the top: does Redfish show it? Then "
                "D-Bus: does the object exist and is its value right? Then the configuration: did entity-manager "
                "publish it? Then the daemon: is it running and what does its journal say? Then the kernel: is "
                "there a hwmon node, did the driver probe? The first layer where the data disappears is where "
                "the bug lives.")
    levels = [("Redfish / IPMI", "Missing here but OK on D-Bus → bmcweb / association bug", BLUE, 12.3),
              ("D-Bus object", "Config exists but no sensor → daemon failed: read journal", PURPLE, 11.1),
              ("Configuration", "No Configuration object → Probe did not match / JSON error", GREEN, 9.9),
              ("Daemon (systemd)", "Unit failed or crash-looping → systemctl status", ORANGE, 8.7),
              ("Kernel / driver", "No hwmon node → DTS address, driver, wiring", TEAL, 7.5)]
    for i, (t, sub, c, w) in enumerate(levels):
        y = 1.4 + i * 1.0
        x = 0.5 + (12.3 - w) / 2
        box(s, x, y, w, 0.85, fill=c, shape=RECT)
        text(s, x + 0.15, y, 2.6, 0.85, t, size=16, bold=True, color=WHITE, anchor=MIDDLE)
        text(s, x + 2.75, y, w - 2.9, 0.85, sub, size=13, color=WHITE, anchor=MIDDLE)
    text(s, 0.5, 6.45, 12.3, 0.45, "Top to bottom: stop at the first layer where the data is wrong.",
         size=14, color=GREY, align=CENTER, bold=True)

    # 43. Commands
    s = d.slide("Debug command cheat sheet", "Read-only commands to run on the BMC shell", SEC,
                "These are safe, read-only commands. busctl tree and introspect show what a service publishes. "
                "busctl monitor shows live signals. journalctl with -u filters one daemon's log. Service names "
                "differ between platforms, so start with busctl list to see what exists.")
    groups = [("D-Bus", PURPLE, "busctl list\nbusctl tree <service>\nbusctl introspect <svc> <path>\n"
               "busctl get-property <svc> <path> <iface> <prop>\nbusctl monitor <service>"),
              ("systemd & logs", ORANGE, "systemctl --failed\nsystemctl status <unit>\njournalctl -u <unit> -b\n"
               "journalctl -f"),
              ("Kernel & hardware", TEAL, "dmesg | grep -i i2c\nls /sys/class/hwmon/*/name\n"
               "cat /sys/class/hwmon/hwmon*/temp1_input\ngpioinfo"),
              ("From outside", BLUE, "curl -k -u <user> \\\n https://<bmc>/redfish/v1/...\n"
               "ipmitool -I lanplus -H <bmc> \\\n -U <user> sensor list")]
    for i, (t, c, cmd) in enumerate(groups):
        x, y = 0.5 + (i % 2) * 6.25, 1.4 + (i // 2) * 2.75
        box(s, x, y, 6.05, 0.5, t, fill=c, size=15, bold=True, shape=RECT)
        code(s, x, y + 0.5, 6.05, 2.0, cmd, size=13)

    # 44. Takeaways
    s = d.slide("Key takeaways", "Five things to remember", SEC,
                "Summarize. The BMC is an independent computer. OpenBMC is layers, and D-Bus is the middle layer "
                "that holds everything together. Boards are described with device tree and JSON. Every external "
                "interface is a translator onto D-Bus. And debugging means following the data down the layers.")
    tk = [("Independent computer", "The BMC manages the host on standby power — even when the host is dead.", TEAL),
          ("Layers", "Flash → boot → kernel → systemd → D-Bus → daemons → Redfish / IPMI.", GREEN),
          ("D-Bus is the heart", "Daemons publish objects; the mapper finds them; signals drive reactions.", PURPLE),
          ("Config over code", "Device tree + entity-manager JSON describe the board.", ORANGE),
          ("Debug top-down", "Follow the data down; the first wrong layer holds the bug.", BLUE)]
    for i, (t, sub, c) in enumerate(tk):
        y = 1.4 + i * 1.06
        box(s, 0.5, y, 0.85, 0.85, str(i + 1), fill=c, size=24, bold=True, shape=OVAL)
        text(s, 1.6, y, 3.6, 0.85, t, size=19, bold=True, color=c, anchor=MIDDLE)
        text(s, 5.2, y, 7.6, 0.85, sub, size=16, anchor=MIDDLE)

    # 45. Q&A
    s = d.raw("Thank the audience and open for questions. Point people to the upstream repositories for deeper "
              "reading: the docs repository has architecture notes, and phosphor-dbus-interfaces is the best "
              "reference for what each D-Bus property means.")
    box(s, 0, 0, 13.333, 7.5, fill=NAVY, shape=RECT)
    text(s, 0.8, 1.0, 11.7, 1.0, "Questions?", size=54, color=WHITE, bold=True)
    box(s, 0.8, 2.2, 11.7, 0.05, fill=SKY, shape=RECT)
    text(s, 0.8, 2.5, 11.7, 0.5, "Where to read next (github.com/openbmc):", size=20, color=rgb("BFD7EE"), bold=True)
    refs = [("docs", "Architecture and design documents"), ("phosphor-dbus-interfaces", "Meaning of every D-Bus interface"),
            ("entity-manager · dbus-sensors", "Board config and sensors"), ("bmcweb", "Redfish implementation"),
            ("openbmc (meta-layers)", "Yocto layers, machine configs")]
    for i, (r, d2) in enumerate(refs):
        y = 3.2 + i * 0.7
        box(s, 0.8, y, 4.6, 0.55, r, fill=BLUE, size=15, font=MONO)
        text(s, 5.6, y, 7.0, 0.55, d2, size=17, color=WHITE, anchor=MIDDLE)
