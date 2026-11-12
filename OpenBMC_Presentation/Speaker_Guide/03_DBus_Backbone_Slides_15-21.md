# Speaker Guide, Part 3: D-Bus Backbone (Slides 15-21)

[← Part 2](02_Hardware_and_Boot_Slides_09-14.md) · [Part 4 →](04_Function_Daemons_Slides_22-30.md)

This is the most important section of the talk. If the audience understands D-Bus, the rest of OpenBMC becomes easy to follow. Slow down here.

---

## Slide 15: Why a message bus?

**Purpose:** motivate D-Bus by showing the problem it solves.

**What's on the slide:**
- **Left (red):** six programs (Redfish, IPMI, Sensors, Fans, Power, Logging) all wired to each other: **15 private links**.
- **Right (green):** the same six programs each connected once to a shared **D-Bus system bus**.
- **Callout:** add or replace a daemon without touching the others.

**In depth:**
- **The arithmetic:** with $n$ programs all talking directly to each other, you need $\frac{n(n-1)}{2}$ connections. 6 programs → 15 links. 30 programs (a realistic BMC) → **435**. Each link is a private protocol that breaks when either side changes.
- **With a bus:** each program connects **once** and speaks **one** protocol. Adding a program adds one connection.
- **What D-Bus is:** a standard Linux **inter-process communication (IPC)** system. A central **broker** process routes messages between connected programs. OpenBMC uses **dbus-broker**, a fast implementation; desktop Linux uses the same technology.
- **System bus vs session bus:** desktops have a per-user *session* bus. OpenBMC uses only the single **system bus** (`/run/dbus/system_bus_socket`).
- **What the bus gives you for free:**
  - **Discovery:** list every connected program (`busctl list`).
  - **Typed messages:** every value has a declared type (string, integer, double, array…).
  - **Publish/subscribe:** programs subscribe to signals; the broker delivers them.
  - **Introspection:** ask any object what methods and properties it has (`busctl introspect`).
  - **Access control:** policies decide who may call what.
- **The key benefit:** a producer (sensor daemon) doesn't know or care who consumes its data (Redfish, IPMI, fan control, logging). Consumers don't care which daemon produces it. They only agree on the **interface** (slide 18).

**Likely questions:**
- *"Isn't a central broker a bottleneck or single point of failure?"* Throughput is fine for management traffic. If dbus-broker died, the system would be badly broken, but it's very stable, and systemd itself depends on it.
- *"Why not REST or gRPC between daemons?"* D-Bus is already part of systemd-based Linux, is lightweight, and has signals and introspection built in.

**Transition:** "So what does a daemon actually put on the bus? Four words explain everything."

---

## Slide 16: D-Bus anatomy — service → object → interface → property

**Purpose:** teach the four terms needed to read any `busctl` output.

**What's on the slide:**
- **Left:** SERVICE `xyz.openbmc_project.HwmonTempSensor` → OBJECT PATH `/xyz/openbmc_project/sensors/temperature/Inlet_Temp`.
- **Right:** three interfaces on that object, each with example properties.
- **Table:** an analogy for each term.

**In depth:**

| Term | Precise meaning | Example | Analogy |
|---|---|---|---|
| **Service** (bus name) | The name a process claims on the bus | `xyz.openbmc_project.HwmonTempSensor` | A company's phone number |
| **Object path** | A "thing" the service exposes, in a tree | `/xyz/openbmc_project/sensors/temperature/Inlet_Temp` | An extension or department |
| **Interface** | A named, typed **contract**: a set of properties, methods and signals | `xyz.openbmc_project.Sensor.Value` | A standard form everyone knows how to fill in |
| **Property** | A typed value on an interface | `Value = 27.5` (double) | A field on the form |
| **Method** | An action you can call | `Delete()` on a log entry | "Please do this" |
| **Signal** | A broadcast notification | `PropertiesChanged` | An announcement |

- **One object, many interfaces:** the sensor object implements `Sensor.Value`, threshold interfaces and `Association.Definitions` at once. A client uses only the ones it understands.
- **Unique vs well-known names:** each connection gets a **unique name** like `:1.42`; a daemon also claims a **well-known name** like `xyz.openbmc_project.HwmonTempSensor`. Tools show both.
- **Standard interfaces on every object:**
  - `org.freedesktop.DBus.Properties`: `Get`, `GetAll`, `Set` and the `PropertiesChanged` signal. This is how all property reads and writes actually happen.
  - `org.freedesktop.DBus.Introspectable`: describe yourself (returns XML).
  - `org.freedesktop.DBus.ObjectManager` (on a root object): `GetManagedObjects`, plus `InterfacesAdded` / `InterfacesRemoved` signals.
- **Type signatures** (seen in `busctl` output): `s` string, `b` boolean, `i`/`u` 32-bit int, `x`/`t` 64-bit int, `d` double, `o` object path, `a` array, `{}` dictionary entry, `v` variant (any type). Example: `a{sv}` is a dictionary from string to any value.

Live example to show:

```sh
busctl introspect xyz.openbmc_project.HwmonTempSensor \
    /xyz/openbmc_project/sensors/temperature/Inlet_Temp
# NAME                                   TYPE      SIGNATURE RESULT/VALUE
# xyz.openbmc_project.Sensor.Value       interface -         -
# .MaxValue                              property  d         127
# .Unit                                  property  s         "xyz.openbmc_project.Sensor.Value.Unit.DegreesC"
# .Value                                 property  d         27.5
```

**Likely questions:**
- *"Who decides the service name?"* The daemon, at startup. The OpenBMC convention is `xyz.openbmc_project.<Something>`.
- *"Can two services publish the same object path?"* Yes. The path is local to each service. The ObjectMapper (slide 19) tracks which services have which path.

**Transition:** "Object paths follow a predictable tree. Learn it once and you can find anything."

---

## Slide 17: The OpenBMC object namespace

**Purpose:** give a mental map of **where things live** on D-Bus.

**What's on the slide:** the root `/xyz/openbmc_project` branching to sensors, inventory, state, logging, software, and network/user/control, each with example leaves.

**In depth: each branch:**

| Branch | Contents | Typical owner | Example |
|---|---|---|---|
| `sensors/<type>/<name>` | One object per sensor, grouped by type: `temperature`, `voltage`, `current`, `power`, `fan_tach`, `fan_pwm`, `utilization`… | dbus-sensors daemons | `/sensors/voltage/P12V` |
| `inventory/system/...` | Physical parts, nested by containment: system → chassis/board → CPU, DIMM… | entity-manager (or inventory-manager) | `/inventory/system/board/MyBoard` |
| `state/` | `host0`, `chassis0`, `bmc0` (plus `host1`… on multi-host) | phosphor-state-manager or x86-power-control | `/state/host0` |
| `logging/entry/N` | One object per event-log entry | phosphor-logging | `/logging/entry/12` |
| `software/<id>` | One object per firmware image (running or staged) | phosphor-bmc-code-mgmt | `/software/1a2b3c4d` |
| `network/` | Interfaces, IPs, DNS, VLANs | phosphor-networkd | `/network/eth0` |
| `user/` | Local accounts, LDAP config | phosphor-user-manager | `/user/admin` |
| `control/` | Policies and settings: power-restore policy, power cap, boot source, fan mode | settings daemon and others | `/control/host0/power_restore_policy` |
| `led/` | LED groups and physical LEDs | phosphor-led-manager | `/led/groups/enclosure_identify` |
| `time/` | BMC time, NTP mode | phosphor-time-manager | `/time/bmc` |

- **Sensor names** come from configuration (entity-manager JSON `Name`), with spaces replaced by `_`.
- **Inventory paths** mirror physical containment. Redfish uses them to build `Chassis` resources.
- **Older paths:** some legacy code uses `/org/openbmc/...`. Modern code uses `/xyz/openbmc_project/...`.

**Live commands:**

```sh
busctl tree xyz.openbmc_project.EntityManager      # inventory and config objects
busctl tree xyz.openbmc_project.State.Host         # /xyz/openbmc_project/state/host0
```

**Likely questions:**
- *"How do I find everything under /sensors regardless of daemon?"* Ask the ObjectMapper (slide 19) — that's exactly what bmcweb does.

**Transition:** "We've said 'interface' a lot. Who defines what `Sensor.Value` means?"

---

## Slide 18: phosphor-dbus-interfaces — the contract

**Purpose:** show where interfaces are defined, and how one definition becomes code for both sides.

**What's on the slide:**
- **Left:** a YAML snippet of `Sensor/Value.interface.yaml`.
- **Middle:** YAML → `sdbus++` generator → C++ bindings.
- **Right:** server (sensor daemon) and client (bmcweb, ipmid) both use the generated code.
- **Callout:** if two daemons agree on the interface, the implementation can change.

**In depth:**
- **The repository:** `github.com/openbmc/phosphor-dbus-interfaces` holds YAML files under `yaml/xyz/openbmc_project/...`. Each `*.interface.yaml` defines:
  - **properties:** name, type, default, description, and allowed **enum** values (e.g. `Unit` can be `DegreesC`, `Volts`, `Amperes`, `Watts`, `RPMS`…);
  - **methods:** name, parameters, return values, errors they may raise;
  - **signals:** name and arguments.

  Companion `*.errors.yaml` and `*.metadata.yaml` files define error names used by logging.
- **sdbus++:** a code generator in the `sdbusplus` repository. From each YAML file it produces:
  - **server** C++ classes: a daemon inherits one and gets the properties, the `Set` handling and change signals for free;
  - **client** helpers and constants: interface name strings, enum ↔ string conversion;
  - **documentation** (Markdown).
- **sdbusplus:** OpenBMC's C++ library for D-Bus. It wraps systemd's `sd-bus` and has an **asynchronous** (Boost.Asio) API used by most modern daemons and bmcweb.
- **Why this matters:**
  - **Replaceability:** `phosphor-state-manager` and `x86-power-control` both implement `xyz.openbmc_project.State.Host`, so bmcweb works with either without changes.
  - **Single source of meaning:** if you're unsure what `CurrentHostState = Quiesced` means, the YAML description is the authority.
  - **Review gate:** new interfaces go through upstream review, which keeps the API consistent.

**Likely questions:**
- *"Do I have to use C++?"* No. Any language with D-Bus support can implement or call these interfaces (e.g. Python scripts with `busctl`). The YAML is the contract; C++ generation is a convenience.
- *"What about vendor-specific data?"* Vendors can define OEM interfaces in their own namespace, but upstream prefers extending shared interfaces.

**Transition:** "Clients now know *what* an interface means. But how do they find *who* implements it?"

---

## Slide 19: ObjectMapper — the bus directory

**Purpose:** explain how clients **discover** objects instead of hard-coding service names.

**What's on the slide:**
- **Centre:** `xyz.openbmc_project.ObjectMapper`.
- **Bottom:** four services (HwmonTempSensor, FanSensor, PSUSensor, EntityManager) indexed by the mapper (dashed arrows).
- **Top left:** bmcweb asks `GetSubTree(/sensors, Sensor.Value)`.
- **Top right:** example reply mapping path → owning service.
- **Table:** the three main mapper methods.

**In depth:**
- **The problem:** temperatures may come from `HwmonTempSensor`, CPU temperatures from `IntelCPUSensor`, PSU sensors from `PSUSensor`, NVMe from `NVMeSensor`… and the list differs per platform. A client can't hard-code all of them.
- **The solution:** the mapper (repository `phosphor-objmgr`) runs as a service and keeps an **index**: object path → which services own it → which interfaces each implements.
- **How it stays current:** it watches bus signals:
  - `NameOwnerChanged`: a service appeared or disappeared. On a new service, the mapper **introspects** its whole object tree.
  - `InterfacesAdded` / `InterfacesRemoved`: objects added or removed at runtime (e.g. a hot-plugged PSU's sensors).
- **Main methods** (on `/xyz/openbmc_project/object_mapper`, interface `xyz.openbmc_project.ObjectMapper`):

| Method | Input | Returns | Use |
|---|---|---|---|
| `GetObject` | path, interface filter | {service: [interfaces]} | "Who owns this exact path?" |
| `GetSubTree` | root path, depth, interface filter | {path: {service: [interfaces]}} | "All objects under X implementing Y, and their owners" |
| `GetSubTreePaths` | same | [paths] | Same, only the paths |
| `GetAncestors` | path, interface filter | {ancestor path: {...}} | "Which parent objects implement Y?" |

- **Typical client pattern (bmcweb):**
  1. `GetSubTree("/xyz/openbmc_project/sensors", 0, ["xyz.openbmc_project.Sensor.Value"])`
  2. For each (path, service): `GetAll` properties from that service.
  3. Build JSON.

Live example:

```sh
busctl call xyz.openbmc_project.ObjectMapper /xyz/openbmc_project/object_mapper \
  xyz.openbmc_project.ObjectMapper GetSubTree sias \
  /xyz/openbmc_project/sensors 0 1 xyz.openbmc_project.Sensor.Value
```

(`sias` = argument types: string, int, array of strings. `0` = unlimited depth, `1` = one interface follows.)

**Likely questions:**
- *"Doesn't the mapper add latency?"* One extra round-trip per request; it's fast because it answers from memory. Some clients cache results.
- *"A daemon is running but not in the mapper — why?"* It may not have finished starting, may publish objects without proper signals, or its name may be outside the namespaces the mapper indexes. Compare `busctl tree <service>` with a mapper `GetObject`.

**Transition:** "The mapper finds objects, but objects are flat. How do we say 'this sensor belongs to that board'?"

---

## Slide 20: Associations — linking objects together

**Purpose:** explain **associations**, the relationships between objects, and why missing associations hide data from Redfish.

**What's on the slide:**
- A sensor object and an inventory board object, joined by a **forward** link `chassis` (sensor → board) and an automatic **reverse** link `all_sensors` (board → sensor).
- The resulting Redfish URL: `/redfish/v1/Chassis/MyBoard/Sensors/Inlet_Temp`.
- Four other common association uses.

**In depth:**
- **How you declare one:** the owning object implements `xyz.openbmc_project.Association.Definitions` with a property `Associations` of type `a(sss)`, a list of (forward name, reverse name, other endpoint path). For the sensor:

  ```text
  Associations = [ ("chassis", "all_sensors", "/xyz/openbmc_project/inventory/system/board/MyBoard") ]
  ```
- **What the mapper does with it:** it automatically creates two **association objects** implementing `xyz.openbmc_project.Association`, each with an `endpoints` property:
  - `<sensor path>/chassis` → endpoints = [board path]
  - `<board path>/all_sensors` → endpoints = [sensor path, …]

  So you can navigate **both directions** without either daemon knowing about the other.
- **Why Redfish needs it:** bmcweb builds `/redfish/v1/Chassis/<id>/Sensors` by reading the chassis object's `all_sensors` endpoints. A sensor without the association still exists on D-Bus but **doesn't appear under any chassis** in Redfish.
- **Other uses on the slide:**
  - **Sensor ↔ chassis/board:** placing sensors in Redfish.
  - **LED group ↔ inventory item:** "identify this DIMM" lights the right LED.
  - **Log entry ↔ failing part (callout):** an error entry points at the faulty FRU, so Redfish can say *which* part failed and a fault LED can turn on.
  - **Software ↔ device:** which firmware image is running on which component.

**Likely questions:**
- *"How do I check a sensor's associations?"* `busctl get-property <service> <sensor path> xyz.openbmc_project.Association.Definitions Associations`, or look for child paths like `<sensor path>/chassis` in the mapper.
- *"Who adds the association for dbus-sensors?"* The sensor daemon, using the inventory path that entity-manager gave it with the configuration.

**Transition:** "Last D-Bus concept: how do daemons react to each other without calling each other?"

---

## Slide 21: Event-driven patterns — signals and requested state

**Purpose:** show the two patterns used everywhere in OpenBMC.

**What's on the slide:**
- **Left, Pattern 1 (Requested → Current):** a client sets `RequestedHostTransition = On`; the owner does the work; the owner updates `CurrentHostState = Running`.
- **Right, Pattern 2 (one signal, many listeners):** a sensor emits `PropertiesChanged` (`CriticalAlarmHigh = true`); logging, LED manager, fan control and bmcweb each react.
- **Callout:** `busctl monitor <service>`.

**In depth:**

**Pattern 1: request by writing, observe by reading.**
- Actions are expressed as **property writes**, not method calls: `RequestedHostTransition`, `RequestedPowerTransition`, `RequestedBMCTransition`.
- The owning daemon validates the request, starts the work, and **returns immediately**. The work (power sequencing) may take seconds.
- Progress and results appear in **Current\*** properties (`CurrentHostState`, `CurrentPowerState`), each change announced with `PropertiesChanged`.
- **Why:** callers never block waiting for slow hardware. Every client (Redfish, IPMI, the web UI) sees the same state, and the "desired vs actual" distinction is clear.

**Pattern 2: publish/subscribe with signals.**
- A daemon subscribes by registering a **match rule** with the broker, e.g. "PropertiesChanged on any object under `/xyz/openbmc_project/sensors`."
- The broker delivers matching signals to every subscriber. The sender doesn't know how many there are.
- The three signals you'll see most:
  - `PropertiesChanged` (interface `org.freedesktop.DBus.Properties`): property values changed.
  - `InterfacesAdded` / `InterfacesRemoved` (`org.freedesktop.DBus.ObjectManager`): objects appeared or disappeared.
  - `NameOwnerChanged` (from the bus itself): a service started or stopped.
- **Why:** no polling between daemons, instant reactions, and adding a new reaction means adding a listener — the sender doesn't change (shown again on slide 35).

**Asynchronous programming:** a daemon that blocks while waiting stalls everything waiting on it. D-Bus calls have a default timeout (25 seconds in sd-bus). That's why modern OpenBMC daemons use the asynchronous sdbusplus/Boost.Asio API.

**Live command:**

```sh
busctl monitor xyz.openbmc_project.State.Host     # then power on from Redfish and watch
```

**Likely questions:**
- *"What if I write Requested and nothing happens?"* Check the owner's journal. It may reject the transition in the current state, or the platform may not support it.
- *"Can signals be lost?"* A subscriber that isn't running misses signals sent meanwhile. Well-written daemons read the current state at startup (`GetManagedObjects` / `GetAll`) and then follow changes.

**Transition:** "We've covered the backbone. Now let's meet the daemons that plug into it." (Continue in [Part 4](04_Function_Daemons_Slides_22-30.md).)
