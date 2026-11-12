# Speaker Guide, Part 2: Hardware and Boot (Slides 9-14)

[← Part 1](01_Introduction_Slides_01-08.md) · [Part 3 →](03_DBus_Backbone_Slides_15-21.md)

---

## Slide 9: BMC flash layout

**Purpose:** show what is stored on the BMC's flash chip and why it's split into five parts.

**What's on the slide:**
- A horizontal bar showing the 32 MB SPI NOR flash split into `u-boot`, `env`, `kernel (FIT)`, `rofs`, `rwfs`, with boundary offsets underneath.
- A legend with one line per partition.

> **Correction:** the kernel/rofs boundary is **4.75 MB** (`0x4C0000`), not "~4.6 MB". The source script is fixed. Rebuild the deck with PowerPoint closed, or edit the label by hand.

**In depth: the real upstream 32 MB layout** (Linux `openbmc-flash-layout.dtsi`):

| Partition | Offset | Size | Format | Contents |
|---|---|---|---|---|
| `u-boot` | `0x000000` | 384 KB | Raw binary | Bootloader (SPL + U-Boot on AST2600) |
| `u-boot-env` | `0x060000` | 128 KB | `name=value` + CRC32 | Boot command, kernel arguments, MAC addresses |
| `kernel` | `0x080000` | 4.25 MB | FIT image | Linux kernel + device tree (DTB) + initramfs |
| `rofs` | `0x4C0000` | 23.25 MB | squashfs (xz) | All programs, libraries, default configs |
| `rwfs` | `0x1C00000` | 4 MB | JFFS2 | Changed settings that must survive reboot |

- **Why `u-boot` is at offset 0:** the SoC's boot ROM always starts reading the flash from address 0. That's hardware, not configuration.
- **Why `rofs` is the biggest:** it holds the entire OpenBMC userspace, compressed. A typical image fills most of it, and "image too big" build errors are common.
- **FIT image:** a container (in device-tree format) holding the kernel, DTB(s) and initramfs, with hashes and an optional signature, so U-Boot can verify everything together.
- **Why rwfs uses JFFS2:** JFFS2 is designed for raw NOR flash. It spreads writes across the chip (wear levelling) and survives power loss mid-write.
- **Other layouts:**
  - *64 MB static:* the same idea with bigger partitions.
  - *UBI:* two complete images (A/B) on one chip, so one can be updated while the other runs.
  - *eMMC:* gigabytes; GPT partitions with A/B images.

**Likely questions:**
- *"Where are logs stored?"* The systemd journal is in RAM by default, to protect the flash from wear, so it's lost on reboot. Event-log entries (phosphor-logging) are persisted in `rwfs`.
- *"What happens if the env partition is corrupted?"* U-Boot detects the bad CRC, prints a warning and uses its compiled-in default environment. The board usually still boots, but custom settings are lost.
- *"How do I see this on a live BMC?"* `cat /proc/mtd`.

**Transition:** "Notice there's a read-only part and a writable part. How do they become one root filesystem?"

---

## Slide 10: Read-only root + writable overlay

**Purpose:** explain **overlayfs**, the trick that makes updates atomic while settings survive.

**What's on the slide:**
- **Left:** three stacked boxes. Top: what processes see (`/`). Middle: upper writable layer (rwfs). Bottom: lower read-only layer (rofs).
- **Right:** three outcomes: firmware update, settings persist, factory reset.

**In depth:**
- **overlayfs** is a Linux filesystem that **merges two directories** into one view:
  - *lower* (read-only): the squashfs image;
  - *upper* (writable): a directory on the JFFS2 partition;
  - *merged:* what every program sees as `/`.
- **Reading a file:** the kernel checks the upper layer first. If the file exists there (because someone changed it), that copy is used; otherwise the lower layer's original.
- **Writing a file:** the first write **copies the file up** from lower to upper, then modifies the copy (copy-on-write). The lower layer never changes.
- **Deleting a file:** a special marker (a "whiteout") is created in the upper layer, hiding the lower file.
- **Who sets this up:** in the static flash layout, the **initramfs** `/init` script (`obmc-init.sh`) mounts rofs and rwfs, builds the overlay and switches to it before systemd starts.
- **The three benefits:**
  1. *Atomic update:* replacing the whole rofs means you get the old system or the new one, never a mix.
  2. *Settings persist:* the upper layer isn't touched by updates, so network config, users and certificates survive.
  3. *Factory reset = erase the upper layer:* everything goes back to image defaults.
- **A trap:** if an update changes a default file in `/etc` that you previously modified, **your modified copy in the upper layer still wins**. This can hide new defaults after an update.

**Likely questions:**
- *"How do I see what I've changed?"* List the upper directory (in the static layout, under `/run/initramfs/rw/cow`).
- *"Is the whole `/` overlaid, or just `/etc`?"* In the static layout the whole root is an overlay. Other layouts (UBI/eMMC) may persist only selected directories such as `/etc` and `/var`.

**Transition:** "Now, how does the BMC get from power-on to running all of this?"

---

## Slide 11: Boot chain — power to login prompt

**Purpose:** walk the boot sequence and show that **each stage verifies and hands off to the next**.

**What's on the slide:** six boxes left to right (Standby power on → SoC boot ROM → U-Boot → Linux kernel → systemd → BMC Ready) with detail cards underneath, and a debug tip.

**In depth: stage by stage:**

1. **Standby power on.** AC power comes in; the PSU's standby output powers the BMC; reset is released. The host stays **off**.
2. **SoC boot ROM.** Code permanently built into the chip runs first. It reads **strap pins** (resistors that pick the boot source, e.g. SPI or eMMC) and loads the first-stage loader into on-chip SRAM. With secure boot enabled, it checks that loader's signature against a key hash burned into **OTP fuses** (write-once memory). On AST2600 the first stage is limited to 64 KB because SRAM is tiny.
3. **U-Boot.** In two parts:
   - *SPL* initialises clocks and **trains the DRAM** (calibrates it so it works reliably).
   - *U-Boot proper* runs from DRAM, reads its environment, then runs `bootcmd`. That reads the FIT image from flash, verifies hashes/signature, decompresses the kernel into DRAM and starts it with the DTB address.
4. **Linux kernel.** It unpacks the device tree, creates devices, binds drivers, then runs the initramfs, which mounts rofs + rwfs as the overlay and switches into it.
5. **systemd (PID 1).** The first user-space process. It starts every service in dependency order, including the OpenBMC daemons and `obmc-*` targets.
6. **BMC Ready.** `phosphor-state-manager` sets `CurrentBMCState = Ready` once the BMC's startup target (normally `multi-user.target`) has finished. Redfish and IPMI are now reachable.

- **Chain of trust:** each stage only runs the next after verifying it. ROM → SPL (OTP key), SPL → U-Boot (FIT signature), U-Boot → kernel (FIT signature). A failure stops the boot or switches to a backup image.
- **Serial console:** the BMC's debug UART (often UART5 on ASPEED, `/dev/ttyS4` in Linux) prints messages from every stage. It's the primary bring-up tool.

**Likely questions:**
- *"How long does it take?"* Typically 30 seconds to a few minutes until Redfish answers. The DRAM, kernel and systemd stages dominate.
- *"Where does BIOS fit?"* It doesn't. The host's BIOS runs on the host CPU later, when the BMC powers the host on.

**Transition:** "In step 4 the kernel 'parses the device tree.' What is that?"

---

## Slide 12: Device tree — describing the board to the kernel

**Purpose:** explain how one kernel binary knows what's on **this** board.

**What's on the slide:**
- **Left:** a simplified `board.dts` with a TMP75 sensor on I2C bus 6 at address 0x48, and GPIO line names.
- **Right:** a 5-step flow: source → `dtc` compiler → packed in FIT → kernel matches `compatible` → driver creates hwmon files.
- **Callout:** a wrong address or bus means the sensor is silently missing.

**In depth:**
- **Why it's needed:** ARM SoCs have buses (I2C, SPI, GPIO) whose devices **can't be scanned**. Something must tell the kernel "there's a TMP75 at 0x48 on bus 6."
- **File types:**
  - `.dtsi` = SoC-wide description (every controller on the AST2600, mostly `disabled`);
  - `.dts` = board file (includes the `.dtsi`, enables what the board uses, adds chips);
  - `.dtb` = compiled binary.
- **Reading the example:**
  - `&i2c6 { … }` modifies the node labelled `i2c6` from the SoC file.
  - `status = "okay"` turns that controller on.
  - `temp@48` is a child node: a device at address 0x48 on that bus.
  - `compatible = "ti,tmp75"` names the device type. The kernel finds the driver whose match table contains this string (here, the `lm75` driver).
  - `reg = <0x48>` is the **7-bit** I2C address.
  - `gpio-line-names` gives each GPIO line a name, in order.
- **Why GPIO names matter to OpenBMC:** power-control and GPIO-monitor daemons find lines **by name** with libgpiod, not by number.
  - OpenBMC's GPIO naming design document recommends lowercase, hyphenated names (e.g. `power-button`, `power-chassis-good`).
  - Many x86 platforms use the names `x86-power-control` defaults to (e.g. `POWER_OUT`, `PS_PWROK`), which can be overridden in its JSON config.
  - Either way, **the name in the DTS must exactly match what the daemon looks for**.
- **Compile and match:** `dtc` (after the C preprocessor) turns `.dts` into `.dtb`. Yocto builds it and packs it into the FIT. At boot the kernel creates a device for each enabled node and calls the matching driver's `probe()`.

**Likely questions:**
- *"7-bit vs 8-bit address?"* Datasheets sometimes give the 8-bit form (`0x90`) that includes the read/write bit. The DTS needs the 7-bit form (`0x48`, i.e. `0x90 >> 1`). This is a very common mistake.
- *"Can I see the live device tree?"* `ls /proc/device-tree/` or `/sys/firmware/devicetree/base/`. Decompile with `dtc -I fs -O dts /sys/firmware/devicetree/base` if `dtc` is installed.
- *"DTS or entity-manager JSON?"* DTS for **fixed** wiring that's always present. entity-manager JSON for parts that **vary** or are detected from FRU data. Don't describe the same I2C device in both (slide 23).

**Transition:** "Once drivers are bound, how do daemons talk to the hardware?"

---

## Slide 13: Kernel — the only path to hardware

**Purpose:** show the four-step chain **hardware → driver → interface → daemon**, and why daemons never touch registers.

**What's on the slide:** five rows, each with four boxes connected by arrows.

**In depth: each row:**

| Hardware | Driver | Interface | Daemon | Notes |
|---|---|---|---|---|
| TMP75 temperature chip | `lm75` (hwmon) | `/sys/class/hwmon/hwmonN/temp1_input` | `hwmontempsensor` | Value in millidegrees: `27500` = 27.5 °C |
| Fan + PWM | ASPEED PWM/tach driver | hwmon `pwm1`, `fan1_input` | `fansensor`, `swampd` | `aspeed-pwm-tacho` on AST2500; AST2600 uses a newer PWM/tach driver |
| Power button GPIO | `gpio-aspeed` | `/dev/gpiochip0` (lines by name) | `x86-power-control` | libgpiod: request line by name, set or read value |
| Host CPU | `peci-cpu` + `peci-cputemp` / `peci-dimmtemp` | `/dev/peci-0`, hwmon | `intelcpusensor` | CPU die and DIMM temperatures over PECI |
| KCS channel | `kcs-bmc` (ASPEED backend) | `/dev/ipmi-kcs3` | `kcsbridged` → `ipmid` | Read a request, write a response |

- **Why this design:**
  1. **Portability:** the same `hwmontempsensor` works on ASPEED, Nuvoton or any SoC with an I2C driver.
  2. **Quality:** drivers are reviewed in the Linux kernel community.
  3. **Debuggability:** you can check every step yourself with `cat` or `ls`.
  4. **Low effort:** supporting a new chip is usually "enable an existing kernel driver + add config," not new code.
- **What "hwmon" is:** the Linux **hardware-monitoring** subsystem. Every sensor driver exposes the same file naming (`tempN_input`, `inN_input`, `fanN_input`, `pwmN`, `powerN_input`, `currN_input`), so one daemon can read any of them.

**Likely questions:**
- *"What if no kernel driver exists for my chip?"* Either write or upstream a kernel driver (preferred), or, for PMBus devices, use the generic `pmbus` driver. Some daemons talk to `/dev/i2c-N` directly for special cases.
- *"Which hwmonN is my chip?"* The numbers change between boots. Check `cat /sys/class/hwmon/hwmon*/name`, or follow `/sys/bus/i2c/devices/6-0048/hwmon/`.

**Transition:** "Who starts all these daemons, and in what order?"

---

## Slide 14: systemd — ordering everything

**Purpose:** show that every daemon is a **systemd unit**, and that OpenBMC uses systemd **targets** to model server power states.

**What's on the slide:**
- **Top:** `obmc-host-start@0.target` with arrows to `obmc-chassis-poweron@0.target` ("Requires") and to host-start units ("pulls in").
- **Bottom left:** chassis power-on target pulls in power-sequence units, a wait-for-power-good step, and platform hook units.
- **Table:** the four main targets.
- **Commands** box.

**In depth:**
- **Unit:** anything systemd manages: `.service` (a daemon), `.target` (a group or milestone), `.socket`, `.timer`…
- **Target:** a named group of units. Starting a target starts everything it depends on. Classic example: `multi-user.target`.
- **OpenBMC's state targets** (in `phosphor-state-manager`):

| Target | Meaning | Typically pulls in |
|---|---|---|
| `obmc-chassis-poweron@0.target` | Main power on | Units that drive power GPIOs/regulators, then wait for power-good |
| `obmc-host-start@0.target` | Boot the host | Chassis power-on (directly or via a "startmin" target), then host-start units |
| `obmc-host-stop@0.target` | Shut down the host | Graceful/forced shutdown units |
| `obmc-chassis-poweroff@0.target` | Main power off | Units that drop power rails |

- **Template instances (`@0`):** one unit file serves many instances. `@0` is host 0; multi-host systems (several servers sharing one BMC) use `@1`, `@2`…
- **Dependency types:**
  - `Requires=` — if the dependency fails, this unit fails too.
  - `Wants=` — start the dependency, but don't fail if it fails.
  - `After=` / `Before=` — order only; doesn't start anything.

  Requirement and ordering are separate settings, and missing `After=` is a common bug.
- **Platform hooks:** a vendor adds its own `.service` to a target (in its Yocto layer) for board-specific steps, e.g. "enable a CPLD rail before host start."
- **Restart on crash:** most OpenBMC services set `Restart=always`, so a crashing daemon comes back, and systemd records each restart.
- **Important:** `x86-power-control` (used on many x86 platforms) **doesn't** use these targets for sequencing; it drives GPIOs directly (slide 27). Know which one your platform uses.

**Likely questions:**
- *"How do I see what a target will start?"* `systemctl list-dependencies obmc-host-start@0.target`
- *"How do I see why a service failed?"* `systemctl status <unit>` then `journalctl -u <unit> -b`.
- *"What is `-b`?"* Show logs from the current boot only.

**Transition:** "All these daemons are running. How do they talk to each other? That's D-Bus, the heart of OpenBMC." (Continue in [Part 3](03_DBus_Backbone_Slides_15-21.md).)
