# Speaker Guide, Part 6: Build, Port, Debug (Slides 39-45)

[← Part 5](05_Interfaces_and_Flows_Slides_31-38.md) · [Back to Part 1](01_Introduction_Slides_01-08.md)

This is the practical section: how what we've learned turns into work, namely building images, bringing up boards and fixing bugs.

---

## Slide 39: How an image is built — Yocto layers

**Purpose:** show how the OpenBMC image is assembled from layers, generic at the bottom and board-specific at the top.

**What's on the slide:**
- Four layers: `poky / openembedded-core` → `meta-phosphor` → `meta-aspeed / meta-nuvoton` → `meta-<vendor>/meta-<machine>`, each with its content.
- An arrow: more specific layers override lower ones via `.bbappend`.
- A flow: `bitbake obmc-phosphor-image` → `image-bmc / .mtd` → flash to the BMC.

**In depth:**
- **Yocto / OpenEmbedded:** a build system that creates a **custom Linux distribution** from source. **BitBake** is its task engine. **Recipes** (`.bb`) describe how to fetch, configure, compile, install and package one piece of software. **Layers** are folders of recipes and configuration.
- **The four layers:**

| Layer | Provides | Examples |
|---|---|---|
| `poky` / `openembedded-core` (+ `meta-openembedded`) | Toolchain, C library, systemd, BusyBox, OpenSSL, Boost… | Same base as many embedded Linux products |
| `meta-phosphor` | Every common OpenBMC recipe (bmcweb, dbus-sensors, entity-manager, phosphor-*), image classes, flash-layout logic, default policies | Shared by all OpenBMC machines |
| `meta-aspeed` / `meta-nuvoton` | SoC support: U-Boot and kernel recipes/configs, machine include files (e.g. `ast2600.inc`) | One per SoC vendor |
| `meta-<vendor>/meta-<machine>` | Your board: device tree, entity-manager JSON, fan/power configs, which daemons to use, OEM patches | e.g. `meta-<vendor>/meta-<board>` |

- **Overriding without forking:** a **`.bbappend`** file in a higher layer extends a lower layer's recipe, e.g. adding your board's JSON to entity-manager, a kernel config fragment, or a patch. Upstream stays untouched, so updates are easier.
- **Machine configuration** (`conf/machine/<machine>.conf`): the key settings, for example:
  - `require conf/machine/include/ast2600.inc` (the SoC);
  - `KERNEL_DEVICETREE = "aspeed/aspeed-bmc-<vendor>-<board>.dtb"`;
  - the U-Boot configuration and flash size/layout;
  - which implementation provides a function, via `VIRTUAL-RUNTIME_*` / `PREFERRED_PROVIDER_*` variables (e.g. picking x86-power-control as the host state manager). Variable names change between releases; check `meta-phosphor`.
- **Building:**

```sh
git clone https://github.com/openbmc/openbmc && cd openbmc
. setup <machine>                  # selects the machine's layers and creates build/<machine>
bitbake obmc-phosphor-image        # long first build; later builds reuse the shared-state cache
```

- **Outputs** (in `build/<machine>/tmp/deploy/images/<machine>/`), names vary slightly:
  - the **whole-flash image** (`image-bmc` / `*.static.mtd`): every partition in one file, for an external programmer or a full reflash;
  - the **update tarball** (`*.static.mtd.tar` or similar): MANIFEST, signatures and partition images, for Redfish update (slide 29);
  - separate partition images (`image-u-boot`, `image-kernel`, `image-rofs`, `image-rwfs`).
- **Developer workflow:** `devtool modify <recipe>` checks out a recipe's source into a workspace, so you can edit, rebuild and deploy one package without touching layers.

**Going deeper:** [How Yocto works, end to end](../../Yocto_How_It_Works_Flow.md) and the [Yocto build textbook](../../Yocto_BMC_Build_Textbook/00_README.md).

**Likely questions:**
- *"Why does the first build take hours?"* It compiles the toolchain and every package from source. Later builds reuse the **shared-state (sstate) cache** and take minutes. Teams share sstate and download mirrors.
- *"Where's the flash layout decided?"* The machine/distro config (static vs UBI vs eMMC) and the device-tree partitions (slide 9). They must agree.

**Transition:** "With this structure, what does porting OpenBMC to a new board actually involve?"

---

## Slide 40: Porting OpenBMC to a new board

**Purpose:** give a **step-by-step order** for a board port, with what to edit and how to verify each step.

**What's on the slide:** a six-row table: # · Edit · Defines · Verify with. Rule: get each layer right before moving up.

**In depth: each step:**

**Step 1: Device tree (`.dts`)**
- **Edit:** a new `aspeed-bmc-<vendor>-<board>.dts` including the SoC `.dtsi`.
  - Enable UART, FMC and flash partitions, MACs/NC-SI, I2C buses and fixed devices, ADC, PWM/tach, KCS, LPC snoop, video, USB.
  - Name every GPIO line.
- **Verify:** the serial console shows kernel boot; `dmesg` has no probe errors; `ls /sys/bus/i2c/devices`; `cat /sys/class/hwmon/*/name`; `gpioinfo` shows your line names; `ip a` shows the network.
- **Typical problems:** wrong pin mux, 8-bit vs 7-bit I2C address, 0- vs 1-based bus numbers, missing kernel config for a driver.

**Step 2: Machine `.conf` / image**
- **Edit:** the machine config and layer (SoC include, DTB name, U-Boot config, flash layout) and the daemon choices (entity-manager + dbus-sensors? x86-power-control or state-manager?). Add packages to the image.
- **Verify:** the image builds and boots to `BMC Ready`; `busctl list` shows the expected services; `systemctl --failed` is empty.

**Step 3: entity-manager JSON**
- **Edit:** a JSON file for the baseboard (and for each FRU-identified add-in part).
  - **Probe** on the board's FRU fields.
  - **Exposes:** every sensor (type, bus, address, name, thresholds, scaling), fans, PSUs, voltage rails (ADC with scale factors).
- **Verify:** `busctl tree xyz.openbmc_project.EntityManager` shows the board and records; `busctl tree` for each sensor service shows the sensors with sensible values.

**Step 4: Power sequencing**
- **Edit:**
  - **x86-power-control:** its JSON config (GPIO line names for power button out, reset out, power-good in, SIO signals; timing values).
  - **phosphor-state-manager:** systemd units added to the `obmc-chassis-poweron@0.target` and `obmc-host-start@0.target` targets.
- **Verify:** power on, off and cycle via Redfish and `ipmitool`; watch `CurrentPowerState` and `CurrentHostState`; check the host boots (serial console, POST codes); test power-restore policy after an AC cycle.

**Step 5: Fan control JSON**
- **Edit:** phosphor-pid-control zones, inputs, setpoints, PID gains, failsafe percent (often as `Pid`/`Pid.Zone` records in entity-manager JSON).
- **Verify:** fan RPM under idle and full load with thermal engineers; unplug a sensor or fan to confirm failsafe behaviour.

**Step 6: OEM code (only if needed)**
- **Edit:** custom IPMI OEM commands (ipmid providers), bmcweb build options or OEM Redfish properties, platform-specific daemons.
- **Verify:** your test suite, plus the Redfish Service Validator for schema compliance.

**Why this order:** it matches the boot order and the dependency stack. Sensors can't work if the device tree is wrong; Redfish can't show what isn't on D-Bus. Fixing from the bottom up avoids chasing symptoms.

**Likely questions:**
- *"How long does a port take?"* It depends heavily on how similar the board is to an existing upstream machine. Copying a close reference machine's layer is the usual starting point.

**Transition:** "Under all these steps sit a few design principles. Know them and you can predict how OpenBMC handles anything new."

---

## Slide 41: Eight design principles

**Purpose:** summarise the **"why"** behind everything in the talk.

**What's on the slide:** eight numbered principles in two columns.

**In depth: each principle and where it appeared:**

| # | Principle | What it means | Seen on slides |
|---|---|---|---|
| 1 | **D-Bus is the single source of truth** | All state and data live in D-Bus objects; no hidden side channels | 15-21, 37 |
| 2 | **Small daemons, one job each** | Separate processes; crash isolation; independent replacement | 22 |
| 3 | **Interfaces are the contract** | phosphor-dbus-interfaces YAML defines meaning; implementations can be swapped | 18, 27 |
| 4 | **Discover via the mapper, never hard-code** | Clients find owners at runtime; supports hot-plug and alternative daemons | 19, 33 |
| 5 | **Configuration over code** | DTS + entity-manager/fan/power JSON describe boards; little C++ needed | 12, 23, 40 |
| 6 | **Hardware only through kernel drivers** | sysfs, `/dev`, sockets; no direct register access from daemons | 8, 13 |
| 7 | **Async and event-driven** | Requested/Current properties, signals, non-blocking I/O | 21, 34, 35 |
| 8 | **Front ends are translators** | bmcweb and ipmid hold no hardware logic and no cache | 32, 36, 37 |

**How to use them:** when you meet an unfamiliar feature, ask: "Which D-Bus objects does it use? Who owns them? What configures them? Which kernel interface sits underneath?" The principles say those answers must exist.

**Transition:** "Principles also give us a debugging method."

---

## Slide 42: Debugging — follow the data down

**Purpose:** teach the **top-down debugging funnel**: find the first layer where the data is missing or wrong.

**What's on the slide:** five funnel levels (Redfish/IPMI → D-Bus object → Configuration → Daemon/systemd → Kernel/driver), each with its typical failure and next action.

**In depth: each level with its checks:**

| Level | Question | Commands | If it fails here |
|---|---|---|---|
| Redfish / IPMI | Is the value visible and correct? | `curl -k -u user https://<bmc>/redfish/v1/...`, `ipmitool sensor list` | Present on D-Bus but not here → bmcweb mapping or **missing association** |
| D-Bus object | Does the object exist, with the right value? | `busctl tree <svc>`, `busctl introspect <svc> <path>`, mapper `GetObject` | Configuration exists but no object → the daemon failed; read its journal |
| Configuration | Did entity-manager publish the config record? | `busctl tree xyz.openbmc_project.EntityManager` | Missing → Probe didn't match (compare FRU fields) or JSON error (entity-manager journal) |
| Daemon (systemd) | Is the daemon running and healthy? | `systemctl status <unit>`, `journalctl -u <unit> -b`, `systemctl --failed` | Failed or restarting repeatedly → read the error; check dependencies |
| Kernel / driver | Does the kernel see the device? | `dmesg`, `ls /sys/class/hwmon`, `i2cdetect -y <bus>` (careful, see below), `gpioinfo` | No device → DTS (address, bus, status), driver config, wiring, power to the device |

**Worked example: "Inlet temperature missing in Redfish":**
1. Redfish: not under the chassis Sensors. → go down.
2. D-Bus: `busctl tree xyz.openbmc_project.HwmonTempSensor` has no `Inlet_Temp`. → go down.
3. Configuration: entity-manager shows `MyBoard/Inlet_Temp` with `Configuration.TMP75`. ✓ Config is fine.
4. Daemon: `journalctl -u xyz.openbmc_project.hwmontempsensor` says it couldn't find a hwmon device for bus 6, address 0x48.
5. Kernel: `dmesg` shows `lm75 6-0048: probe failed -6` (ENXIO: no device at that address). The schematic shows the chip is at **0x49**, so the JSON `Address` is wrong. **Bug found at the configuration level**, even though it was confirmed at the kernel level.

**Caution about `i2cdetect`:** probing a bus writes or reads at every address, which can upset some devices (e.g. PMBus parts or EEPROMs). On production systems prefer reading known addresses, and only probe buses you understand.

**Transition:** "Here are those commands in one place."

---

## Slide 43: Debug command cheat sheet

**Purpose:** a reference card of **read-only** commands, grouped by layer.

**What's on the slide:** four code boxes: D-Bus; systemd & logs; kernel & hardware; from outside.

**In depth: what each command shows:**

**D-Bus**

| Command | Shows |
|---|---|
| `busctl list` | All services on the bus (well-known and unique names, process, unit) |
| `busctl tree <service>` | The object-path tree a service publishes |
| `busctl introspect <svc> <path>` | Interfaces, properties (with current values), methods and signals on one object |
| `busctl get-property <svc> <path> <iface> <prop>` | One property value |
| `busctl monitor <service>` | Live signals and method calls involving that service (Ctrl-C to stop) |

**systemd & logs**

| Command | Shows |
|---|---|
| `systemctl --failed` | Units that failed to start, or crashed and gave up |
| `systemctl status <unit>` | State, PID, recent log lines, restart count |
| `journalctl -u <unit> -b` | That unit's full log since this boot |
| `journalctl -f` | All logs live (like `tail -f`) |

**Kernel & hardware**

| Command | Shows |
|---|---|
| `dmesg \| grep -i i2c` | Kernel messages about I2C (probe errors, timeouts, NAKs) |
| `ls /sys/class/hwmon/*/name` / `cat .../name` | Which hwmon device belongs to which driver |
| `cat /sys/class/hwmon/hwmon*/temp1_input` | Raw sensor values (millidegrees) |
| `gpioinfo` | Every GPIO line: name, direction, in use by which consumer |

**From outside**

| Command | Shows |
|---|---|
| `curl -k -u <user> https://<bmc>/redfish/v1/...` | The raw Redfish JSON (`-k` skips certificate checks; use only in a lab) |
| `ipmitool -I lanplus -H <bmc> -U <user> sensor list` | IPMI sensor view (only if IPMI-over-LAN is enabled) |

- **Read-only:** none of these change state. Commands that **do** change state (`busctl set-property`, `busctl call`, `systemctl restart`, `gpioset`, `i2cset`) need care and permission on shared systems.
- **Platform differences:** service and unit names vary. Start with `busctl list` and `systemctl list-units`.
- **Tools may be missing on production images:** `gpioinfo`, `i2c-tools` or `dtc` may not be installed. They're typically in debug or development image variants.

**Transition:** "Let's wrap up with five things to remember."

---

## Slide 44: Key takeaways

**Purpose:** five messages the audience should leave with.

**What's on the slide:** five numbered points.

**In depth: how to say each one:**
1. **Independent computer:** "The BMC is its own computer on standby power. It manages the host and works even when the host is dead."
2. **Layers:** "Flash → boot → kernel → systemd → D-Bus → daemons → Redfish/IPMI. Every problem lives in one of these layers."
3. **D-Bus is the heart:** "Daemons publish objects, the mapper finds them, and signals drive reactions. Learn `busctl`; it's your most important tool."
4. **Configuration over code:** "Boards are described by device tree and JSON. Most board work is configuration."
5. **Debug top-down:** "Follow the data down the layers. The first layer where it's wrong is where the bug is."

**Suggested close:** "Next time something is missing in Redfish, don't start with bmcweb's code. Start with `busctl tree`."

---

## Slide 45: Questions?

**Purpose:** open Q&A and point to the best references.

**What's on the slide:** five upstream repositories (on github.com/openbmc) with what each is good for.

**In depth: why each reference:**

| Repository | Why read it |
|---|---|
| `docs` | Architecture and design documents, coding guidelines, GPIO naming, sensor and Redfish design notes |
| `phosphor-dbus-interfaces` | The authoritative meaning of every D-Bus interface and property (the YAML) |
| `entity-manager` · `dbus-sensors` | How boards and sensors are configured; JSON examples for many real boards |
| `bmcweb` | How each Redfish URL is built from D-Bus; read the handler for a URL you're debugging |
| `openbmc` (meta-layers) | The Yocto layers and machine configs of every upstream platform; find one similar to yours |

**Questions you may get, with short answers:**

- *"How does OpenBMC compare to commercial BMC firmware?"* Same functions, but open, modular and inspectable. Vendors build products on it and add their own features and support.
- *"How do I start contributing?"* Pick a small bug or documentation fix. Upstream uses Gerrit for code review (see the `docs` repository's contributing guide).
- *"Can I run OpenBMC without hardware?"* Yes. Some machines build images that boot in **QEMU** (ASPEED machine models), which is useful for learning D-Bus, Redfish and the build flow.
- *"Where do I learn D-Bus hands-on?"* Boot a QEMU image and run every command on slide 43.

---

## Appendix A: Rehearsal checklist

- [ ] Rebuild the deck with PowerPoint **closed** (`& ".\.venv\Scripts\python.exe" ".\OpenBMC_Presentation\build_deck.py"`) so the slide 9 and slide 34 corrections apply. **This overwrites any edits you made in PowerPoint**; otherwise make those two changes by hand.
- [ ] Fill in presenter and date on slide 1.
- [ ] If you can, prepare a live demo on a lab BMC or QEMU: `busctl tree`, `busctl monitor` while powering on, a Redfish `curl`.
- [ ] Replace generic names with your platform's real ones where your team will recognise them (service names, board names).
- [ ] Time yourself: aim for about 60 minutes with Q&A. If short on time, shorten slides 8, 17, 36 and 43 (reference tables; say "use this later").

## Appendix B: Glossary

| Term | Meaning |
|---|---|
| **BMC** | Baseboard Management Controller: the separate management computer on the server board |
| **SoC** | System-on-chip: CPU cores plus peripherals in one chip (e.g. ASPEED AST2600) |
| **FRU** | Field Replaceable Unit; also the EEPROM data identifying it |
| **PGOOD** | Power-good signal: rails are stable |
| **KCS** | Keyboard Controller Style: a mailbox interface for in-band IPMI |
| **eSPI / LPC** | Host ↔ BMC buses carrying KCS, POST codes, virtual UART |
| **PECI / APML** | Intel / AMD interfaces for reading CPU temperatures and errors |
| **NC-SI** | Sideband interface letting the BMC share the host's NIC |
| **FIT** | U-Boot's signed container for kernel + DTB + initramfs |
| **DTS / DTB** | Device tree source / compiled binary describing the board's hardware |
| **squashfs / JFFS2** | Read-only compressed filesystem / flash-friendly writable filesystem |
| **overlayfs** | Merges a read-only lower layer and a writable upper layer into one view |
| **hwmon** | Linux hardware-monitoring subsystem (standard sensor files in sysfs) |
| **D-Bus** | Linux message bus used for inter-process communication |
| **ObjectMapper** | OpenBMC service indexing which service owns which D-Bus objects |
| **Association** | A named, two-way link between D-Bus objects |
| **entity-manager** | JSON-driven daemon publishing inventory and configuration objects |
| **PID control** | Feedback control (proportional, integral, derivative) used for fans |
| **IPMI / RMCP+** | Older management protocol / its authenticated LAN transport (UDP 623) |
| **MCTP / EID** | Management transport between components / endpoint ID |
| **PLDM / PDR** | Platform Level Data Model / its Platform Descriptor Records |
| **Redfish** | DMTF's modern RESTful (HTTPS + JSON) management API |
| **SOL / KVM** | Serial over LAN / remote keyboard, video and mouse |
| **Yocto / BitBake / recipe / layer** | Build system / its task engine / build instructions for one package / a group of recipes |
