# Speaker Guide, Part 4: Function Daemons (Slides 22-30)

[← Part 3](03_DBus_Backbone_Slides_15-21.md) · [Part 5 →](05_Interfaces_and_Flows_Slides_31-38.md)

The goal in this section: for each job from slide 4, show **which daemon** does it and **which D-Bus objects** it publishes.

---

## Slide 22: The daemon map

**Purpose:** give an overview of the daemons in a typical image, grouped by job.

**What's on the slide:** ten tiles (job + daemon/repository names) and a purple bar: "All of them publish and consume objects on the D-Bus system bus."

**In depth: each tile:**

| Job | Daemons / repositories | What they do | Detail on slide |
|---|---|---|---|
| Inventory & config | `entity-manager`, `fru-device` **or** `phosphor-inventory-manager` | Detect parts, publish inventory and configuration objects | 23 |
| Sensors | `dbus-sensors` (one daemon per sensor type) **or** `phosphor-hwmon` | Read kernel sensor files, publish `/sensors/...` objects with thresholds | 24-25 |
| Fan control | `phosphor-pid-control` (`swampd`), `phosphor-fan-presence` | Closed-loop fan speed; fan presence and fault detection | 26 |
| Power & state | `phosphor-state-manager` **or** `x86-power-control` | Host/chassis/BMC state and power sequencing | 27 |
| Logging | `phosphor-logging`, `phosphor-sel-logger` | Event-log entries; IPMI SEL records | 28 |
| Firmware update | `phosphor-bmc-code-mgmt` | Verify, stage and activate firmware images | 29 |
| Host protocols | `ipmid`, `kcsbridged`, `netipmid`, `pldmd`, `mctpd` | IPMI in-band and over LAN; MCTP and PLDM | 30 |
| Remote access | `obmc-console`, `obmc-ikvm`, virtual media | Serial console, KVM, ISO mounting | 31 |
| Network, users, time | `phosphor-networkd`, `phosphor-user-manager`, `phosphor-time-manager` | IP config, accounts and roles, NTP/manual time | — |
| LEDs, buttons, dumps | `phosphor-led-manager`, `phosphor-buttons`, `phosphor-debug-collector` | LED groups, front-panel buttons, debug dumps | — |

- **"or" means alternatives:** two implementations of the **same D-Bus interfaces**; each platform picks one. Rough split:
  - **entity-manager + dbus-sensors + x86-power-control:** common on Intel/AMD x86 server platforms; dynamic, JSON-driven.
  - **phosphor-inventory-manager + phosphor-hwmon + phosphor-state-manager:** older static/YAML-driven style, common on IBM POWER platforms.

  Mixes exist.
- **Why so many small daemons:** a crash in one (e.g. a PSU sensor daemon) doesn't affect others; systemd restarts it; each can be updated, tested and replaced on its own.
- **How to see what *your* image runs:** `busctl list | grep xyz.openbmc_project` and `systemctl list-units 'xyz.openbmc_project*'`.

**Transition:** "Let's start with how the BMC learns what hardware it has: entity-manager."

---

## Slide 23: entity-manager — hardware described as data

**Purpose:** explain **configuration-driven** hardware support: Probe decides *when* a config applies; Exposes says *what* is on the board.

**What's on the slide:**
- **Left:** simplified JSON with `Name`, `Probe` (match on FRU product name) and `Exposes` (a TMP75 sensor and a fan).
- **Right:** four steps: fru-device reads EEPROMs → entity-manager matches the Probe → publishes `Configuration.TMP75` → the sensor daemon creates the sensor.
- **Callout:** it also publishes inventory objects used by Redfish.

**In depth:**
- **fru-device:**
  - scans I2C buses for **FRU EEPROMs** (often addresses 0x50-0x57) and parses the IPMI FRU format: board manufacturer, product name, part number, serial number;
  - publishes one object per FRU under `/xyz/openbmc_project/FruDevice/...`, with properties like `BOARD_PRODUCT_NAME`, `BOARD_SERIAL_NUMBER`, plus `BUS` and `ADDRESS`.
- **entity-manager:**
  - loads every JSON file in `/usr/share/entity-manager/configurations/`;
  - for each file, evaluates its **Probe**, a match expression over D-Bus data such as `xyz.openbmc_project.FruDevice({'BOARD_PRODUCT_NAME': 'MyBoard'})`. Probes can be combined with `AND`/`OR`; `"TRUE"` always matches;
  - when a probe matches, publishes:
    - an **inventory object** for the entity, e.g. `/xyz/openbmc_project/inventory/system/board/MyBoard`, with `Inventory.Item.Board` and asset properties copied from the FRU;
    - one **Configuration object** per `Exposes` record, as a child of that inventory object, with interface `xyz.openbmc_project.Configuration.<Type>` (e.g. `Configuration.TMP75`). Its properties are exactly the JSON fields (`Name`, `Bus`, `Address`, `Thresholds`…).
- **Consumers:** each sensor daemon watches for the Configuration types it handles. `hwmontempsensor` handles `TMP75`, `TMP421` and others; `adcsensor` handles `ADC`; `fansensor` handles `AspeedFan`, `I2CFan`… When a new one appears (`InterfacesAdded`), it creates the sensor (slide 24).
- **Templates:** JSON can use values from the matched FRU, e.g. `"Bus": "$bus"`. One config file then works for the same card in different slots.
- **Hot-plug:** when a PSU or riser is inserted, its FRU appears, its Probe matches and its sensors appear. Removed hardware disappears the same way.

**The DTS vs JSON rule:** devices that are always present and fixed may be described in the device tree. Devices that vary go in JSON. **Never both for the same I2C address**: the second attempt to bind a driver fails ("address busy") and the sensor silently disappears.

**Likely questions:**
- *"How do I check whether my config was applied?"* `busctl tree xyz.openbmc_project.EntityManager` should show your board and its `Exposes` records. If not, the Probe didn't match. Compare with `busctl introspect xyz.openbmc_project.FruDevice <fru path>`.
- *"Where's the JSON schema?"* In the entity-manager repository (`schemas/`). Configs are validated at build time.

**Transition:** "Let's follow one sensor from FRU to D-Bus value."

---

## Slide 24: Sensor lifecycle — from FRU to D-Bus value

**Purpose:** show **who does what, in order**, for one sensor.

**What's on the slide:** a sequence diagram with five participants (fru-device, entity-manager, hwmontempsensor, Linux kernel, ObjectMapper) and seven messages.

**In depth: each arrow:**

1. **fru-device → entity-manager: "FRU data on D-Bus."** EEPROM contents are published as properties.
2. **entity-manager (self): "Probe matches JSON."**
3. **entity-manager → hwmontempsensor: "Configuration.TMP75 {Bus, Address}."** The configuration object appears; the sensor daemon receives `InterfacesAdded`.
4. **hwmontempsensor → kernel: "bind driver (new_device)."** If no driver is bound at that address yet, the daemon asks the kernel to create the I2C device by writing `tmp75 0x48` to `/sys/bus/i2c/devices/i2c-6/new_device`. The kernel then probes the `lm75` driver.
5. **kernel → hwmontempsensor: "hwmonN/temp1_input."** The driver registers a hwmon device. The daemon finds the right `hwmonN` by matching the bus and address in sysfs.
6. **hwmontempsensor → ObjectMapper: "publish /sensors/temperature/Inlet_Temp."** The daemon creates the D-Bus object with `Sensor.Value`, threshold interfaces, associations and status interfaces. The mapper indexes it.
7. **hwmontempsensor (loop): "read sysfs, update Value, check thresholds."** Polled every poll interval (configurable, typically around a second). It converts millidegrees to degrees, updates `Value` (emitting `PropertiesChanged`), and evaluates thresholds.

- **Extra interfaces you'll see on a sensor:**
  - `xyz.openbmc_project.State.Decorator.Availability` (`Available`): is the sensor readable right now?
  - `xyz.openbmc_project.State.Decorator.OperationalStatus` (`Functional`): is it healthy?
- **Power-state awareness:** many sensors (e.g. CPU or VR sensors) can only be read when the host is on. Config option `PowerState: "On"` makes the daemon skip reading, and suppress threshold alarms, while the host is off.
- **Failure modes and where they appear:**

| Fails at step | Symptom | Check |
|---|---|---|
| 1 | No FRU object | `busctl tree xyz.openbmc_project.FruDevice`; EEPROM wiring and address |
| 2 | No board in EntityManager | Probe string vs actual FRU fields |
| 4-5 | Config exists, no sensor | Daemon journal; `dmesg` for driver errors; DTS conflict |
| 7 | Value stuck or NaN | Device stopped responding; `Available = false`; I2C errors in `dmesg` |

**Transition:** "Let's look inside one sensor object at its thresholds."

---

## Slide 25: Inside a sensor — value and thresholds

**Purpose:** explain thresholds, alarms and hysteresis.

**What's on the slide:**
- A coloured band: Critical low | Warning low | Normal | Warning high | Critical high, with example limits 5 / 10 / 85 / 95 °C and a current value of 27.5.
- A table of properties and the interfaces they're on.
- Bullets: crossing → alarm → signal → reactions; hysteresis.

**In depth:**
- **Threshold interfaces:**
  - `xyz.openbmc_project.Sensor.Threshold.Warning`: `WarningHigh`, `WarningLow`, `WarningAlarmHigh`, `WarningAlarmLow`.
  - `xyz.openbmc_project.Sensor.Threshold.Critical`: `CriticalHigh`, `CriticalLow`, `CriticalAlarmHigh`, `CriticalAlarmLow`.
  - Others exist for special uses (e.g. `HardShutdown`, `SoftShutdown`, `PerformanceLoss`).
- **Alarm logic:** when `Value` crosses a limit, the matching `*Alarm*` property becomes `true` and a `PropertiesChanged` signal is sent. When the value returns inside the limit (minus hysteresis), it becomes `false` again, with another signal.
- **Hysteresis:** without it, a value hovering at 95.0 ↔ 94.9 would toggle the alarm every poll, flooding logs and events. With e.g. 2 °C hysteresis, the alarm asserts at 95 but only clears below 93.
- **Where limits come from:** the `Thresholds` array in entity-manager JSON (or YAML/config for phosphor-hwmon). Each entry has `Direction` (greater/less than), `Severity` (0 = warning, 1 = critical…), `Value`, and optionally `Hysteresis`. Some sensors read limits from the device itself.
- **Changing limits at runtime:** threshold properties are often writable (e.g. via IPMI "set sensor thresholds" or Redfish), and some daemons write the new value back to the configuration.
- **Who reacts to alarms** (slide 35): logging (event entry), LED manager (fault LED), fan control (raise speed), bmcweb (Redfish event), SEL logger (IPMI SEL), and optionally a shutdown policy.

**Likely questions:**
- *"Are the numbers on the slide real?"* No — examples. Real limits come from component datasheets and thermal engineering.
- *"What are MaxValue/MinValue?"* The sensor's measurement **range** (for scaling, IPMI SDRs and UI gauges), not alarm limits.

**Transition:** "One of the most important consumers of temperature data is fan control."

---

## Slide 26: Fan control — a closed loop

**Purpose:** explain fan control as a **feedback loop**: sensors in, PWM out.

**What's on the slide:** Temperature sensors → Thermal PIDs (per zone) → Max demand → RPM setpoint → Fan PID → PWM → Fans → Tach feedback back to the fan PID. Callouts for failsafe and JSON configuration.

**In depth:**
- **PID controller:** a standard control algorithm. It looks at the error (setpoint − measurement) and outputs a correction from three terms:
  - **P**roportional: the bigger the error, the bigger the correction;
  - **I**ntegral: removes a persistent small error;
  - **D**erivative: reacts to how fast the error changes (often unused in fan control).
- **Two-level structure in phosphor-pid-control (`swampd`):**
  1. **Thermal controllers:** one per temperature input (or group). Each compares temperature (or *margin*, i.e. how far below the limit it is) with a setpoint and outputs a **fan speed demand** (RPM or %).
  2. **Zone:** a set of fans cooling the same area. It takes the **maximum** of all thermal demands — the hottest component wins.
  3. **Fan controllers:** compare the demanded RPM with actual tach RPM and output a **PWM duty cycle**.
- **Feedback:** fans speed up → temperatures fall → thermal demand falls → fans slow down. It stabilises where cooling matches heat.
- **Failsafe:** if a temperature sensor in a zone is **missing, failed or unreadable**, the controller can't trust its inputs, so it sets fans to a configured **failsafe percent** (high). Loud, but safe. Diagnose by looking for a sensor with `Available = false` or a stale value.
- **Configuration:** JSON (either swampd's own config file or `Pid`/`Pid.Zone`/`Stepwise` records in entity-manager): zones, inputs, setpoints, PID gains, min/max outputs, failsafe percent.
- **Stepwise controllers:** an alternative to PID; a lookup table ("above 40 °C → 50 %"), simpler but less smooth.
- **Fan presence/fault:** `phosphor-fan-presence` detects missing fans (tach = 0 or presence GPIO) and can mark fans non-functional, raising events and LEDs.
- **Manual mode:** a control property lets tests or OEM commands put a zone in manual mode and set PWM directly. Remember to return it to automatic.

**Likely questions:**
- *"Why are fans loud right after BMC boot?"* Failsafe until all sensors are available, or until host-dependent sensors start once the host is on.
- *"Who tunes the PID gains?"* Thermal engineers, per chassis, from thermal testing.

**Transition:** "Now power: how does 'power on' actually happen?"

---

## Slide 27: Power and state management

**Purpose:** explain the three state objects and how power transitions are requested and observed.

**What's on the slide:**
- The host-state cycle: Off → TransitioningToRunning → Running → TransitioningToOff → back to Off.
- A table of the three objects: what to write to request a change, and what to read for the result.
- The two implementations: phosphor-state-manager (systemd targets) vs x86-power-control (GPIOs directly).

**In depth:**

| Object | Concept | Request property → values | Current property → values |
|---|---|---|---|
| `/xyz/openbmc_project/state/chassis0` | **Electrical power** to the main board | `RequestedPowerTransition` → `On`, `Off`, `PowerCycle` | `CurrentPowerState` → `On`, `Off`, `TransitioningToOn`/`Off` |
| `/xyz/openbmc_project/state/host0` | **Software on the host CPUs** (firmware/OS) | `RequestedHostTransition` → `On`, `Off`, `Reboot`, `GracefulWarmReboot`, `ForceWarmReboot` | `CurrentHostState` → `Off`, `Running`, `TransitioningToRunning`, `TransitioningToOff`, `Quiesced`, `DiagnosticMode`… |
| `/xyz/openbmc_project/state/bmc0` | **The BMC itself** | `RequestedBMCTransition` → `Reboot`, `HardReboot` | `CurrentBMCState` → `Ready`, `NotReady`, `UpdateInProgress`, `Quiesced` |

- **Chassis vs host:** chassis is "is electricity flowing?"; host is "is the computer running?" Host `On` implies chassis `On` first. Chassis can be `On` while the host is `Off` (e.g. halted in firmware).
- **Quiesced:** the host hit an error and is stopped in a safe state for debugging. **DiagnosticMode:** the host is collecting a crash dump.
- **phosphor-state-manager:** maps requests to **systemd targets** (`obmc-host-start@0.target` etc., slide 14). Each platform adds its power-sequencing units to those targets. Common on IBM/POWER and some Arm platforms.
- **x86-power-control:** a single daemon with its own internal state machine. It reads a JSON config naming the GPIO lines and timings, e.g. power-button output, reset output, power-good input, SIO S5 input, and how long to "press" the button. It "presses" the button by pulsing a GPIO, watches power-good, and handles the front-panel power/reset/NMI buttons. Common on Intel and AMD x86 platforms.
- **Policies around power** (in `control/` objects):
  - **Power-restore policy** (`AlwaysOn`, `AlwaysOff`, `Restore`): what to do after AC power returns.
  - **Restart cause:** why the host last powered on.
  - **Boot options:** boot source override (PXE, disk, BIOS setup).

**Likely questions:**
- *"Redfish says On, but the server isn't booting."* Chassis power may be on while host firmware is stuck. Check `CurrentHostState`, BIOS POST codes (port-80 snoop) and the host serial console.
- *"How do I know which implementation my platform uses?"* `busctl status xyz.openbmc_project.State.Host` and look at the process name, or `systemctl list-units | grep -E 'power-control|state-manager'`.

**Transition:** "When things go wrong, we need to record it. Logging."

---

## Slide 28: Logging and events

**Purpose:** show how a fault becomes a D-Bus **log entry** that every interface can see, and the difference between log entries and the journal.

**What's on the slide:** any daemon → phosphor-logging → `/logging/entry/N` → Redfish LogServices + EventService, IPMI SEL, fault LED via association. The systemd journal is shown separately. Callout: "Entry = what happened. Journal = why."

**In depth:**
- **Two kinds of logs:**

| | Log **entry** (`/xyz/openbmc_project/logging/entry/N`) | **Journal** (`journalctl`) |
|---|---|---|
| Audience | Operators, management tools | Developers |
| Content | Structured: Severity, Message (event ID), Timestamp, AdditionalData, Resolved flag, associations (callouts) | Free-form text and debug lines from every process |
| Visible via | Redfish, IPMI, Web UI | Only on the BMC shell (or a dump) |
| Persistence | Saved to flash (`rwfs`), capped count | RAM by default; lost on reboot |

- **How a daemon creates an entry:** via phosphor-logging's API (the structured `lg2` logging plus error/event definitions from YAML), or a D-Bus `Create` call on the logging service. Each entry is a D-Bus object with interfaces like `xyz.openbmc_project.Logging.Entry`, plus `Association.Definitions` for callouts.
- **Severity levels:** Emergency, Alert, Critical, Error, Warning, Notice, Informational, Debug.
- **Callouts:** an association from the entry to the faulty inventory item. Enables "replace DIMM A3" in Redfish and lights that part's fault LED.
- **Resolved:** operators mark entries resolved (a property write); a daemon may resolve its own when the condition clears.
- **Redfish:** entries appear under `/redfish/v1/Systems/system/LogServices/EventLog/Entries`, and bmcweb can push new ones to EventService subscribers. Some platforms have bmcweb build the Redfish event log from **journal messages with Redfish message IDs** rather than D-Bus entries — a build option; know which yours uses.
- **IPMI SEL:** `phosphor-sel-logger` turns threshold and other events into IPMI SEL records, so `ipmitool sel list` shows them.
- **Capacity:** the entry count is capped. When full, oldest entries are removed or new ones rejected depending on configuration. Watch for floods (e.g. a flapping sensor without hysteresis).

**Likely questions:**
- *"How do I see all entries on the BMC?"* `busctl tree xyz.openbmc_project.Logging`, then `busctl introspect` one entry.
- *"How do I see why a daemon logged an error?"* `journalctl -u <daemon> -b`, around the entry's timestamp.

**Transition:** "Firmware update is the riskiest thing a BMC does. Let's see how it's made safe."

---

## Slide 29: Firmware update flow

**Purpose:** walk the update pipeline: upload → verify → publish → activate → reboot, and explain A/B images.

**What's on the slide:** a five-step flow, a table of Software object properties, Image A (running) / Image B (being written), and a warning about power loss.

**In depth: each step:**
1. **Upload:** the client POSTs the image to Redfish `UpdateService` (multipart upload in current bmcweb), or copies it to the BMC. It's saved to a temporary directory (e.g. `/tmp/images`).
2. **Verify:** `phosphor-bmc-code-mgmt` unpacks the tarball:
   - checks the **MANIFEST** (purpose, version, machine name, so you can't flash the wrong board);
   - with signing enabled, verifies the **signatures** of the manifest, the included public key and each image file against keys already on the BMC.

   A failure gives `Activation = Invalid`/`Failed` and an error log entry.
3. **Software object:** `/xyz/openbmc_project/software/<id>` appears (the ID is derived from the version) with:
   - `xyz.openbmc_project.Software.Version`: `Version`, `Purpose` (`BMC`, `Host`, `PSU`, `System`, `Other`);
   - `xyz.openbmc_project.Software.Activation`: `Activation` (`Ready`, `Activating`, `Active`, `Failed`…) and `RequestedActivation` (write `Active` to start);
   - `xyz.openbmc_project.Software.RedundancyPriority`: `Priority` (0 = boots next) on multi-image systems.
4. **Activate:** writes the flash.
   - **Single image (static layout):** files are staged in RAM; the actual write happens during the **next BMC reboot**, after the filesystems are unmounted, by the initramfs `update` script.
   - **Dual image (UBI/eMMC, A/B):** the **inactive** side is written while the BMC keeps running, then `Priority` makes it the next boot.
5. **Reboot:** the BMC boots the new image. On A/B systems, if the new image fails to boot (watchdog or boot counter), U-Boot falls back to the old side.

- **Newer API:** recent OpenBMC releases add a `Software.Update` interface with a `StartUpdate` method, so one code path serves many device types. Check which interfaces your release uses.
- **Other firmware:** the same model updates **host BIOS** (via the BMC's SPI1/mux to the BIOS flash), **PSU**, **CPLD**, retimers, or **PLDM devices** (slide 30); `Purpose` distinguishes them.
- **The warning:** on single-image systems, power loss during the flash write can leave a half-written partition and an unbootable BMC. Recovery paths: dual-flash fallback, a root-of-trust/PFR restore, or an external programmer.

**Likely questions:**
- *"Are my settings kept after update?"* Normally yes. `rwfs` (the overlay upper layer) is preserved unless a factory reset is requested.
- *"Who signs images?"* The vendor, at build time, with a private key (`SIGNING_KEY` in Yocto). Upstream defaults to a public **insecure test key**; production must use its own protected key.

**Transition:** "Some of the most important messages come from the host itself. Let's see the host protocols."

---

## Slide 30: Talking to the host — IPMI, MCTP, PLDM

**Purpose:** show the three host-facing protocol paths and that all of them end on D-Bus.

**What's on the slide:**
- **Row 1 (in-band IPMI):** BIOS/host OS (`ipmitool`) → KCS/BT → `kcsbridged` → `ipmid` + command providers → D-Bus.
- **Row 2 (out-of-band IPMI):** remote admin (`ipmitool -I lanplus`) → `netipmid` (RMCP+, UDP 623) → `ipmid`.
- **Row 3 (MCTP/PLDM):** NIC, GPU, drives, host firmware → MCTP over I2C/I3C or PCIe → `mctpd` (assigns endpoint IDs) → `pldmd` (sensors, firmware update).

**In depth:**

**IPMI (Intelligent Platform Management Interface)**: the older, widely supported standard.
- **Messages:** NetFn (function group) + Cmd (command) + data, e.g. NetFn Chassis / Cmd "Chassis Control" = power on/off.
- **In-band path:** the host writes a request into the **KCS** mailbox (I/O ports such as 0xCA2/0xCA3) over eSPI/LPC. The kernel's KCS driver delivers it to `/dev/ipmi-kcsN`. `kcsbridged` reads it and forwards it on D-Bus to `ipmid`, then returns the response.
- **Out-of-band path:** `netipmid` (one instance per network interface) implements **RMCP+** (IPMI 2.0 over UDP port 623): session setup, authentication, encryption. It also carries **SOL** (Serial over LAN), connecting to `obmc-console`.
- **ipmid and providers:** `ipmid` loads **provider libraries** at startup. Each registers handlers for NetFn/Cmd pairs (standard commands, plus OEM commands, e.g. Intel's `intel-ipmi-oem`). Handlers read and write D-Bus: "Get Sensor Reading" reads `Sensor.Value`; "Chassis Control" writes `RequestedHostTransition`.
- **SDRs:** IPMI describes sensors with Sensor Data Records. OpenBMC builds them **dynamically** from D-Bus sensors (with dbus-sensors setups), so new sensors automatically appear in `ipmitool sdr`.

**MCTP (Management Component Transport Protocol)**: the modern transport.
- Carries management messages between components (BMC, NICs, GPUs, NVMe drives, host CPUs) over **I2C/I3C, PCIe VDM** or other bindings.
- Each component has an **EID** (endpoint ID). The BMC usually acts as **bus owner**: `mctpd` discovers endpoints and assigns EIDs with MCTP control messages.
- Linux has native MCTP networking (`AF_MCTP` sockets), so apps send messages to an EID like using a network socket.
- `mctpd` publishes discovered endpoints on D-Bus, so other daemons can find them.

**PLDM (Platform Level Data Model)**: a message family carried over MCTP.
- **Type 0, base:** discover which PLDM types and commands a device supports.
- **Type 2, monitoring & control:** the device describes its sensors and controls in **PDRs** (Platform Descriptor Records). `pldmd` reads them and publishes the sensors on D-Bus, so they appear in Redfish like any other sensor.
- **Type 4, FRU:** inventory data.
- **Type 5, firmware update:** a standard way to update NIC/GPU/device firmware. The BMC acts as the update agent.

**The rule on the slide:** every protocol ends at D-Bus objects. An IPMI "Get Sensor Reading" and a Redfish GET read the **same** `Sensor.Value`.

**Going deeper:** [MCTP textbook](../../MCTP_Textbook/00_README.md) and [PLDM textbook](../../PLDM_Textbook/00_README.md) in this library.

**Likely questions:**
- *"Is IPMI going away?"* Redfish is the modern replacement for management, and IPMI-over-LAN is often disabled for security. In-band IPMI via KCS remains widely used by BIOS and OS tools.
- *"Why MCTP when we have I2C?"* I2C is just wires. MCTP adds addressing, message types, fragmentation and discovery on top, and works the same over I2C, I3C and PCIe.

**Transition:** "Besides protocols, the BMC lets you sit at the server remotely: console, KVM, virtual media." (Continue in [Part 5](05_Interfaces_and_Flows_Slides_31-38.md).)
