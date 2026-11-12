"""Part 4: function daemons — inventory, sensors, fans, power, logging, update, host protocols."""
from deck_helpers import *

SEC = "Function daemons"


def build(d):
    # 22. Daemon map
    s = d.slide("The daemon map", "Small single-purpose services, grouped by job (typical upstream names)", SEC,
                "This is the population of a typical OpenBMC image. Each box is a job; the names inside are "
                "the repositories or daemons that do it. Where you see two names separated by 'or', those "
                "are alternative implementations of the same D-Bus interfaces, and each platform picks one.")
    cats = [("Inventory & config", "entity-manager, fru-device\nor phosphor-inventory-manager", GREEN),
            ("Sensors", "dbus-sensors (hwmontemp, adc, fan, psu, cpu, nvme)\nor phosphor-hwmon", TEAL),
            ("Fan control", "phosphor-pid-control (swampd)\nphosphor-fan-presence", SKY),
            ("Power & state", "phosphor-state-manager\nor x86-power-control", BLUE),
            ("Logging", "phosphor-logging (event log)\nphosphor-sel-logger (IPMI SEL)", ORANGE),
            ("Firmware update", "phosphor-bmc-code-mgmt", PURPLE),
            ("Host protocols", "ipmid, kcsbridged, netipmid\npldmd, mctpd", RED),
            ("Remote access", "obmc-console, obmc-ikvm\nvirtual media", rgb("2E4057")),
            ("Network, users, time", "phosphor-networkd\nphosphor-user-manager\nphosphor-time-manager", GREY),
            ("LEDs, buttons, dumps", "phosphor-led-manager, phosphor-buttons\nphosphor-debug-collector", rgb("8E5BB5"))]
    for i, (t, sub, c) in enumerate(cats):
        x, y = 0.5 + (i % 5) * 2.5, 1.4 + (i // 5) * 2.6
        box(s, x, y, 2.35, 0.65, t, fill=c, size=14, bold=True, shape=RECT)
        box(s, x, y + 0.65, 2.35, 1.75, sub, fill=LIGHT, fg=DARK, size=11, shape=RECT)
    box(s, 0.5, 6.5, 12.35, 0.45, "All of them publish and consume objects on the D-Bus system bus",
        fill=PURPLE, size=14, bold=True, shape=RECT)

    # 23. Entity-manager
    s = d.slide("entity-manager: hardware described as data", "Probe decides WHEN a config applies; Exposes says WHAT is on the board",
                SEC, "fru-device reads the FRU EEPROMs and publishes what it found. entity-manager loads JSON "
                "files; each has a Probe, for example 'the board FRU says product name X'. When the probe "
                "matches, every record in Exposes is published as a Configuration object on D-Bus. Sensor "
                "and fan daemons pick those up. Adding a board is mostly JSON plus device tree, not C++. "
                "It also handles hot-plug: when a PSU's FRU appears, its configuration activates.")
    code(s, 0.5, 1.4, 5.6, 5.0,
         "{\n  \"Name\": \"MyBoard\",\n  \"Probe\":\n    \"xyz.openbmc_project.FruDevice\n"
         "     ({'BOARD_PRODUCT_NAME': 'MyBoard'})\",\n  \"Exposes\": [\n    {\n      \"Name\": \"Inlet_Temp\",\n"
         "      \"Type\": \"TMP75\",\n      \"Bus\": 6,\n      \"Address\": \"0x48\",\n"
         "      \"Thresholds\": [ ... ]\n    },\n    { \"Type\": \"AspeedFan\", ... }\n  ]\n}", size=13)
    text(s, 0.5, 6.45, 5.6, 0.4, "Simplified entity-manager JSON (example)", size=12, color=GREY, align=CENTER)
    vflow(s, 6.8, 1.4, ["fru-device reads FRU EEPROMs over I2C", "entity-manager: does any Probe match?",
                        "Publish Configuration.TMP75 (Bus 6, 0x48)", "Sensor daemon sees it → creates sensor"],
          6.0, 0.85, gap=0.4, colors=[GREEN, NAVY, PURPLE, TEAL], size=15)
    note(s, 6.8, 6.0, 6.0, 0.85, "Also publishes **inventory** objects (board, chassis) used by Redfish.",
         size=14, fill=MINT, accent=GREEN)

    # 24. Sensor bring-up
    s = d.slide("Sensor lifecycle: from FRU to D-Bus value", "Who does what, in order", SEC,
                "Walk the arrows. fru-device publishes FRU data. entity-manager matches the probe and "
                "publishes a configuration. The hwmon temperature daemon sees the new configuration, asks "
                "the kernel to bind the driver at that bus and address, finds the hwmon sysfs node and "
                "publishes the sensor object. Then it polls forever, updating Value and checking thresholds.")
    sequence(s, 0.4, 1.35, 12.5, 5.6, ["fru-device", "entity-manager", "hwmontempsensor", "Linux kernel", "ObjectMapper"],
             [(0, 1, "FRU data on D-Bus"), (1, 1, "Probe matches JSON"),
              (1, 2, "Configuration.TMP75 {Bus, Address}"), (2, 3, "bind driver (new_device)"),
              (3, 2, "hwmonN/temp1_input", True), (2, 4, "publish /sensors/temperature/Inlet_Temp"),
              (2, 2, "loop: read sysfs, update Value, check thresholds")],
             colors=[GREEN, NAVY, TEAL, rgb("2E4057"), PURPLE], size=12)

    # 25. Thresholds
    s = d.slide("Inside a sensor: value and thresholds", "One reading, four alarm levels", SEC,
                "A sensor object carries its current value and threshold interfaces. Warning and critical "
                "levels exist for both high and low. When the value crosses a level, the matching alarm "
                "property flips to true and a signal goes out. Hysteresis stops the alarm toggling on "
                "and off when the value hovers near the limit.")
    zones = [("Critical low", RED, 1.3), ("Warning low", ORANGE, 1.3), ("Normal", GREEN, 5.2),
             ("Warning high", ORANGE, 1.6), ("Critical high", RED, 1.6)]
    x = 0.6
    for t, c, w in zones:
        box(s, x, 1.8, w, 0.9, t, fill=c, size=14, bold=True, shape=RECT)
        x += w
    for t, xx in [("5 °C", 1.9), ("10 °C", 3.2), ("85 °C", 8.4), ("95 °C", 10.0)]:
        arrow(s, xx, 1.55, xx, 2.95, color=DARK, width=1.5, head=False, dash=True)
        text(s, xx - 0.6, 2.95, 1.2, 0.35, t, size=12, align=CENTER)
    box(s, 5.7, 1.35, 0.9, 0.4, "27.5", fill=NAVY, size=13, bold=True)
    arrow(s, 6.15, 1.75, 6.15, 1.95, color=NAVY, width=3)
    table(s, 0.6, 3.6, 7.2, [["Property", "Interface", "Example"],
                             ["Value", "Sensor.Value", "27.5"], ["WarningHigh", "Threshold.Warning", "85"],
                             ["WarningAlarmHigh", "Threshold.Warning", "false"], ["CriticalHigh", "Threshold.Critical", "95"],
                             ["CriticalAlarmHigh", "Threshold.Critical", "false"]],
          col_w=[2.6, 2.8, 1.8], row_h=0.48, size=13, mono_cols=(0,))
    bullets(s, 8.2, 3.6, 4.6, 3.0, ["Crossing a level sets the **Alarm** property true",
                                     "A **PropertiesChanged** signal goes out",
                                     "Logging, LEDs, fans and Redfish react",
                                     "**Hysteresis** prevents flapping near the limit"], size=15)
    text(s, 0.6, 6.55, 7.2, 0.35, "Threshold numbers are examples; real limits come from configuration.",
         size=12, color=GREY)

    # 26. Fan control
    s = d.slide("Fan control: a closed loop", "phosphor-pid-control (swampd) — sensors in, PWM out", SEC,
                "Fan control is a feedback loop. Thermal PID controllers compare temperatures with a setpoint "
                "and decide how much cooling a zone needs. The highest demand wins. A fan PID turns that into "
                "PWM, and the tach reading closes the loop. If a sensor goes missing or fails, the zone enters "
                "failsafe mode and runs the fans at a safe high speed.")
    box(s, 0.5, 2.0, 2.4, 1.1, "Temperature\nsensors", fill=TEAL, size=15)
    box(s, 3.5, 2.0, 2.6, 1.1, "Thermal PIDs\n(per zone)", fill=PURPLE, size=15)
    box(s, 6.7, 2.0, 2.3, 1.1, "Max demand\n→ RPM setpoint", fill=NAVY, size=14)
    box(s, 9.6, 2.0, 2.9, 1.1, "Fan PID\n→ PWM duty", fill=BLUE, size=15)
    box(s, 9.6, 4.1, 2.9, 1.1, "Fans", fill=SKY, size=18, bold=True)
    box(s, 3.5, 4.1, 5.5, 1.1, "Tach feedback (actual RPM)", fill=LIGHT, fg=DARK, line=SKY, size=15)
    arrow(s, 2.9, 2.55, 3.5, 2.55, width=2.5)
    arrow(s, 6.1, 2.55, 6.7, 2.55, width=2.5)
    arrow(s, 9.0, 2.55, 9.6, 2.55, width=2.5)
    arrow(s, 11.05, 3.1, 11.05, 4.1, width=2.5, label="PWM", lsize=12, lw=1.0)
    arrow(s, 9.6, 4.65, 9.0, 4.65, width=2.5)
    arrow(s, 6.25, 4.1, 10.5, 3.1, width=2, dash=True, color=SKY)
    text(s, 0.5, 1.35, 12, 0.5, "Heat goes up → temperature rises → more demand → faster fans → temperature falls",
         size=15, color=GREY)
    note(s, 0.5, 5.65, 5.9, 1.2, "**Failsafe:** missing or failed sensor in a zone → fans to a safe high speed.",
         size=14, fill=AMBER, accent=RED)
    note(s, 6.7, 5.65, 6.1, 1.2, "Configured per platform in JSON: zones, sensors, setpoints, PID gains.",
         size=14, fill=MINT, accent=GREEN)

    # 27. Power state
    s = d.slide("Power and state management", "Three state objects: Chassis, Host, BMC", SEC,
                "There are three state objects. Chassis is about electrical power. Host is about the software "
                "running on the host CPUs. BMC is about the BMC itself. A request such as 'power on' is a "
                "write to RequestedHostTransition. The owner runs the sequence, either via systemd targets "
                "in phosphor-state-manager or directly with GPIOs in x86-power-control, then updates the "
                "Current properties as power-good and boot progress arrive.")
    states = [("Off", 0.6, GREY), ("Transitioning\nToRunning", 3.6, ORANGE), ("Running", 6.6, GREEN),
              ("Transitioning\nToOff", 9.6, ORANGE)]
    for t, x, c in states:
        box(s, x, 1.6, 2.4, 1.0, t, fill=c, size=15, bold=True, shape=OVAL)
    arrow(s, 3.0, 2.1, 3.6, 2.1, width=2.5)
    arrow(s, 6.0, 2.1, 6.6, 2.1, width=2.5)
    arrow(s, 9.0, 2.1, 9.6, 2.1, width=2.5)
    arrow(s, 10.8, 2.6, 1.8, 2.6, color=GREY, width=1.75, dash=True)
    text(s, 4.5, 2.65, 4.5, 0.4, "back to Off", size=12, color=GREY, align=CENTER)
    text(s, 0.6, 3.05, 12, 0.4, "Host state (simplified) — other states such as Quiesced and DiagnosticMode also exist",
         size=12, color=GREY)
    table(s, 0.6, 3.6, 12.2, [["Object", "Request with", "Watch result in", "Example values"],
                              ["/state/chassis0", "RequestedPowerTransition", "CurrentPowerState", "On, Off"],
                              ["/state/host0", "RequestedHostTransition", "CurrentHostState", "Running, Off"],
                              ["/state/bmc0", "RequestedBMCTransition", "CurrentBMCState", "Ready, NotReady"]],
          col_w=[2.4, 3.6, 3.2, 3.0], row_h=0.5, size=14, mono_cols=(0, 1, 2))
    box(s, 0.6, 5.85, 5.9, 0.95, "phosphor-state-manager:\nsystemd obmc-* targets run the sequence", fill=BLUE, size=14)
    box(s, 6.9, 5.85, 5.9, 0.95, "x86-power-control:\ndrives power/reset GPIOs directly, watches PGOOD", fill=PURPLE,
        size=14)

    # 28. Logging
    s = d.slide("Logging and events", "One error becomes a D-Bus object everyone can see", SEC,
                "Daemons report errors through phosphor-logging. Each event becomes a Logging Entry object "
                "with severity, message, timestamp and associations to the failing part. Redfish shows it "
                "in the event log and can push it to subscribers; IPMI shows it as SEL records. The systemd "
                "journal still holds the detailed debug text. Use the entry for 'what happened', the journal "
                "for 'why'.")
    box(s, 0.5, 2.7, 2.6, 1.3, "Any daemon\ndetects a fault", fill=TEAL, size=15)
    box(s, 3.7, 2.7, 2.8, 1.3, "phosphor-logging", fill=ORANGE, size=16, bold=True)
    box(s, 7.1, 2.7, 3.0, 1.3, "/logging/entry/N\nSeverity · Message\nTimestamp · callout", fill=NAVY, size=13)
    arrow(s, 3.1, 3.35, 3.7, 3.35, width=2.5)
    arrow(s, 6.5, 3.35, 7.1, 3.35, width=2.5)
    outs = [("Redfish LogServices\n+ EventService push", BLUE, 1.4), ("IPMI SEL\n(phosphor-sel-logger)", RED, 3.0),
            ("Fault LED via\nassociation", ORANGE, 4.6)]
    for t, c, y in outs:
        box(s, 10.7, y, 2.2, 1.1, t, fill=c, size=12)
        arrow(s, 10.1, 3.35, 10.7, y + 0.55, width=1.75)
    box(s, 0.5, 5.4, 6.0, 1.3, "systemd journal (journalctl)\nDetailed text for developers", fill=LIGHT, fg=DARK,
        line=GREY, size=14)
    arrow(s, 1.8, 4.0, 1.8, 5.4, color=GREY, width=1.75, dash=True)
    note(s, 7.1, 5.4, 3.3, 1.3, "Entry = **what** happened.\nJournal = **why**.", size=14)

    # 29. Firmware update
    s = d.slide("Firmware update flow", "Upload → verify → activate → reboot", SEC,
                "An image is uploaded through Redfish UpdateService or a copy to the BMC. The code-management "
                "daemon unpacks it, checks the manifest and signature, and publishes a Software object with "
                "version and purpose. Activation writes the flash, often to the inactive side on dual-image "
                "systems. After reboot the new image runs, and the old one remains available for recovery "
                "on dual-image designs. Exact flow and interfaces differ by release and platform.")
    flow(s, 0.5, 1.6, ["Upload image\n(Redfish)", "Verify manifest\n& signature", "Software object\non D-Bus",
                       "Activate:\nwrite flash", "Reboot into\nnew image"], 2.2, 1.2, gap=0.32,
         colors=[BLUE, RED, PURPLE, ORANGE, GREEN], size=14)
    table(s, 0.5, 3.3, 7.3, [["Software object property", "Example"], ["Version", "2.16.0-dev"],
                             ["Purpose", "BMC, Host (BIOS), PSU..."], ["Activation", "Ready → Activating → Active"],
                             ["Priority", "Which image boots next"]],
          col_w=[3.6, 3.7], row_h=0.5, size=14)
    box(s, 8.3, 3.3, 2.1, 1.0, "Image A\n(running)", fill=GREEN, size=14)
    box(s, 10.7, 3.3, 2.1, 1.0, "Image B\n(being written)", fill=ORANGE, size=14)
    text(s, 8.3, 4.4, 4.5, 0.8, "Dual-image (A/B): a failed update falls back to the good copy", size=13,
         color=GREY, align=CENTER)
    note(s, 0.5, 6.0, 12.3, 0.85, "**Never** interrupt power during the flash-write step on single-image systems. "
         "Know your platform's recovery path before updating.", size=14, fill=AMBER, accent=RED)

    # 30. Host protocols
    s = d.slide("Talking to the host: IPMI, MCTP, PLDM", "In-band (from the host) and out-of-band (from the network)",
                SEC, "In-band IPMI: the BIOS or OS writes to the KCS interface; kcsbridged moves the message onto "
                "D-Bus and ipmid handles it with plug-in command providers. Out-of-band IPMI arrives over the "
                "network on UDP 623 to netipmid. MCTP is a modern transport over I2C/I3C or PCIe; mctpd "
                "assigns endpoint IDs, and pldmd uses PLDM over MCTP for sensors and firmware update of "
                "devices like NICs, GPUs and the host.")
    box(s, 0.5, 1.5, 2.6, 1.0, "BIOS / host OS\n(ipmitool)", fill=GREY, size=14)
    box(s, 3.7, 1.5, 2.4, 1.0, "KCS / BT", fill=PURPLE, size=15)
    box(s, 6.7, 1.5, 2.4, 1.0, "kcsbridged", fill=RED, size=15)
    box(s, 0.5, 3.0, 2.6, 1.0, "Remote admin\n(ipmitool -I lanplus)", fill=GREY, size=13)
    box(s, 3.7, 3.0, 5.4, 1.0, "netipmid  (RMCP+, UDP 623)", fill=RED, size=15)
    box(s, 9.7, 1.5, 3.1, 2.5, "ipmid\n+ command providers\n→ D-Bus objects", fill=NAVY, size=15)
    for y in (2.0, 3.5):
        arrow(s, 3.1, y, 3.7, y, width=2)
    arrow(s, 6.1, 2.0, 6.7, 2.0, width=2)
    arrow(s, 9.1, 2.0, 9.7, 2.0, width=2)
    arrow(s, 9.1, 3.5, 9.7, 3.5, width=2)
    box(s, 0.5, 4.6, 2.6, 1.0, "NIC, GPU, drives,\nhost firmware", fill=GREY, size=13)
    box(s, 3.7, 4.6, 2.4, 1.0, "MCTP\n(I2C/I3C, PCIe)", fill=TEAL, size=14)
    box(s, 6.7, 4.6, 2.4, 1.0, "mctpd\n(assigns EIDs)", fill=GREEN, size=14)
    box(s, 9.7, 4.6, 3.1, 1.0, "pldmd: sensors,\nfirmware update", fill=BLUE, size=14)
    for x in (3.1, 6.1, 9.1):
        arrow(s, x, 5.1, x + 0.6, 5.1, width=2)
    note(s, 0.5, 6.0, 12.3, 0.85, "Same rule as everywhere: every protocol ends up reading or writing **D-Bus objects**.",
         size=15, fill=LILAC, accent=PURPLE)
