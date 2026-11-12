"""Part 2: flash layout, boot chain, device tree, kernel, systemd."""
from deck_helpers import *

SEC = "Hardware & boot"


def build(d):
    # 9. Flash layout
    s = d.slide("BMC flash layout", "What is stored where (typical 32 MB SPI-NOR static layout — example)", SEC,
                "This is the classic static layout on a 32 MB SPI flash. U-Boot and its environment at the "
                "start, then the FIT image with kernel and device tree, then a big read-only squashfs root "
                "filesystem, and a small writable partition at the end. Sizes vary per platform; newer "
                "designs use UBI or eMMC and often two image copies for A/B updates.")
    segs = [("u-boot", 0.55, NAVY), ("env", 0.35, rgb("2E4057")), ("kernel (FIT)", 1.9, TEAL),
            ("rofs  —  read-only root filesystem (squashfs)", 6.9, GREEN), ("rwfs", 1.4, ORANGE)]
    x = 0.6
    for t, w, c in segs:
        box(s, x, 1.6, w, 1.0, t, fill=c, size=13 if w > 0.5 else 10, bold=True, shape=RECT, line=WHITE)
        x += w
    for t, xx in [("0", 0.6), ("384 KB", 1.15), ("512 KB", 1.5), ("4.75 MB", 3.4), ("28 MB", 10.3),
                  ("32 MB", 11.7)]:
        text(s, xx - 0.5, 2.62, 1.0, 0.35, t, size=10, color=GREY, align=CENTER)
    rows = [("u-boot", "Bootloader: brings up DRAM, loads the kernel", NAVY),
            ("env", "U-Boot variables (boot command, MAC address, boot side)", rgb("2E4057")),
            ("kernel", "FIT image = Linux kernel + device tree blob (+ optional initramfs)", TEAL),
            ("rofs", "All programs and default configs. Replaced as a whole on update", GREEN),
            ("rwfs", "Persistent changes: /etc settings, /var data. Wiped on factory reset", ORANGE)]
    for i, (k, v, c) in enumerate(rows):
        y = 3.25 + i * 0.66
        box(s, 0.6, y, 1.5, 0.55, k, fill=c, size=14, bold=True)
        text(s, 2.25, y, 10.4, 0.55, v, size=16, anchor=MIDDLE)

    # 10. Overlay filesystem
    s = d.slide("Read-only root + writable overlay", "How updates stay atomic while settings survive", SEC,
                "Linux overlayfs merges two layers. Reads come from the upper writable layer if the file "
                "was changed, otherwise from the read-only squashfs. A firmware update swaps the lower "
                "layer in one piece, so you never get a half-updated system. A factory reset simply "
                "clears the upper layer. When debugging 'my config change disappeared', check which "
                "layer the file lives in.")
    box(s, 0.8, 1.5, 6.6, 1.0, "What processes see:  /  (merged view)", fill=BLUE, size=18, bold=True)
    box(s, 0.8, 3.0, 6.6, 1.0, "Upper:  rwfs  —  writable  (your changed /etc, /var)", fill=ORANGE, size=16)
    box(s, 0.8, 4.5, 6.6, 1.0, "Lower:  rofs  —  read-only squashfs  (from the image)", fill=GREEN, size=16)
    arrow(s, 4.1, 3.0, 4.1, 2.5, color=DARK, width=2.5)
    arrow(s, 2.0, 4.5, 2.0, 2.5, color=DARK, width=2.5, dash=True)
    text(s, 0.8, 5.65, 6.6, 0.9, "File changed?  → served from upper.\nUnchanged?  → served from lower.",
         size=15, color=GREY)
    for i, (t, sub, c) in enumerate([
            ("Firmware update", "Replace the lower layer as a whole. Atomic: old or new, never half.", GREEN),
            ("Settings persist", "Upper layer survives reboots and updates.", ORANGE),
            ("Factory reset", "Erase the upper layer → back to image defaults.", RED)]):
        y = 1.5 + i * 1.65
        box(s, 8.0, y, 4.8, 1.4, fill=LIGHT, shape=ROUND)
        box(s, 8.0, y, 0.12, 1.4, fill=c, shape=RECT)
        text(s, 8.3, y + 0.1, 4.4, 0.45, t, size=18, bold=True)
        text(s, 8.3, y + 0.55, 4.4, 0.8, sub, size=14, color=GREY)

    # 11. Boot chain
    s = d.slide("Boot chain: power to login prompt", "Each stage verifies and hands off to the next", SEC,
                "When standby power arrives, the SoC boot ROM runs first. On secure-boot platforms it "
                "verifies U-Boot's signature. U-Boot initializes DRAM and loads the FIT image. The kernel "
                "starts, parses the device tree, binds drivers, mounts the root filesystem with the overlay, "
                "and starts systemd as PID 1. systemd then brings the BMC to the 'Ready' state.")
    flow(s, 0.5, 1.55, ["Standby\npower on", "SoC boot ROM", "U-Boot", "Linux kernel", "systemd\n(PID 1)",
                        "BMC Ready"], 1.85, 1.1, gap=0.32, colors=[GREY, NAVY, TEAL, GREEN, PURPLE, BLUE], size=15)
    details = ["BMC powers up from standby rail; host may stay off",
               "Fixed code in silicon; finds boot media; may verify signature (secure boot)",
               "Init DRAM, clocks; reads env; loads FIT image (kernel + DTB)",
               "Parses device tree, binds drivers, mounts rofs + overlay",
               "Starts all units in dependency order; obmc targets",
               "State.BMC = Ready; Redfish and IPMI reachable"]
    for i, t in enumerate(details):
        x = 0.5 + i * 2.17
        box(s, x, 2.85, 1.85, 2.3, t, fill=LIGHT, fg=DARK, size=12, shape=RECT, anchor=TOP)
    note(s, 0.5, 5.5, 12.3, 1.2, "**Debug tip:** the BMC serial console shows every stage. If you see "
         "U-Boot output but no kernel messages, suspect the FIT image or device tree; if the kernel boots "
         "but services fail, look at **systemctl --failed** and **journalctl -b**.", size=15)

    # 12. Device tree
    s = d.slide("Device tree: describing the board to the kernel", "Same kernel binary, different boards — the DTB tells them apart",
                SEC, "The kernel cannot discover what is soldered on an I2C bus. The device tree source describes "
                "it: which controllers are enabled, which chips sit at which addresses, and names for GPIO "
                "lines. It is compiled into a DTB, packed in the FIT image, and at boot the kernel matches the "
                "'compatible' strings to drivers. GPIO line names are important: OpenBMC daemons look up "
                "lines by name such as 'power-button', not by number.")
    code(s, 0.5, 1.45, 5.6, 4.0,
         "&i2c6 {\n    status = \"okay\";\n\n    temp@48 {\n        compatible = \"ti,tmp75\";\n"
         "        reg = <0x48>;\n    };\n};\n\n&gpio0 {\n    gpio-line-names =\n        \"power-button\",\n"
         "        \"reset-button\",\n        \"power-good\", ...;\n};", size=14)
    text(s, 0.5, 5.5, 5.6, 0.4, "board.dts (simplified example)", size=12, color=GREY, align=CENTER)
    vflow(s, 7.0, 1.45, ["board.dts  (source, in kernel tree)", "dtc compiler → board.dtb",
                         "Packed in FIT image with kernel", "Kernel matches \"compatible\" → driver",
                         "Driver creates /sys/class/hwmon/hwmonN"],
          5.6, 0.68, gap=0.28, colors=[NAVY, TEAL, GREEN, PURPLE, BLUE], size=15)
    note(s, 7.0, 6.15, 5.6, 0.75, "Wrong address or bus in the DTS = sensor silently missing.", size=14)

    # 13. Kernel interfaces
    s = d.slide("Kernel: the only path to hardware", "Daemons use standard Linux interfaces, never raw registers", SEC,
                "Follow one row left to right. A TMP75 chip is handled by the lm75 driver, which exposes a "
                "sysfs file; the hwmontempsensor daemon reads that file. Because every daemon uses standard "
                "interfaces, supporting a new chip usually means enabling a kernel driver and adding "
                "configuration — not writing a new daemon.")
    cols = [("Hardware", TEAL), ("Kernel driver", GREEN), ("Interface", PURPLE), ("Daemon", ORANGE)]
    for i, (t, c) in enumerate(cols):
        box(s, 0.5 + i * 3.15, 1.4, 2.85, 0.55, t, fill=c, size=16, bold=True)
    rows = [("TMP75 temp chip", "lm75 (hwmon)", "/sys/class/hwmon/.../temp1_input", "hwmontempsensor"),
            ("Fan + PWM", "aspeed-pwm-tacho", "hwmon pwm1, fan1_input", "fansensor, swampd"),
            ("Power button GPIO", "gpio-aspeed", "/dev/gpiochip0 (by name)", "x86-power-control"),
            ("Host CPU", "peci-cpu / peci-cputemp", "/dev/peci-0, hwmon", "intelcpusensor"),
            ("KCS channel", "kcs-bmc", "/dev/ipmi-kcs3", "kcsbridged → ipmid")]
    for r, row in enumerate(rows):
        y = 2.15 + r * 0.9
        for i, t in enumerate(row):
            x = 0.5 + i * 3.15
            box(s, x, y, 2.85, 0.7, t, fill=LIGHT, fg=DARK, size=13, font=MONO if i == 2 else FONT, shape=RECT)
            if i:
                arrow(s, x - 0.28, y + 0.35, x - 0.03, y + 0.35, width=1.75)
    text(s, 0.5, 6.65, 12.3, 0.4, "Driver and daemon names are typical upstream examples; your platform may differ.",
         size=12, color=GREY)

    # 14. systemd targets
    s = d.slide("systemd: ordering everything", "Daemons are units; OpenBMC groups them into state targets", SEC,
                "Every daemon is a systemd service and is restarted automatically if it crashes. OpenBMC "
                "adds 'obmc' targets that model server state. Starting the host target pulls in the chassis "
                "power-on target, which runs the power-sequencing units. Platforms hook their own steps "
                "into these targets. The @0 is the host instance: multi-host systems have @0, @1 and so on.")
    box(s, 4.3, 1.4, 4.7, 0.8, "obmc-host-start@0.target", fill=BLUE, size=16, bold=True, font=MONO)
    box(s, 0.5, 2.9, 4.3, 0.8, "obmc-chassis-poweron@0.target", fill=GREEN, size=14, bold=True, font=MONO)
    box(s, 8.5, 2.9, 4.3, 0.8, "host start units\n(e.g. press power, watch boot)", fill=PURPLE, size=14)
    arrow(s, 5.5, 2.2, 2.65, 2.9, label="Requires", lsize=12)
    arrow(s, 7.8, 2.2, 10.65, 2.9, label="pulls in", lsize=12)
    for i, t in enumerate(["power-sequence units", "wait for power-good", "platform hook units"]):
        box(s, 0.5 + i * 1.45, 4.25, 1.35, 1.0, t, fill=LIGHT, fg=DARK, line=GREEN, size=11)
        arrow(s, 2.65, 3.7, 1.17 + i * 1.45, 4.25, width=1.5, head=True)
    table(s, 5.6, 3.95, 7.2, [["Target (instance @0)", "Meaning"],
                              ["obmc-chassis-poweron", "Turn chassis power on"],
                              ["obmc-host-start", "Boot the host"],
                              ["obmc-host-stop", "Shut down the host"],
                              ["obmc-chassis-poweroff", "Turn chassis power off"]],
          col_w=[3.3, 3.9], row_h=0.45, size=13, mono_cols=(0,))
    note(s, 0.5, 5.65, 4.9, 1.15, "**Commands:**  systemctl status <unit>,  systemctl --failed,  "
         "systemctl list-dependencies <target>", size=13)
