# Speaker Guide, Part 1: Introduction and Hardware (Slides 1-8)

An in-depth explanation of every slide in [OpenBMC_Architecture.pptx](../OpenBMC_Architecture.pptx). Each slide has:

- **Purpose:** why the slide exists in the talk.
- **What's on the slide:** how to read the visual.
- **In depth:** what you need to understand to explain it confidently.
- **Likely questions:** what your team may ask, with answers.
- **Transition:** how to lead into the next slide.

The speaker notes inside the PowerPoint are the short version. This guide is the long version.

| Part | Slides | Topic |
|---|---|---|
| **1 (this file)** | 1-8 | What a BMC is, OpenBMC overview, hardware context |
| [2](02_Hardware_and_Boot_Slides_09-14.md) | 9-14 | Flash, overlay, boot chain, device tree, kernel, systemd |
| [3](03_DBus_Backbone_Slides_15-21.md) | 15-21 | D-Bus, namespace, interfaces, ObjectMapper, associations, signals |
| [4](04_Function_Daemons_Slides_22-30.md) | 22-30 | Daemons: inventory, sensors, fans, power, logging, update, host protocols |
| [5](05_Interfaces_and_Flows_Slides_31-38.md) | 31-38 | Remote access, bmcweb, end-to-end flows, Redfish mapping, security |
| [6](06_Build_Port_Debug_Slides_39-45.md) | 39-45 | Yocto, board porting, principles, debugging, takeaways |

Service, path and driver names are typical upstream OpenBMC names. Your platform may use different ones; check with `busctl list` and `systemctl list-units` on your BMC.

---

## Slide 1: Title — "OpenBMC Architecture"

**Purpose:** set the goal of the session. By the end, everyone should be able to say *which layer* to look at when something breaks.

**What's on the slide:** a strip of six coloured boxes: Hardware → Kernel → systemd → D-Bus → Daemons → Redfish / IPMI. This is a compressed version of the full layer stack on slide 6.

**In depth:**
- Read the strip left to right as **the path a piece of data takes**. A temperature is measured by a chip (hardware), read by a driver (kernel), by a program that systemd started, published on D-Bus, then turned into Redfish JSON.
- Read it right to left as **the path a command takes**. "Power on" arrives as Redfish, becomes a D-Bus property write, a daemon acts, and a GPIO toggles.
- Fill in your name and date before presenting.

**Transition:** "Here's the order we'll go in."

---

## Slide 2: Agenda

**Purpose:** show that the talk goes **bottom-up**: each part needs the one before it.

**What's on the slide:** seven numbered parts, each with a short description.

**In depth:**
- **Why bottom-up?** You can't understand why a sensor is missing from Redfish (part 5) without knowing that sensors come from D-Bus (part 3), which come from daemons (part 4), which read kernel files (part 2).
- Parts 1-5 are the **"what"**. Part 6 (end-to-end flows) is where everything connects. Part 7 is the practical **"how do I use this at work"**.
- **Timing suggestion (about 60 min):** Part 1: 6 min, Part 2: 10, Part 3: 12, Part 4: 12, Part 5: 6, Part 6: 6, Part 7: 8, plus Q&A.

**Transition:** "Let's start with the most basic question: what is a BMC?"

---

## Slide 3: What is a BMC?

**Purpose:** establish that a BMC is a **separate computer** inside the server.

**What's on the slide:**
- **Left (HOST):** the server's main computer: CPUs, large DRAM, PCIe devices, BIOS/UEFI, customer OS.
- **Right (BMC):** a small ARM system-on-chip (SoC) with its own DRAM, flash, NIC and Linux.
- **Green arrow (BMC → host), "controls & observes":** the BMC powers the host on and off, reads its sensors, captures its screen.
- **Blue arrow (host → BMC), "in-band messages":** the host's BIOS or OS sends messages to the BMC over internal wiring (IPMI over KCS, MCTP/PLDM, serial console).
- **Yellow box:** the BMC runs on **standby power**.

**In depth:**
- **Standby power:** as soon as the server is plugged in, the power supply provides a standby rail (usually 12 V standby). The BMC runs from it. The host's main power is switched on separately, by the BMC. That's why the BMC can turn the host on: it's already running.
- **Two computers, two operating systems:** the host runs Windows, Linux, VMware, etc. The BMC runs its own embedded Linux (OpenBMC). They don't share memory or CPU.
- **Typical BMC chips:** ASPEED AST2500/AST2600/AST2700, Nuvoton NPCM7xx/8xx. They are small (1-2 GB DRAM, 32-128 MB flash, or eMMC on newer designs) but include special hardware for management: video capture, KCS (keyboard controller style) host interfaces, PWM/tach controllers, many I2C buses.
- **In-band vs out-of-band:**
  - *In-band:* from **inside** the server, host → BMC over board wiring (KCS, eSPI, PCIe, USB).
  - *Out-of-band:* from **outside**, over the BMC's own network port (Redfish, IPMI-over-LAN, SSH). This works even with the host off.

**Likely questions:**
- *"Can the host OS see the BMC?"* Partly. It sees the KCS interface (as `/dev/ipmi0` with `ipmitool`), a virtual USB keyboard and CD drive, and a VGA device (the BMC's video chip). It can't log into the BMC's Linux through those.
- *"What happens if the BMC crashes?"* The host keeps running. You lose monitoring and remote control until the BMC reboots, and fans typically go to a safe high speed.

**Transition:** "So what does this little computer actually do all day?"

---

## Slide 4: What does a BMC do?

**Purpose:** list the six **requirements**. Every daemon later in the talk serves one of these.

**What's on the slide:** six tiles: Monitor, Control power, Cool, Inventory, Remote access, Update & log.

**In depth: what each job means and which software does it later:**

| Job | What it means in practice | Covered on slide |
|---|---|---|
| **Monitor** | Read hundreds of temperatures, voltages, currents, fan speeds and power readings continuously; raise alarms on thresholds | 23-25 |
| **Control power** | On, off, reset, power-cycle, graceful shutdown of the host, plus power capping on some platforms | 27, 34 |
| **Cool** | Run a feedback loop that sets fan speeds from temperatures; failsafe if sensors are lost | 26 |
| **Inventory** | Know which parts are installed (CPUs, DIMMs, PSUs, drives, cards), with serial and part numbers from FRU EEPROMs | 23 |
| **Remote access** | Serial console, graphical KVM, virtual media to install an OS remotely | 31 |
| **Update & log** | Update BMC/BIOS/PSU/CPLD firmware; keep event logs; push alerts to management systems | 28, 29 |

- **Why it matters for operators:** a large data center has tens of thousands of servers and few people. Every job the BMC does remotely saves a walk to a rack.
- **Fleet management:** tools like OpenStack Ironic, vendor managers or custom automation use Redfish to do all of this at scale.

**Likely questions:**
- *"Does the BMC control the host's network or storage?"* Generally no. It manages the hardware platform, not the host's data path. It may read NIC or drive health (via MCTP/PLDM or NVMe-MI) and update their firmware.

**Transition:** "Now, OpenBMC is one way to build software that does all of this."

---

## Slide 5: What is OpenBMC?

**Purpose:** explain that OpenBMC is a **framework and Linux distribution**, not a single program, and contrast it with closed vendor firmware.

**What's on the slide:**
- **Hub and spokes (left):** OpenBMC is made of a Yocto-built Linux distro, kernel + U-Boot, many small daemons, a D-Bus object model, and Redfish/IPMI front ends.
- **Table (right):** traditional BMC vs OpenBMC.
- **Timeline:** 2014 Facebook hackathon, 2018 Linux Foundation project.

**In depth:**
- **Yocto-built:** OpenBMC isn't installed like Ubuntu; it is *built* from source by Yocto/BitBake into one flash image for one specific board (part 7).
- **Many small daemons:** instead of one huge program, dozens of services each do one job (sensors, power, logging…). They live in separate repositories on github.com/openbmc.
- **D-Bus as the API:** the daemons don't call each other's functions. They publish and read objects on a shared message bus. This is the most important design decision (part 3).
- **History:** started at Facebook in 2014 to get control over BMC firmware in their data centers; joined by IBM, Google, Microsoft, Intel and others; became a Linux Foundation project in 2018.
- **Traditional BMC firmware:** historically a closed, single-vendor codebase (often from one firmware company), customised per server vendor. Bugs could only be fixed by the vendor, and behaviour was hard to inspect.
- **What "upstream" means:** the shared community codebase. Vendors add their board support in their own layers (`meta-<vendor>`) and contribute general fixes back.

**Likely questions:**
- *"Is every vendor's OpenBMC the same?"* The core is shared, but each vendor picks daemons, adds board configs, and may carry private patches or OEM features. "OpenBMC-based" firmware can differ a lot between vendors.
- *"Is OpenBMC only for ASPEED?"* No. ASPEED and Nuvoton are the main supported SoCs, and other ARM SoCs can be ported.

**Transition:** "Here's the single most important picture of the talk."

---

## Slide 6: The big picture — seven layers

**Purpose:** give the **map** for the rest of the talk. Every later slide zooms into one of these layers.

**What's on the slide:**
- Seven stacked bars, layer 1 (Flash) at the bottom to layer 7 (External interfaces) at the top.
- **Blue arrow down:** requests flow down ("read sensor", "power on").
- **Green arrow up:** data and events flow up.
- **Purple callout:** "Layer 5 is the heart: daemons never call each other directly."

**In depth: each layer in one sentence, and where it's covered:**

| # | Layer | One-sentence role | Slides |
|---|---|---|---|
| 1 | Flash | Permanent storage: bootloader, its settings, kernel, read-only programs, writable settings | 9-10 |
| 2 | Boot | Fixed ROM code starts U-Boot, which loads and verifies the kernel | 11 |
| 3 | Kernel + device tree | The only software that touches hardware; exposes it as files and devices | 12-13 |
| 4 | systemd | Starts every daemon in the right order and restarts it if it crashes | 14 |
| 5 | D-Bus + ObjectMapper | The shared "database" of objects all daemons read and write | 15-21 |
| 6 | Function daemons | Each implements one job from slide 4 | 22-30 |
| 7 | External interfaces | Translate Redfish/IPMI/Web into D-Bus operations | 30-37 |

- **Why "layer 5 is the heart":** because all communication goes through D-Bus, you can test or debug any feature by looking at D-Bus alone. If the D-Bus data is right, the problem is above it; if wrong, below it.
- **Layering rule:** each layer only talks to its neighbours. bmcweb (layer 7) never reads an I2C device; it reads D-Bus. A sensor daemon (layer 6) never pokes registers; it reads a kernel file.

**Likely questions:**
- *"Where does the device tree fit?"* It belongs to layer 3: it tells the kernel what hardware exists. It is built separately but loaded with the kernel (layer 2).
- *"Where does the web UI fit?"* Layer 7. It is a web app served by bmcweb that calls Redfish like any other client.

**Transition:** "Let's start at the bottom: what is the BMC physically wired to?"

---

## Slide 7: Hardware context — what the BMC is wired to

**Purpose:** show the **physical** connections the software must manage. The software's job is to turn all these different wires into one clean API.

**What's on the slide:** the BMC SoC in the centre with eight spokes, each a type of connection.

**In depth: each spoke:**

- **SPI / eMMC → BMC flash.** Where the BMC's own firmware lives. SPI NOR (32-128 MB) on most designs; eMMC (GBs) on newer ones. Covered on slides 9-11.
- **I2C / I3C → sensors, VRs, PSUs, FRUs.** The busiest connection. A BMC has 8-16+ I2C buses. On them:
  - temperature sensor chips (e.g. TMP75 at address 0x48);
  - voltage regulators (VRs) that report voltage, current and temperature using **PMBus** (a command set on top of I2C);
  - power supplies (PSUs), also PMBus;
  - **FRU EEPROMs** (small memory chips holding manufacturer, part and serial number for a board or part).

  I3C is the faster successor, used for DDR5 DIMM sensors and newer devices.
- **GPIO → power button, reset, PGOOD.** Simple on/off signals:
  - *outputs* from the BMC: press the power button, assert reset, turn on an LED;
  - *inputs* to the BMC: power-good (PGOOD) means the power rails are stable; presence pins show whether a PSU or card is inserted.
- **PWM / Tach → fans.** PWM (pulse-width modulation) sets fan speed by duty cycle. Tach (tachometer) is a pulse signal from the fan for measuring actual RPM.
- **PECI / APML → CPU temps and errors.** Special one-wire buses for reading host CPU data. PECI is Intel's; APML (over I2C/I3C) is AMD's. They give CPU die temperature, DIMM temperatures, and error registers after a crash.
- **eSPI / LPC (KCS) → in-band IPMI.** The bus between the host chipset and the BMC. **KCS** is a small mailbox the BIOS/OS uses to send IPMI commands. The BIOS also sends POST codes over it (port 0x80).
- **PCIe · USB · UART → VGA, MCTP, KVM, console:**
  - *PCIe:* the BMC appears to the host as a VGA graphics card. The BMC captures that screen for KVM. PCIe also carries MCTP messages (vendor-defined messages).
  - *USB:* the BMC acts as a USB device to the host (virtual keyboard, mouse, CD drive).
  - *UART:* the host's serial console is wired to the BMC (Serial over LAN).
- **RGMII / NC-SI → management network.** RGMII connects the BMC's MAC to its own Ethernet PHY (a dedicated management port). **NC-SI** lets the BMC **share** the host's NIC, so one cable serves both.

**Likely questions:**
- *"Why so many I2C buses?"* Devices at the same address can't share a bus, buses get slow with many devices, and separating them isolates faults. I2C muxes (like the PCA9548) add even more downstream buses.
- *"What's the difference between eSPI and LPC?"* LPC is the older parallel bus. eSPI is its serial replacement on newer Intel/AMD platforms. Both carry KCS, POST codes and virtual UART.

**Transition:** "Here's the same information as a reference table, adding what the kernel exposes."

---

## Slide 8: Hardware link cheat sheet

**Purpose:** connect each wire to (a) the **kernel interface** software uses and (b) the **feature** users see. Use this as a reference.

**What's on the slide:** a 4-column table: Link · Talks to · Kernel exposes · Used for.

**In depth: the "Kernel exposes" column is the key one:**

| Kernel interface | What it is | Example use |
|---|---|---|
| `/dev/i2c-N` | Raw I2C bus access (character device) | Tools like `i2cget`; daemons that talk PMBus directly |
| hwmon sysfs (`/sys/class/hwmon/hwmonN/…`) | Standard Linux files for sensors: `temp1_input` (millidegrees C), `in1_input` (mV), `fan1_input` (RPM), `pwm1` (0-255) | dbus-sensors reads these |
| `/dev/gpiochipN` (libgpiod) | Modern GPIO access; lines found by **name** | x86-power-control finds "power button" by name |
| `/dev/peci-N` | PECI bus; also hwmon drivers for CPU and DIMM temperature | intelcpusensor |
| `/dev/ipmi-kcsN` | The BMC side of the KCS mailbox | kcsbridged |
| `AF_MCTP` sockets | Kernel MCTP networking: send and receive by endpoint ID | mctpd, pldmd |
| configfs gadget | Configure the BMC's USB device personality | KVM keyboard/mouse, virtual media |
| `/dev/ttySN` | Serial ports | obmc-console |
| `ethN` | Network interfaces | phosphor-networkd, bmcweb |

- **Key message:** OpenBMC daemons talk **only** to these kernel interfaces, never to hardware registers directly. Benefits:
  - the same daemon works on any SoC that has a kernel driver;
  - drivers are reviewed and maintained upstream in Linux;
  - you can test by reading the file yourself, e.g. `cat /sys/class/hwmon/hwmon3/temp1_input`.
- **Units in hwmon:** temperature in **millidegrees** (27500 = 27.5 °C), voltage in **millivolts**, current in milliamps, power in **microwatts**, fan in RPM. Daemons convert these to standard units on D-Bus.

**Likely questions:**
- *"What is configfs?"* A kernel filesystem (`/sys/kernel/config`) where programs create kernel objects by making directories and writing files. USB gadgets are set up this way.

**Transition:** "We know what's wired to the BMC. Now: what's on its flash, and how does it boot?" (Continue in [Part 2](02_Hardware_and_Boot_Slides_09-14.md).)
