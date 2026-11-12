# Speaker Guide, Part 5: External Interfaces and End-to-End Flows (Slides 31-38)

[← Part 4](04_Function_Daemons_Slides_22-30.md) · [Part 6 →](06_Build_Port_Debug_Slides_39-45.md)

This section brings everything together. The three flow slides (33-35) are where the audience sees all the layers working at once, so give them time.

---

## Slide 31: Remote access — console, KVM, virtual media

**Purpose:** show the three features that replace a physical visit to the server.

**What's on the slide:** three rows (serial console, graphical KVM, virtual media). Each shows the host-side hardware path and how the user reaches it.

**In depth:**

### Serial console (Serial over LAN, SOL)
- **Hardware:** the host's serial port (UART) is wired to a BMC UART. The host BIOS and OS print boot messages and a login prompt on it.
- **Software:** `obmc-console-server` owns that UART and shares it through a local socket, so several viewers can watch at once.
- **How users reach it:**
  - **SSH to port 2200** on the BMC connects straight to the host console;
  - the **Web UI** console page (a bmcweb WebSocket);
  - **IPMI SOL** via `netipmid` (`ipmitool -I lanplus ... sol activate`).
- **Console log:** the server keeps a log of recent console output on the BMC, useful to see what the host printed before a crash.

### Graphical KVM (keyboard, video, mouse)
- **Video:** the BMC contains a **VGA controller** that the host sees as its graphics card (over PCIe). The BMC's **video engine** captures and compresses that frame buffer (JPEG-style). Linux exposes it as a **V4L2** device (`/dev/video0`, `aspeed-video` driver).
- **Keyboard/mouse:** the BMC acts as a **USB HID device** (a "gadget", set up through configfs) plugged into the host. Keystrokes from the browser become real USB keyboard input to the host.
- **Software:** `obmc-ikvm` reads frames from V4L2, serves them over the **VNC/RFB** protocol, and injects input into the HID gadget. bmcweb proxies a browser **WebSocket** to it, so the Web UI shows the screen.
- **Requirement:** the host must use the BMC's VGA as its display. If a discrete GPU drives the screen instead, KVM shows nothing useful.

### Virtual media
- The BMC acts as a **USB mass-storage gadget**; the host sees a USB CD/DVD or disk.
- **Proxy mode:** the ISO stays on the administrator's PC. The browser streams blocks through bmcweb (WebSocket) to an NBD (network block device) server on the BMC, which backs the USB gadget.
- **Legacy (remote-share) mode:** the BMC itself mounts an image from a network location (e.g. HTTPS or CIFS) and serves it.
- **Typical use:** install an OS or run a recovery ISO without anyone touching the server.

**Likely questions:**
- *"KVM is black or says 'no signal'."* The host may be off, using another GPU, or in a video mode the engine doesn't support. Check the host's power state and BIOS video settings.
- *"Is the console log persistent?"* Only as configured. Many platforms keep it in RAM or rotate a small file.

**Transition:** "All of these, plus Redfish and the Web UI, go through one front door: bmcweb."

---

## Slide 32: bmcweb — the front door

**Purpose:** explain bmcweb's request pipeline and that it is a **translator** with no hardware logic.

**What's on the slide:**
- A six-step pipeline: TLS → Authenticate → Route URL → Privilege check → Handler (async D-Bus) → JSON response, with a detail card under each.
- Three services it provides: Redfish, Web UI, WebSockets.
- Callout: bmcweb is a translator.

**In depth:**
- **What it is:** a single C++ program (using Boost.Beast/Asio for HTTP and asynchronous I/O) listening on HTTPS port 443. It is compact and fast, suited to a small BMC.
- **Pipeline:**
  1. **TLS:** HTTPS only. The server certificate is managed as a D-Bus object (self-signed on first boot; replace it via Redfish `CertificateService`).
  2. **Authentication:**
     - **Basic auth:** username/password on each request.
     - **Session token:** POST to `/redfish/v1/SessionService/Sessions`, get an `X-Auth-Token` header, reuse it.
     - **Cookie + CSRF token:** used by the Web UI.
     - **mTLS:** a client certificate mapped to a user.

     Passwords are checked through **PAM** against local accounts or LDAP.
  3. **Routing:** URL + method → a handler function registered at compile time (e.g. `GET /redfish/v1/Chassis/<str>`).
  4. **Privilege check:** each route needs Redfish privileges (`Login`, `ConfigureComponents`, `ConfigureManager`, `ConfigureUsers`, `ConfigureSelf`). The user's **role** gives a set of them:
     - **Administrator:** all.
     - **Operator:** `Login`, `ConfigureComponents`, `ConfigureSelf`.
     - **ReadOnly:** `Login`, `ConfigureSelf`.
  5. **Handler:** makes **asynchronous** D-Bus calls (mapper lookups, `GetAll`, `Set`) and fills a JSON response as replies arrive. Async means one slow daemon doesn't block other requests.
  6. **JSON response:** shaped to the DMTF **Redfish schema** (with `@odata.id`, `@odata.type`…). Upstream CI checks it with the Redfish Service Validator.
- **No cache, no hardware logic:** every GET reads current D-Bus values; bmcweb never talks to I2C or GPIO. This is why "wrong in Redfish but right on D-Bus" means a bmcweb bug, and "wrong on both" means a lower layer.
- **Other features:** EventService (push events to subscribers, or Server-Sent Events), Redfish aggregation (some builds), and compile-time options to enable or disable features per platform.

**Likely questions:**
- *"Where's the Web UI code?"* `webui-vue` (a Vue.js single-page app). bmcweb serves its static files, and the UI calls Redfish like any client.
- *"Can I add an OEM Redfish property?"* Yes, in bmcweb (OEM sections). Upstream prefers standard schema properties wherever possible.

**Transition:** "Let's follow three real requests through every layer, starting with the simplest: reading a temperature."

---

## Slide 33: Flow 1 — reading a temperature over Redfish

**Purpose:** follow one GET request end to end, and show that the request **never touches the hardware**.

**What's on the slide:** a sequence diagram (Redfish client, bmcweb, ObjectMapper, sensor daemon, kernel/chip). The first message, a periodic read, happens **before** the request.

**In depth: step by step:**

1. **Before any request:** the sensor daemon polls the kernel every poll interval and updates `Value` on D-Bus. This runs whether or not anyone asks.
2. **Client → bmcweb:** `GET /redfish/v1/Chassis/<chassis>/Sensors/<sensor-id>`. In current bmcweb, sensor IDs combine type and name, e.g. `temperature_Inlet_Temp`.
3. **bmcweb:** TLS, authentication, privilege check (`Login` is enough for reading).
4. **bmcweb → ObjectMapper:** finds the chassis's inventory object, follows its `all_sensors` association, and uses `GetSubTree` / `GetObject` to learn which **service** owns the sensor path.
5. **bmcweb → sensor daemon:** `org.freedesktop.DBus.Properties.GetAll` on the sensor object returns `Value`, `Unit`, `MaxValue`, `MinValue`, thresholds, alarms, `Available`, `Functional`.
6. **bmcweb → client:** JSON such as:

```json
{
  "@odata.id": "/redfish/v1/Chassis/MyBoard/Sensors/temperature_Inlet_Temp",
  "Name": "Inlet Temp",
  "Reading": 27.5,
  "ReadingUnits": "Cel",
  "ReadingType": "Temperature",
  "Thresholds": {
    "UpperCaution":  { "Reading": 85 },
    "UpperCritical": { "Reading": 95 }
  },
  "Status": { "State": "Enabled", "Health": "OK" }
}
```

- **Translation details:** D-Bus `Unit = DegreesC` → Redfish `ReadingUnits = "Cel"`; Warning → `UpperCaution`; Critical → `UpperCritical`. `Health` comes from the alarm properties (any critical alarm → `Critical`), and `State` from `Available`/`Functional`.
- **Why reads are fast:** the HTTP request only reads RAM in another process; no I2C transaction happens during it.
- **Stale value:** if `Reading` doesn't change, the **sensor daemon** stopped updating (device not responding, host off with a `PowerState` setting, daemon stuck). bmcweb is just reporting the last value.

**Transition:** "Reading is easy. What about an action like power on?"

---

## Slide 34: Flow 2 — powering on the host

**Purpose:** show that a Redfish **action** becomes one D-Bus property write, and that the operation is asynchronous.

**What's on the slide:** a sequence diagram (client, bmcweb, State.Host owner, systemd/GPIO, power hardware), with a note that `ipmitool chassis power on` writes the same property.

> **Note:** an earlier version of this slide said "204 No Content". bmcweb usually returns **200 OK with a Redfish Success message** for actions (the Redfish spec allows 200, 202 or 204). The source now reads "Success reply (async)". Rebuild the deck to apply it.

**In depth: step by step:**
1. **Client:** `POST /redfish/v1/Systems/system/Actions/ComputerSystem.Reset` with `{"ResetType": "On"}`. Requires the `ConfigureComponents` privilege (Operator or Administrator).
2. **bmcweb → State.Host owner:** maps `ResetType` to a D-Bus write. Typical mapping:

| Redfish `ResetType` | D-Bus write |
|---|---|
| `On` | Host `RequestedHostTransition = On` |
| `GracefulShutdown` | Host `RequestedHostTransition = Off` |
| `ForceOff` | Chassis `RequestedPowerTransition = Off` |
| `GracefulRestart` | Host `RequestedHostTransition = GracefulWarmReboot` |
| `ForceRestart` | Host `RequestedHostTransition = ForceWarmReboot` |
| `PowerCycle` | Chassis `PowerCycle` (or host reboot, depending on version) |
| `Nmi` | NMI control interface (sends a non-maskable interrupt to the host) |

3. **bmcweb → client:** replies as soon as the property write is accepted, **not** when the host has booted. Power-on takes seconds; booting takes minutes.
4. **State owner → systemd/GPIO:**
   - **phosphor-state-manager:** starts `obmc-host-start@0.target`, which pulls in chassis power-on units.
   - **x86-power-control:** pulses the power-button GPIO output (simulating a press) and starts a timer.
5. **Power hardware:** the platform's power sequencer (often a CPLD) turns on the rails in order.
6. **Power-good asserted:** the PGOOD GPIO input goes high. The daemon sees it and updates `CurrentPowerState = On`, then host state through `TransitioningToRunning` to `Running` (exact timing depends on the implementation and BIOS progress signals).
7. **Signals:** each change emits `PropertiesChanged`. bmcweb can push a Redfish event, and clients polling `PowerState` see `On`.

- **Failure path:** if power-good never arrives, the daemon times out, reverts state to `Off` and logs an error entry ("power-on timeout").
- **Same property for IPMI:** `ipmitool chassis power on` → ipmid → `RequestedHostTransition = On`. One implementation, many front doors.

**Likely questions:**
- *"How do I know when it's really booted?"* Watch `CurrentHostState`, BIOS POST codes (`/xyz/openbmc_project/state/boot/raw0` on platforms with POST-code support), or Redfish `BootProgress`.

**Transition:** "Third flow: nobody sends a request — something goes wrong on its own."

---

## Slide 35: Flow 3 — an over-temperature alert

**Purpose:** show **event-driven, decoupled** reactions: one signal, many independent listeners.

**What's on the slide:** temp rises above 95 °C → `CriticalAlarmHigh = true` → `PropertiesChanged` signal → six reactions (event log entry, fault LED, fans to max, Redfish event, IPMI SEL record, optional shutdown). Callout: adding a reaction means adding a listener.

**In depth: each reaction and who does it:**

| Reaction | Daemon | How it learns about the alarm | What it does |
|---|---|---|---|
| Event log entry | phosphor-logging (often via the sensor daemon or a threshold monitor) | Signal or direct report | Creates `/logging/entry/N` with severity Critical and a callout |
| Fault LED on | phosphor-led-manager | Association from the log entry/inventory to an LED group, or a fault monitor | Sets the LED group `Asserted = true`; the physical LED turns amber |
| Fans to max | phosphor-pid-control | Reads the temperature itself every cycle | Thermal PID demand rises; fans speed up (no signal needed) |
| Redfish event | bmcweb EventService | Subscribed to D-Bus signals or log entries | POSTs an event to each subscriber's URL, or pushes over SSE |
| IPMI SEL record | phosphor-sel-logger | Subscribed to threshold signals | Adds a SEL entry (`ipmitool sel list`) |
| Optional shutdown | Platform policy (e.g. a hard-shutdown threshold monitor) | Signal on a `HardShutdown`/`SoftShutdown` threshold | Requests a host power-off to protect hardware |

- **No daemon calls another:** the sensor daemon only changes a property. Everyone else subscribed earlier and the broker delivers the signal.
- **Adding a reaction** (e.g. an SNMP trap): write one new listener. The sensor daemon, logging and bmcweb don't change.
- **Order and timing:** reactions run in parallel, in no guaranteed order. Fan control may already be reacting before any log entry exists.
- **Clearing:** when the temperature drops below the limit minus hysteresis, the alarm clears and listeners react again (LED off, log entry possibly marked resolved, a "deasserted" event).

**Transition:** "We've been translating between Redfish and D-Bus. Here's the full translation key."

---

## Slide 36: Redfish resources ↔ D-Bus objects

**Purpose:** a lookup table from each major Redfish URL to its D-Bus source, for debugging.

**What's on the slide:** a two-column table and a note that IDs such as `system` and `bmc` are bmcweb defaults.

**In depth: each row:**

| Redfish | D-Bus source | Notes |
|---|---|---|
| `/redfish/v1/Systems/system` | `state/host0`, `state/chassis0`, plus `control/host0/*` (boot options, power-restore policy), BIOS version from `software/` | `PowerState`, `Reset` action, `Boot` settings |
| `/redfish/v1/Chassis/<id>` | Inventory objects with `Item.Board` or `Item.Chassis` (from entity-manager) | `<id>` comes from the inventory object name |
| `/redfish/v1/Chassis/<id>/Sensors`, `Thermal`, `Power` | `/xyz/openbmc_project/sensors/*`, chosen through the chassis's `all_sensors` association | `Thermal`/`Power` are older, deprecated schemas; newer clients use `Sensors`, `ThermalSubsystem`, `PowerSubsystem` |
| `/redfish/v1/Managers/bmc` | `state/bmc0`, `network/*`, `time/*`, `software/*` (BMC firmware) | Includes the BMC `Reset` action and network protocol settings |
| `/redfish/v1/UpdateService` | `software/*` | `FirmwareInventory` lists each Software object |
| `/redfish/v1/AccountService` | `user/*` (phosphor-user-manager) | Accounts, roles, LDAP |
| `/redfish/v1/Systems/system/LogServices/EventLog` | `logging/entry/*` (or journal-based, depending on bmcweb build options) | Entries, `ClearLog` action |
| `/redfish/v1/EventService` | Bus signals → subscriber pushes | Subscriptions are stored by bmcweb |

**Debug method using this table:**
1. Find the row for the wrong Redfish value.
2. Check the D-Bus object on the right with `busctl introspect` / `get-property`.
3. If D-Bus is **right** → bmcweb translation bug.
4. If D-Bus is **wrong** → the owning daemon (use the mapper's `GetObject` to find it), then lower layers.

**Transition:** "This table shows the deeper principle: all interfaces converge on D-Bus."

---

## Slide 37: All interfaces converge on D-Bus

**Purpose:** reinforce that Redfish, Web UI, IPMI and shell tools are just **different doors** to the same objects.

**What's on the slide:** five doors (Redfish, Web UI, IPMI in-band, IPMI LAN, busctl/SSH) → the same D-Bus objects → owning daemons → kernel → hardware. Debug tip: reproduce with busctl first.

**In depth:**
- **Consistency:** an admin powering on with Redfish and another with `ipmitool` change the **same** property, so they can never disagree about state.
- **Fix once:** correcting a sensor's scaling in entity-manager JSON fixes it in Redfish, IPMI SDR and the Web UI at the same time.
- **Isolate bugs quickly:**
  - **busctl works but Redfish fails** → front-end (bmcweb) bug.
  - **busctl also wrong** → back-end (daemon/config/kernel) bug.
  - **IPMI wrong but Redfish right** → ipmid provider or SDR mapping.
- **busctl as a test client:**

```sh
# Read the same state Redfish shows
busctl get-property xyz.openbmc_project.State.Host /xyz/openbmc_project/state/host0 \
    xyz.openbmc_project.State.Host CurrentHostState

# Perform the same action Redfish 'Reset On' performs (only on a lab system you're allowed to power on)
busctl set-property xyz.openbmc_project.State.Host /xyz/openbmc_project/state/host0 \
    xyz.openbmc_project.State.Host RequestedHostTransition s \
    xyz.openbmc_project.State.Host.Transition.On
```

**Caution:** `busctl set-property` and `call` change real hardware state and skip Redfish's privilege checks (you're root on the BMC). Use them deliberately, on lab systems.

**Transition:** "With this many doors, security matters. Here's how it's layered."

---

## Slide 38: Security architecture

**Purpose:** present security as **layers**, from network to firmware, and give practical operating advice.

**What's on the slide:** five staggered layers (Network, API, Accounts, Services, Firmware) with controls for each, and the message that an attacker must pass the outer layers first.

**In depth: each layer:**

**1. Network**
- Put BMCs on an **isolated management network**, never the public internet or a production network.
- **Turn off what you don't use:** e.g. IPMI over LAN (UDP 623), which has known protocol weaknesses (RAKP hash exposure in IPMI 2.0). In Redfish: `ManagerNetworkProtocol` → `IPMI.ProtocolEnabled = false`.
- TLS only for web traffic. Replace the self-signed certificate with one from your CA.

**2. API**
- Every request authenticated (except a few public endpoints such as the Redfish service root).
- Role-based privileges (slide 32), session timeouts, a session limit.
- Account lockout after failed logins (an AccountService setting).

**3. Accounts**
- `phosphor-user-manager` manages local users and their roles/groups. PAM checks passwords. Optional LDAP/Active Directory.
- **Default credentials:** upstream development images ship a well-known default account. Production must change it, or force a change at first login.
- Password complexity and history rules via PAM configuration.

**4. Services**
- Each daemon is a separate process: a crash or bug in one doesn't directly expose others' memory.
- systemd restarts failed services; D-Bus policies limit who can call what.
- Least privilege where supported (not all upstream daemons drop root yet; check your platform).

**5. Firmware**
- **Signed update images:** the BMC rejects images not signed by a trusted key (slide 29). Production must use its **own** signing key, not upstream's test key.
- **Secure boot:** boot ROM → SPL → U-Boot → kernel, each verifying the next (slide 11). Platform feature: needs OTP keys programmed.
- **Hardware root of trust** (PFR, Caliptra, DC-SCM RoT): verifies BMC and BIOS flash before they run, and restores known-good copies.

**Operating checklist:**
1. Change or disable default accounts.
2. Isolate the management network.
3. Disable IPMI-over-LAN and other unused protocols.
4. Install proper TLS certificates.
5. Keep BMC firmware updated (security fixes).
6. Use production signing keys and enable secure boot where supported.

**Likely questions:**
- *"Can the host OS attack the BMC through KCS?"* In-band IPMI is a privileged interface. Platforms can restrict in-band commands (IPMI channel and "firmware firewall" settings) and should validate all host input. It's a real attack surface to review.

**Transition:** "Finally: how is all of this built, ported to a new board, and debugged?" (Continue in [Part 6](06_Build_Port_Debug_Slides_39-45.md).)
