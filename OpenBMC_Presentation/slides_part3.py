"""Part 3: D-Bus backbone, interfaces, ObjectMapper, associations, signals."""
from deck_helpers import *

SEC = "D-Bus backbone"


def build(d):
    # 15. Why D-Bus
    s = d.slide("Why a message bus?", "Point-to-point wiring does not scale; a shared bus does", SEC,
                "Imagine every program had to know how to talk to every other program: that is the left "
                "picture, N times N connections and constant breakage. OpenBMC instead puts every daemon on "
                "the D-Bus system bus. A daemon publishes objects; anyone can read them, change them or "
                "subscribe to changes. Producers and consumers never need to know about each other.")
    names = ["Redfish", "IPMI", "Sensors", "Fans", "Power", "Logging"]
    import math
    cx, cy, r = 3.2, 4.1, 1.95
    pts = []
    for i, n in enumerate(names):
        a = math.pi / 2 + i * 2 * math.pi / len(names)
        x, y = cx + r * math.cos(a), cy - r * math.sin(a)
        pts.append((x, y))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            arrow(s, pts[i][0], pts[i][1], pts[j][0], pts[j][1], color=RED, width=1.25, head=False)
    for (x, y), n in zip(pts, names):
        box(s, x - 0.7, y - 0.28, 1.4, 0.56, n, fill=GREY, size=13)
    text(s, 0.5, 1.4, 5.4, 0.5, "Without a bus: 15 private links", size=18, bold=True, color=RED, align=CENTER)
    text(s, 7.0, 1.4, 5.8, 0.5, "With D-Bus: one shared backbone", size=18, bold=True, color=GREEN, align=CENTER)
    box(s, 7.0, 3.85, 5.8, 0.6, "D-Bus system bus", fill=PURPLE, size=17, bold=True)
    for i, n in enumerate(names):
        x = 7.0 + (i % 3) * 2.0
        y = 2.3 if i < 3 else 5.4
        box(s, x, y, 1.8, 0.6, n, fill=BLUE, size=14)
        arrow(s, x + 0.9, y + 0.6 if i < 3 else y, x + 0.9, 3.85 if i < 3 else 4.45, color=GREEN,
              width=2, head=True, tail=True)
    note(s, 7.0, 6.2, 5.8, 0.7, "Add or replace a daemon without touching the others.", size=14,
         fill=MINT, accent=GREEN)

    # 16. Anatomy
    s = d.slide("D-Bus anatomy: service → object → interface → property", "Four words that make every busctl output readable",
                SEC, "Read this like an address. The service is the process. The object path is the thing it "
                "exposes, here one temperature sensor. Interfaces are typed contracts on that object. "
                "Properties are the values, methods are actions, and signals announce changes. Anyone who "
                "understands Sensor.Value can read any sensor in the system, whichever daemon provides it.")
    box(s, 0.5, 1.45, 4.3, 0.95, "SERVICE (who)\nxyz.openbmc_project.HwmonTempSensor", fill=NAVY, size=13)
    box(s, 0.5, 2.95, 4.3, 0.95, "OBJECT PATH (what)\n/xyz/openbmc_project/sensors/\ntemperature/Inlet_Temp",
        fill=BLUE, size=12)
    arrow(s, 2.65, 2.4, 2.65, 2.95, width=2.5)
    ifaces = [("Interface:  xyz.openbmc_project.Sensor.Value", "Value = 27.5      Unit = DegreesC", 1.45),
              ("Interface:  ...Sensor.Threshold.Critical", "CriticalHigh = 95      CriticalAlarmHigh = false", 2.95),
              ("Interface:  ...Association.Definitions", "Links: this sensor ↔ chassis / board in inventory", 4.45)]
    for t, p, y in ifaces:
        box(s, 5.6, y, 7.2, 0.6, t, fill=PURPLE, size=14, align=LEFT)
        box(s, 5.6, y + 0.6, 7.2, 0.6, p, fill=LILAC, fg=DARK, size=14, align=LEFT, shape=RECT, font=MONO)
        arrow(s, 4.8, 3.42, 5.6, y + 0.3, width=1.75)
    table(s, 0.5, 4.45, 4.3, [["Term", "Like..."], ["Service", "A process / phone number"],
                              ["Object", "A thing it manages"], ["Interface", "A typed contract"],
                              ["Property / Method / Signal", "Value / action / notice"]],
          col_w=[2.2, 2.1], row_h=0.48, size=12)

    # 17. Namespace
    s = d.slide("The OpenBMC object namespace", "Well-known paths: learn the tree once, find anything", SEC,
                "OpenBMC daemons publish under /xyz/openbmc_project. Sensors are grouped by type, inventory "
                "follows the physical containment hierarchy, and state objects are per host, chassis or BMC. "
                "Because paths are predictable, you can usually guess where something lives before you look.")
    box(s, 0.5, 3.4, 2.7, 0.7, "/xyz/openbmc_project", fill=NAVY, size=14, bold=True, font=MONO)
    branches = [("sensors/", "temperature/Inlet_Temp\nfan_tach/Fan0\nvoltage/P12V", TEAL),
                ("inventory/", "system/board/<Board>\nsystem/chassis/...", GREEN),
                ("state/", "host0   chassis0   bmc0", BLUE),
                ("logging/", "entry/1   entry/2 ...", ORANGE),
                ("software/", "<version-id>  (firmware images)", PURPLE),
                ("network/ · user/ · control/", "eth0, users, power cap, fan mode...", GREY)]
    for i, (b, leaf, c) in enumerate(branches):
        y = 1.4 + i * 0.92
        box(s, 4.1, y, 2.9, 0.72, b, fill=c, size=14, bold=True, font=MONO)
        box(s, 7.4, y, 5.4, 0.72, leaf, fill=LIGHT, fg=DARK, size=12, font=MONO, align=LEFT, shape=RECT)
        arrow(s, 3.2, 3.75, 4.1, y + 0.36, width=1.5)
        arrow(s, 7.0, y + 0.36, 7.4, y + 0.36, width=1.5, head=False)

    # 18. phosphor-dbus-interfaces
    s = d.slide("phosphor-dbus-interfaces: the contract", "Interfaces are defined once in YAML and generated into C++", SEC,
                "The meaning of every interface lives in one repository, phosphor-dbus-interfaces, written as "
                "YAML. The sdbus++ tool generates C++ server and client bindings from it. A daemon that "
                "implements State.Host and a client that uses it compile against the same generated code. "
                "This is why two different power daemons can be swapped: they publish the same interface.")
    code(s, 0.5, 1.45, 4.7, 3.6,
         "# Sensor/Value.interface.yaml\ndescription: >\n  A sensor reading.\nproperties:\n  - name: Value\n"
         "    type: double\n  - name: Unit\n    type: enum[self.Unit]\n  - name: MaxValue\n    type: double",
         size=14)
    flow(s, 5.6, 2.55, ["YAML\ndefinition", "sdbus++\ngenerator", "C++ bindings"], 2.0, 1.2, gap=0.45,
         colors=[NAVY, PURPLE, BLUE], size=14)
    box(s, 9.9, 4.25, 2.9, 0.8, "Server: sensor daemon", fill=GREEN, size=14)
    box(s, 9.9, 5.35, 2.9, 0.8, "Client: bmcweb, ipmid", fill=ORANGE, size=14)
    arrow(s, 10.9, 3.75, 11.35, 4.25, width=2)
    arrow(s, 10.9, 3.75, 10.3, 5.35, width=2)
    note(s, 0.5, 5.35, 8.9, 1.4, "**Rule of thumb:** if two daemons agree on the interface, the "
         "implementation behind it can change without breaking anyone. Read the YAML to learn exactly "
         "what a property means and its allowed values.", size=14, fill=LILAC, accent=PURPLE)

    # 19. ObjectMapper
    s = d.slide("ObjectMapper: the bus directory", "Clients ask \"who implements X?\" instead of hard-coding service names",
                SEC, "The mapper watches every service on the bus and builds an index of object paths and the "
                "interfaces they implement. bmcweb never hard-codes 'temperatures are in HwmonTempSensor'. It "
                "asks the mapper for every object under /sensors that implements Sensor.Value, and gets back "
                "the owning services. That is what makes daemons replaceable at runtime.")
    box(s, 4.8, 2.9, 3.7, 1.4, "xyz.openbmc_project\n.ObjectMapper", fill=PURPLE, size=16, bold=True)
    for i, n in enumerate(["HwmonTempSensor", "FanSensor", "PSUSensor", "EntityManager"]):
        x = 0.5 + i * 3.15
        box(s, x, 5.4, 2.85, 0.7, n, fill=GREEN, size=13)
        arrow(s, x + 1.43, 5.4, 6.65, 4.3, color=GREEN, width=1.5, dash=True)
    text(s, 0.5, 6.2, 12.3, 0.4, "Mapper indexes services automatically as they appear and disappear (InterfacesAdded / NameOwnerChanged)",
         size=12, color=GREY, align=CENTER)
    box(s, 0.5, 1.4, 3.3, 0.9, "bmcweb\n(client)", fill=BLUE, size=15)
    arrow(s, 3.8, 1.75, 5.2, 2.9, width=2, label="GetSubTree(/sensors,\nSensor.Value)", lsize=11, lw=2.6, loff=-0.15)
    arrow(s, 5.6, 2.9, 3.8, 2.15, color=GREY, width=2, dash=True)
    code(s, 8.9, 1.4, 3.9, 1.35, "→ { \"/sensors/temperature/Inlet\":\n     \"HwmonTempSensor\",\n"
         "   \"/sensors/fan_tach/Fan0\":\n     \"FanSensor\", ... }", size=11)
    text(s, 8.9, 2.8, 3.9, 0.4, "Reply: path → owning service", size=12, color=GREY)
    table(s, 9.3, 3.35, 3.5, [["Method", "Answers"], ["GetObject", "Who owns this path?"],
                              ["GetSubTree", "All objects with iface X"], ["GetSubTreePaths", "Just the paths"]],
          col_w=[1.6, 1.9], row_h=0.42, size=11)

    # 20. Associations
    s = d.slide("Associations: linking objects together", "How Redfish knows which chassis a sensor belongs to", SEC,
                "Objects on D-Bus are flat; associations add the relationships. A sensor declares it is "
                "'chassis' of a board inventory object, and the mapper automatically creates the reverse "
                "link 'all_sensors' on the board. bmcweb follows these links to put sensors under the right "
                "Chassis in Redfish. Missing associations are a very common reason a sensor exists on D-Bus "
                "but not in Redfish.")
    box(s, 0.6, 2.2, 4.4, 1.2, "Sensor\n/sensors/temperature/Inlet_Temp", fill=TEAL, size=14)
    box(s, 8.3, 2.2, 4.4, 1.2, "Inventory item\n/inventory/system/board/MyBoard", fill=GREEN, size=14)
    arrow(s, 5.0, 2.5, 8.3, 2.5, color=BLUE, width=2.5, label="forward: \"chassis\"", lsize=13)
    arrow(s, 8.3, 3.1, 5.0, 3.1, color=ORANGE, width=2.5, dash=True)
    text(s, 5.0, 3.15, 3.3, 0.4, "reverse: \"all_sensors\" (auto)", size=13, color=ORANGE, align=CENTER)
    box(s, 0.6, 4.2, 12.1, 0.75, "Redfish:  /redfish/v1/Chassis/MyBoard/Sensors/Inlet_Temp", fill=BLUE, size=16,
        font=MONO)
    arrow(s, 6.65, 3.6, 6.65, 4.2, width=2.5)
    for i, (t, c) in enumerate([("Sensor ↔ chassis/board", TEAL), ("LED group ↔ inventory item (identify)", ORANGE),
                                ("Log entry ↔ failing part (callout)", RED), ("Software ↔ the device it runs on", PURPLE)]):
        box(s, 0.6 + i * 3.07, 5.4, 2.9, 1.0, t, fill=LIGHT, fg=DARK, line=c, size=13, lw=2)

    # 21. Signals and patterns
    s = d.slide("Event-driven patterns: signals and requested state", "Ask by writing a property; learn by listening",
                SEC, "Two patterns appear everywhere. First, you request an action by writing a 'Requested' "
                "property, and the owner reports the result in a 'Current' property. Second, nobody polls "
                "other daemons: they subscribe to PropertiesChanged and InterfacesAdded signals. One change "
                "can wake up many listeners at once, which is how alerts, LEDs and Redfish events all "
                "react to the same sensor event.")
    text(s, 0.5, 1.35, 6.0, 0.45, "Pattern 1: Requested → Current", size=18, bold=True, color=BLUE)
    sequence(s, 0.5, 1.85, 6.0, 4.6, ["Client", "State.Host owner"],
             [(0, 1, "set RequestedHostTransition = On"), (1, 1, "do the work (GPIO, targets)"),
              (1, 0, "CurrentHostState = Running", True)], colors=[BLUE, GREEN], size=12)
    text(s, 7.0, 1.35, 5.8, 0.45, "Pattern 2: one signal, many listeners", size=18, bold=True, color=PURPLE)
    box(s, 7.0, 2.0, 5.8, 0.85, "Sensor daemon emits PropertiesChanged\n(CriticalAlarmHigh = true)", fill=TEAL, size=14)
    for i, (t, c) in enumerate([("Logging: create entry", ORANGE), ("LED manager: fault LED", RED),
                                ("Fan control: speed up", SKY), ("bmcweb: Redfish event", BLUE)]):
        x, y = 7.0 + (i % 2) * 3.0, 3.8 + (i // 2) * 1.2
        box(s, x, y, 2.8, 0.85, t, fill=c, size=13)
        arrow(s, 9.9, 2.85, x + 1.4, y, color=PURPLE, width=1.5)
    note(s, 7.0, 6.25, 5.8, 0.65, "Watch live:  busctl monitor <service>", size=13, fill=LILAC, accent=PURPLE)
