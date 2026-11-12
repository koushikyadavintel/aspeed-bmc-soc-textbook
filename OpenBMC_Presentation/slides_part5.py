"""Part 5: remote access, bmcweb, end-to-end flows, Redfish mapping, security."""
from deck_helpers import *

SEC = "External interfaces & flows"


def build(d):
    # 31. Remote access
    s = d.slide("Remote access: console, KVM, virtual media", "Being 'at the server' without being in the data center",
                SEC, "Three features replace a physical visit. Serial over LAN: obmc-console connects to the host "
                "UART and fans it out to SSH, the web UI and IPMI SOL. KVM: obmc-ikvm captures the host's "
                "screen from the BMC video engine and sends keyboard and mouse back as a USB HID gadget. "
                "Virtual media: the BMC presents an ISO as a USB drive to the host, so you can install an "
                "OS remotely.")
    rows = [("Serial console (SOL)", "Host UART → obmc-console-server", "SSH (port 2200), Web UI, IPMI SOL", TEAL),
            ("Graphical KVM", "BMC video engine (screen) + USB HID gadget (keys)", "obmc-ikvm → bmcweb WebSocket (VNC)", BLUE),
            ("Virtual media", "USB mass-storage gadget → host sees a drive", "ISO streamed via bmcweb / NBD", PURPLE)]
    box(s, 0.5, 1.4, 3.2, 0.55, "Feature", fill=NAVY, size=15, bold=True, shape=RECT)
    box(s, 4.0, 1.4, 4.4, 0.55, "Host side (hardware path)", fill=NAVY, size=15, bold=True, shape=RECT)
    box(s, 8.7, 1.4, 4.1, 0.55, "User side (how you reach it)", fill=NAVY, size=15, bold=True, shape=RECT)
    for i, (f, h, u, c) in enumerate(rows):
        y = 2.2 + i * 1.35
        box(s, 0.5, y, 3.2, 1.1, f, fill=c, size=16, bold=True)
        box(s, 4.0, y, 4.4, 1.1, h, fill=LIGHT, fg=DARK, size=14)
        box(s, 8.7, y, 4.1, 1.1, u, fill=LIGHT, fg=DARK, size=14)
        arrow(s, 3.7, y + 0.55, 4.0, y + 0.55, width=2)
        arrow(s, 8.4, y + 0.55, 8.7, y + 0.55, width=2, tail=True)
    note(s, 0.5, 6.25, 12.3, 0.65, "All three need the right hardware wiring (UART, PCIe VGA, USB) — check the board first.",
         size=14)

    # 32. bmcweb
    s = d.slide("bmcweb: the front door", "One C++ web server for Redfish, Web UI and WebSockets", SEC,
                "Every HTTPS request goes through the same pipeline. TLS, then authentication by session "
                "token, basic auth, cookie or client certificate. Then routing to a handler, a privilege "
                "check against the Redfish privilege registry, and the handler itself, which makes "
                "asynchronous D-Bus calls and builds JSON. bmcweb holds no hardware logic and no cache of "
                "hardware values: it is a translator.")
    flow(s, 0.4, 1.6, ["TLS", "Authenticate", "Route URL", "Privilege\ncheck", "Handler:\nasync D-Bus", "JSON\nresponse"],
         1.8, 1.2, gap=0.3, colors=[NAVY, RED, BLUE, ORANGE, PURPLE, GREEN], size=15)
    details = ["HTTPS only; certs managed on D-Bus", "Session token, basic, cookie or mTLS",
               "/redfish/v1/... → handler function", "Role: Administrator / Operator / ReadOnly",
               "Mapper lookups + property reads", "Redfish schema-shaped JSON"]
    for i, t in enumerate(details):
        box(s, 0.4 + i * 2.1, 2.95, 1.8, 1.3, t, fill=LIGHT, fg=DARK, size=12, shape=RECT)
    for i, (t, sub, c) in enumerate([("Redfish", "/redfish/v1 REST API", BLUE),
                                     ("Web UI", "webui-vue single-page app", GREEN),
                                     ("WebSockets", "KVM, serial console, virtual media", PURPLE)]):
        x = 0.4 + i * 4.2
        box(s, x, 4.65, 3.9, 0.6, t, fill=c, size=16, bold=True, shape=RECT)
        box(s, x, 5.25, 3.9, 0.6, sub, fill=LIGHT, fg=DARK, size=13, shape=RECT)
    note(s, 0.4, 6.15, 12.4, 0.75, "bmcweb is a **translator**: if data is wrong in Redfish but right on D-Bus, the bug "
         "is in bmcweb; if wrong on D-Bus too, look lower.", size=14)

    # 33. Flow A
    s = d.slide("Flow 1: reading a temperature over Redfish", "Follow one request through every layer", SEC,
                "The client sends GET. bmcweb authenticates and asks the mapper which service owns sensor "
                "objects. It then reads properties from that service directly. Notice that the sensor daemon "
                "had already read the hardware before the request arrived; it polls continuously. The request "
                "never touches I2C. That is why Redfish reads are fast, and why a stale value means the sensor "
                "daemon, not bmcweb, stopped updating.")
    sequence(s, 0.4, 1.35, 12.5, 5.0, ["Redfish client", "bmcweb", "ObjectMapper", "Sensor daemon", "Kernel / chip"],
             [(4, 3, "periodic read (before any request)", True),
              (0, 1, "GET .../Sensors/Inlet_Temp"), (1, 1, "TLS, auth, privilege"),
              (1, 2, "GetSubTree(Sensor.Value)"), (2, 1, "path → service", True),
              (1, 3, "Properties.GetAll"), (3, 1, "Value 27.5, thresholds", True),
              (1, 0, "JSON  { \"Reading\": 27.5 }", True)],
             colors=[GREY, BLUE, PURPLE, TEAL, rgb("2E4057")], size=12)
    text(s, 0.4, 6.45, 12.5, 0.45, "The HTTP request never touches the I2C bus: values come from the daemon's latest poll.",
         size=13, color=GREY, align=CENTER)

    # 34. Flow B
    s = d.slide("Flow 2: powering on the host", "A write to one property starts the whole sequence", SEC,
                "The Redfish Reset action becomes a single property write: RequestedHostTransition equals On. "
                "bmcweb replies immediately, because power-on is asynchronous. The state daemon starts the "
                "systemd targets or toggles GPIOs, waits for power-good, and updates the Current properties. "
                "Clients poll PowerState or subscribe to events to see the result.")
    sequence(s, 0.4, 1.35, 12.5, 5.0, ["Redfish client", "bmcweb", "State.Host owner", "systemd / GPIO", "Power hardware"],
             [(0, 1, "POST ComputerSystem.Reset {On}"), (1, 2, "RequestedHostTransition = On"),
              (1, 0, "Success reply (async)", True), (2, 3, "start obmc-host-start@0 / press GPIO"),
              (3, 4, "power sequence"), (4, 2, "power-good asserted", True),
              (2, 2, "CurrentHostState = Running → signal")],
             colors=[GREY, BLUE, GREEN, PURPLE, rgb("2E4057")], size=12)
    text(s, 0.4, 6.45, 12.5, 0.45, "ipmitool chassis power on writes the very same D-Bus property.",
         size=13, color=GREY, align=CENTER)

    # 35. Flow C
    s = d.slide("Flow 3: an over-temperature alert", "One threshold crossing, many independent reactions", SEC,
                "A temperature crosses its critical threshold. The sensor daemon flips CriticalAlarmHigh and "
                "emits a signal. Nobody calls anybody: each interested daemon has subscribed. Logging writes an "
                "entry, the LED manager lights the fault LED, fan control speeds up, bmcweb pushes a Redfish "
                "event to subscribers, and the IPMI SEL gets a record. If the condition is severe, the platform "
                "policy may also power the host off.")
    flow(s, 0.5, 1.5, ["Temp rises\nabove 95 °C", "CriticalAlarmHigh\n= true", "PropertiesChanged\nsignal"], 3.5, 1.1,
         gap=0.9, colors=[RED, ORANGE, PURPLE], size=15)
    reacts = [("Event log entry", "phosphor-logging", ORANGE), ("Fault LED on", "led-manager", RED),
              ("Fans to max", "pid-control", SKY), ("Redfish event", "bmcweb EventService", BLUE),
              ("IPMI SEL record", "sel-logger", rgb("8E5BB5")), ("Optional shutdown", "platform policy", GREY)]
    for i, (t, who, c) in enumerate(reacts):
        x = 0.5 + i * 2.1
        box(s, x, 3.6, 1.9, 1.0, t, fill=c, size=14, bold=True)
        box(s, x, 4.6, 1.9, 0.55, who, fill=LIGHT, fg=DARK, size=11, shape=RECT)
        arrow(s, 11.05, 2.6, x + 0.95, 3.6, color=PURPLE, width=1.5)
    note(s, 0.5, 5.6, 12.3, 1.2, "**Decoupled by design:** adding a new reaction (e.g. an SNMP trap) means one more "
         "listener — no change to the sensor daemon.", size=15, fill=LILAC, accent=PURPLE)

    # 36. Mapping
    s = d.slide("Redfish resources ↔ D-Bus objects", "Where each Redfish URL gets its data", SEC,
                "This table is the translation key. When a Redfish property looks wrong, find its row, then "
                "inspect the D-Bus object on the right with busctl. If D-Bus is right, the bug is in bmcweb. "
                "If D-Bus is wrong, go to the daemon that owns that object.")
    table(s, 0.5, 1.4, 12.3, [
        ["Redfish resource", "D-Bus source (typical)"],
        ["/redfish/v1/Systems/system  (PowerState, Reset)", "/xyz/openbmc_project/state/host0, chassis0"],
        ["/redfish/v1/Chassis/<id>", "Inventory Board / Chassis objects (entity-manager)"],
        ["/redfish/v1/Chassis/<id>/Sensors, Thermal, Power", "/xyz/openbmc_project/sensors/*  + associations"],
        ["/redfish/v1/Managers/bmc", "/xyz/openbmc_project/state/bmc0, network, time"],
        ["/redfish/v1/UpdateService", "/xyz/openbmc_project/software/*"],
        ["/redfish/v1/AccountService", "/xyz/openbmc_project/user/*  (user manager)"],
        ["/redfish/v1/Systems/system/LogServices/EventLog", "/xyz/openbmc_project/logging/entry/*"],
        ["/redfish/v1/EventService", "Signals on the bus → pushed to subscribers"],
    ], col_w=[6.2, 6.1], row_h=0.55, size=14, mono_cols=(0, 1))
    note(s, 0.5, 6.4, 12.3, 0.5, "Resource IDs such as 'system' and 'bmc' are bmcweb defaults; platforms may differ.",
         size=13)

    # 37. Convergence
    s = d.slide("All interfaces converge on D-Bus", "Redfish, IPMI, Web UI and SSH tools are just different doors",
                SEC, "This is why OpenBMC behaves consistently. Whether an admin uses Redfish, ipmitool, the web "
                "UI or busctl on the BMC, the request lands on the same D-Bus objects. Fix the data once at the "
                "D-Bus layer and every interface sees the fix. It also means testing at D-Bus level isolates "
                "front-end bugs from back-end bugs.")
    doors = [("Redfish", BLUE), ("Web UI", GREEN), ("IPMI (in-band)", RED), ("IPMI (LAN)", ORANGE),
             ("busctl / SSH", GREY)]
    for i, (t, c) in enumerate(doors):
        x = 0.5 + i * 2.5
        box(s, x, 1.5, 2.3, 0.85, t, fill=c, size=15, bold=True)
        arrow(s, x + 1.15, 2.35, 6.65, 3.5, color=c, width=2)
    box(s, 3.0, 3.5, 7.3, 1.0, "Same D-Bus objects  (e.g. /state/host0, /sensors/...)", fill=PURPLE, size=17, bold=True)
    box(s, 3.0, 5.0, 7.3, 0.9, "Owning daemons  →  kernel  →  hardware", fill=NAVY, size=16)
    arrow(s, 6.65, 4.5, 6.65, 5.0, width=2.5)
    note(s, 0.5, 6.15, 12.3, 0.75, "**Debug tip:** reproduce with busctl first. If busctl works, the bug is in the front end.",
         size=14)

    # 38. Security
    s = d.slide("Security architecture", "Defence in layers, from boot to API", SEC,
                "Security is layered too. Secure boot verifies the firmware chain. Firmware updates are signed. "
                "Users have roles that map to Redfish privileges and to IPMI and SSH access. All web traffic is "
                "TLS and certificates are managed through D-Bus. Each daemon runs as a separate process, so a "
                "bug is contained. Operationally: change default passwords, disable unused interfaces such "
                "as IPMI over LAN, and keep the BMC on an isolated management network.")
    layers = [("Network", "Isolated mgmt network · disable unused services (e.g. IPMI LAN) · TLS only", BLUE),
              ("API", "Authentication · Redfish roles: Administrator / Operator / ReadOnly · session limits", PURPLE),
              ("Accounts", "phosphor-user-manager · PAM · LDAP · no default passwords in production", ORANGE),
              ("Services", "Separate processes · systemd restarts · least-privilege where supported", GREEN),
              ("Firmware", "Signed images for update · secure boot of U-Boot/kernel (platform feature)", RED)]
    for i, (t, sub, c) in enumerate(layers):
        y = 1.4 + i * 1.0
        box(s, 0.5 + i * 0.3, y, 2.4, 0.82, t, fill=c, size=16, bold=True)
        box(s, 2.95 + i * 0.3, y, 9.85 - i * 0.3, 0.82, sub, fill=LIGHT, fg=DARK, size=14, align=LEFT)
    text(s, 0.5, 6.45, 12.3, 0.45, "Outer layers first: an attacker must pass network, then API, then account checks.",
         size=13, color=GREY, align=CENTER)
