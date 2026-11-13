# 5. Power, SPI Flash, and Boot: A Walkthrough from AC to "BMC Ready"

This chapter answers a common set of first questions with diagrams: where the BMC gets power, how it is wired to its SPI flash, what flashing does inside the chip, which instruction runs first, and what happens next until OpenBMC is ready.

The examples use ASPEED AST2500/AST2600 because most OpenBMC boards use them. **Voltages, currents, timings, and addresses below are typical illustrative values, not ASPEED datasheet values.** Check your board schematic and the ASPEED datasheet before relying on a number. Labels follow the [ASPEED volume](../ASPEED_BMC_SoC_Textbook/00_README.md): *documented* means a public source states it; *typical* means common practice that varies by board.

## 5.1 The big picture

```text
 AC MAINS (230V/110V)
       │
 ┌─────▼──────────────────────────────────────────────────────────────┐
 │                       PSU (Power Supply Unit)                      │
 │   Standby output (ON whenever AC is plugged in): 12V_STBY / 5VSB   │
 │   Main output (ON only when the host is powered ON): 12V main      │
 └─────┬───────────────────────────────────────────┬──────────────────┘
       │ STANDBY (always on)                       │ MAIN (host on only)
 ┌─────▼───────────────────────────┐        ┌──────▼──────────────────┐
 │   STANDBY POWER DOMAIN          │        │  HOST DOMAIN            │
 │  ┌───────┐  SPI  ┌───────────┐  │ GPIO/  │  CPU, PCH, DIMMs,       │
 │  │ BMC   │◄─────►│ SPI NOR   │  │ eSPI/  │  BIOS flash, fans...    │
 │  │AST2600│       │ (firmware)│  │ LPC/   │                         │
 │  └──┬────┘       └───────────┘  │ I2C    │                         │
 │     │ DDR                       │◄──────►│                         │
 │  ┌──▼─────┐ ┌──────┐ ┌────────┐ │        │                         │
 │  │ DRAM   │ │ PHY/ │ │ CPLD / │ │        │                         │
 │  │512M-1G │ │ NIC  │ │ PwrSeq │ │        │                         │
 │  └────────┘ └──────┘ └────────┘ │        │                         │
 └─────────────────────────────────┘        └─────────────────────────┘
```

**Key point:** the BMC runs from **standby power**. It boots as soon as AC is connected, while the server still looks "off", and it is the BMC that later turns the host on. This holds only while standby power and the BMC's own resources are present (see [Chapter 1](01_Hardware_and_Boot.md)); it is not an unconditional guarantee.

## 5.2 Where the power comes from and how it is divided

```text
 PSU 12V_STBY (or 5VSB) ── a few amps available on standby (typical)
      │
      ├──► Buck regulator ──► P3V3_STBY (3.3V)  → BMC I/O, 3.3V SPI flash, PHY, CPLD, EEPROMs, sensors
      ├──► Buck/LDO ────────► P1V8_STBY (1.8V)  → BMC 1.8V I/O banks, 1.8V SPI flash, PLLs
      ├──► Buck ────────────► VDD_CORE (~1.1-1.2V class) → BMC Arm core  [check the datasheet]
      ├──► Buck ────────────► P1V2_DDR (VDDQ)   → DDR4 memory + BMC DDR PHY
      │                       P2V5 (VPP)        → DDR4 VPP
      │                       0.6V (VTT/VREF)   → DDR termination
      └──► ...                                  → USB / ADC / analog rails
```

The whole BMC subsystem (SoC, DRAM, flash, PHY) typically draws on the order of **a few watts** (roughly 1.5-5 W).

### Power sequencing and reset release

```text
 Time ─►
 AC plug-in
   │
   ▼
 12V_STBY  ────┐______________________________________ (rises in ~ms)
 P3V3_STBY ─────────┐_________________________________
 P1V8_STBY ──────────────┐____________________________
 VDD_CORE  ───────────────────┐_______________________
 DDR rails ────────────────────────┐__________________
 PWRGOOD   ─────────────────────────────┐_____________  (all rails OK)
 BMC SRST# ‾‾‾‾‾‾‾‾(held LOW = reset)‾‾‾‾‾‾‾‾‾‾‾┐______  RELEASED → CPU starts
                                               ▲
                     Strap pins latched here ──┘
```

1. Rails rise in the order the datasheet requires. A CPLD, a sequencer, or power-good chaining between regulators enforces the order.
2. While the rails ramp, a reset supervisor or the CPLD holds the BMC reset input (`SRST#` / `PORST#`) **low**.
3. When all rails are stable, `PWRGOOD` asserts and reset is **released**. Strap pins are latched and the CPU starts fetching instructions.

## 5.3 How the BMC is wired to the SPI flash

```text
          AST2600 BMC                                SPI NOR flash (e.g. 32-64 MiB)
 ┌────────────────────────────┐                     ┌─────────────────────┐
 │  FMC (Firmware Memory      │  FWSPICS0# ────────►│ CS#   (chip select) │  ← primary (boot) flash
 │       Controller)          │  FWSPICK   ────────►│ CLK                 │
 │                            │  FWSPIDQ0  ◄───────►│ IO0 / MOSI (DI)     │
 │  ┌──────────────────────┐  │  FWSPIDQ1  ◄───────►│ IO1 / MISO (DO)     │
 │  │ Memory-mapped window │  │  FWSPIDQ2  ◄───────►│ IO2 / WP#           │ (quad mode)
 │  │ 0x2000_0000 → CS0    │  │  FWSPIDQ3  ◄───────►│ IO3 / HOLD#         │
 │  │ (CS1 above it)       │  │                     │ VCC (3.3V or 1.8V)  │
 │  └──────────────────────┘  │                     └─────────────────────┘
 │                            │  FWSPICS1# ───────► [ 2nd flash: golden/backup image ]
 │  SPI1 / SPI2 controllers ──┼───────────────────► [ host BIOS flash, often via a mux ]
 └────────────────────────────┘
```

- The **FMC** is the boot SPI controller (AST2600 registers at `0x1E62_0000`; see [ASPEED Chapter 2](../ASPEED_BMC_SoC_Textbook/02_AST2600_Hardware.md)).
- **CS0** is the boot flash. **CS1** can hold a backup ("golden") image.
- The FMC supports a **memory-mapped read mode**. The CPU reads an address in the flash window (typically starting at `0x2000_0000`), and the controller turns that read into SPI READ commands in hardware. The per-chip-select window boundaries are set by segment registers, so check them for your part.

That memory-mapped mode is how the BMC "automatically takes code from SPI". No software has to drive the SPI bus to fetch the earliest instructions.

## 5.4 What happens inside the flash when you write it

SPI NOR stores each bit as charge on a **floating-gate** (or charge-trap) cell. The charge persists without power, which makes the memory non-volatile.

| Operation | Effect | Granularity |
| --- | --- | --- |
| **Erase** | all bits become `1` (`0xFF`) | 4 KiB sector, 32/64 KiB block, or whole chip |
| **Program** | chosen bits change `1 → 0` | page, typically 256 bytes |
| **Read** | no change | any byte |

A bit can **never** be programmed from 0 to 1. That is why NOR must be erased before it is written.

### Typical SPI command sequence for a write

```text
 Host/programmer                    SPI flash
     │── 0x06 WREN (write enable) ──►│  sets WEL bit
     │── 0x20 SECTOR ERASE + addr ──►│  4 KiB → all 0xFF   (tens to hundreds of ms)
     │── 0x05 READ STATUS ──────────►│
     │◄──────── WIP=1 (busy) ────────│  ...poll...
     │◄──────── WIP=0 (done) ────────│
     │── 0x06 WREN ─────────────────►│
     │── 0x02 PAGE PROGRAM + addr + up to 256 bytes ──►│  (sub-ms to a few ms)
     │── 0x05 poll until WIP=0 ─────►│
     │   ... repeat for every page ...
     │── 0x03 / 0x0B READ (verify) ─►│
```

Other common opcodes: `0xD8` 64 KiB block erase, `0xC7`/`0x60` chip erase. Devices larger than 16 MiB need **4-byte addressing**, either by entering 4-byte mode (`0xB7`) or by using the 4-byte variants of each command. Opcodes and timings are vendor-specific in detail; read the flash part's datasheet.

### How the OpenBMC static image is laid out

The classic 32 MiB static layout (`image-bmc` / `*.static.mtd`), from Linux `arch/arm/boot/dts/aspeed/openbmc-flash-layout.dtsi`:

```text
 0x0000000 ┌──────────────────────┐
           │ u-boot      384 KiB  │  0x60000 bytes   ← first code read from flash
 0x0060000 ├──────────────────────┤
           │ u-boot-env  128 KiB  │  0x20000 bytes   bootcmd, bootargs, MAC addresses
 0x0080000 ├──────────────────────┤
           │ kernel     4.25 MiB  │  0x440000 bytes  FIT: kernel + DTB + initramfs
 0x04C0000 ├──────────────────────┤
           │ rofs      23.25 MiB  │  0x1740000 bytes read-only squashfs root
 0x1C00000 ├──────────────────────┤
           │ rwfs          4 MiB  │  0x400000 bytes  writable jffs2 (/etc overlay, settings)
 0x2000000 └──────────────────────┘
```

The 64 MiB variant (`openbmc-flash-layout-64.dtsi`) is: u-boot 896 KiB at `0x0`, env 128 KiB at `0xE0000`, kernel 9 MiB at `0x100000`, rofs 32 MiB at `0xA00000`, rwfs 22 MiB at `0x2A00000`. Many AST2600 boards instead use UBI or eMMC layouts. The machine's device tree defines the real partitions; confirm with `cat /proc/mtd`.

## 5.5 Ways to flash the image

```text
 ┌───────────────────────────────────────────────────────────────────────┐
 │ 1. External programmer (blank or bricked board)                       │
 │    PC ──USB──► SPI programmer ──clip/header──► SPI flash              │
 │    Hold the BMC in reset (or mux the flash away) so it doesn't fight  │
 │    $ flashrom -p <programmer> -w obmc-phosphor-image.static.mtd       │
 ├───────────────────────────────────────────────────────────────────────┤
 │ 2. From U-Boot (serial console)                                       │
 │    => tftp <dram-addr> image-bmc                                      │
 │    => sf probe 0:0                                                    │
 │    => sf update <dram-addr> 0 ${filesize}                             │
 ├───────────────────────────────────────────────────────────────────────┤
 │ 3. From BMC Linux                                                     │
 │    $ cp image-bmc /run/initramfs/image-bmc && reboot                  │
 │      (the initramfs shutdown script writes flash after the rootfs     │
 │       is unmounted)                                                   │
 │    or, for one partition: flashcp -v <file> /dev/mtdN                 │
 ├───────────────────────────────────────────────────────────────────────┤
 │ 4. Standard OpenBMC remote update (production path)                   │
 │    Redfish: POST the signed package to the UpdateService push URI     │
 │    bmcweb → phosphor-bmc-code-mgmt → verify signature → write the     │
 │    target slot → activate → reboot                                    │
 ├───────────────────────────────────────────────────────────────────────┤
 │ 5. From the host: a vendor utility (e.g. ASPEED socflash) over a      │
 │    host interface, if the platform permits it                         │
 └───────────────────────────────────────────────────────────────────────┘
```

Methods 1-3 are bench and recovery paths. A production product should use a signed update path (method 4) and the update policy in [Chapter 3](03_Flash_Images_and_Updates.md). Writing raw flash bypasses image verification, so restrict it to authorised lab hardware.

## 5.6 The first instruction: what runs first, and when

When `SRST#` is released, the Arm core fetches its first instruction from its **reset vector**.

**AST2500 (ARM1176), typical:**

```text
 Reset ─► Arm fetches address 0x0000_0000
          0x0 is mapped by hardware to SPI flash CS0
          ─► first instruction = first word of the flash = U-Boot's vector table
             _start:  b reset        @ arch/arm/lib/vectors.S
```

**AST2600 (dual Cortex-A7):**

```text
 Reset ─► internal Boot ROM (mask ROM inside the chip, cannot be changed)
          • reads straps / OTP: boot source (SPI or eMMC)? secure boot on?
          • if secure boot: loads SPL and verifies its signature (documented by socsec)
          • hands control to the first stage from SPI flash (or eMMC)
```

The AST2600 secure-boot details (60/64 KB SPL limit, OTP keys, `revision_id`) are in [ASPEED Chapter 4](../ASPEED_BMC_SoC_Textbook/04_Boot_Security_and_Software.md). The AST2700 is different again: a RISC-V boot MCU runs SPL before the Cortex-A35 starts.

**Strap pins** are board resistors pulled up or down. The chip latches them when reset is released, into hardware-strap registers in the SCU (commonly cited as SCU70 on AST2500 and SCU500/SCU510 on AST2600; verify against your datasheet). Straps select things such as:

- boot source (SPI or eMMC)
- SPI clock speed
- whether the Arm CPU is disabled
- whether the watchdog/ABR dual-boot feature is enabled

## 5.7 Boot stages step by step

```text
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 0: Boot ROM (AST2600; not present as a verifier on AST2500)  ~ms       │
 │  read straps/OTP → (optional) verify signature → hand off to first stage     │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 ▼  running from SPI flash (XIP) or, for verified SPL, on-chip SRAM
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 1: U-Boot SPL / lowlevel_init                                          │
 │  1. Vector table → reset: privileged mode, IRQ/FIQ off, MMU & caches off     │
 │  2. Stack pointer → internal SRAM (no DRAM yet!)                             │
 │  3. Configure SCU: PLLs, CPU/AHB/APB clocks, release peripheral resets       │
 │  4. Speed up FMC SPI timing (slow default → faster, e.g. quad mode)          │
 │  5. *** DRAM init ***: program the SDRAM controller, DDR PHY training        │
 │  6. Disable or kick the watchdog so the board isn't reset mid-boot           │
 │  7. Copy (relocate) full U-Boot from SPI to DRAM and jump to it              │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 ▼  now running from DRAM (fast)
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 2: U-Boot proper                                    ~1-3 s             │
 │  board_init_f → board_init_r: serial console (often UART5, 115200), timers,  │
 │  SPI flash driver, Ethernet (MAC from env/EEPROM), load environment          │
 │  "Hit any key to stop autoboot" → run bootcmd, e.g.:                         │
 │     bootm 20080000   ← FIT in memory-mapped flash (CS0 base + 0x80000)       │
 │  FIT: verify hashes/signature → place kernel, DTB, initramfs in DRAM         │
 │  pass bootargs, e.g. console=ttyS4,115200n8 root=/dev/ram rw                 │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 3: Linux kernel                                     ~3-10 s            │
 │  decompress → MMU on → parse device tree                                     │
 │   (aspeed-bmc-<vendor>-<board>.dts describes GPIOs, I2C, SPI, flash parts)   │
 │  probe drivers: SPI-NOR controller (→ /dev/mtd*), ftgmac100 (net),           │
 │   i2c-aspeed, aspeed-gpio, kcs-bmc (IPMI), aspeed-video (KVM), PWM/tach,     │
 │   ADC, PECI...                                                               │
 │  unpack initramfs → run /init                                                │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 4: OpenBMC initramfs (/init script)                                    │
 │  mount ROFS (squashfs, mtd "rofs")  →  /run/initramfs/ro                     │
 │  mount RWFS (jffs2,   mtd "rwfs")   →  /run/initramfs/rw                     │
 │  overlayfs (ro lower + rw upper)    →  new root                              │
 │  switch_root → /sbin/init (systemd)                                          │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 5: systemd + OpenBMC services                       ~20-120 s          │
 │  dbus-broker (system D-Bus: the backbone of OpenBMC)                         │
 │  phosphor-objmgr (mapper)        ─ finds who owns which D-Bus object         │
 │  phosphor-state-manager          ─ BMC/Chassis/Host state machines           │
 │  entity-manager + dbus-sensors   ─ discover hardware via FRU EEPROMs; sensors│
 │  phosphor-ipmi-host / -net       ─ IPMI over KCS / LAN                       │
 │  bmcweb                          ─ Redfish + web UI (HTTPS)                  │
 │  LED manager, fan control, logging, PLDM/MCTP, obmc-console...               │
 │  xyz.openbmc_project.State.BMC  CurrentBMCState: NotReady → Ready            │
 └───────────────┬──────────────────────────────────────────────────────────────┘
                 ▼
 ┌──────────────────────────────────────────────────────────────────────────────┐
 │ STAGE 6: BMC powers the HOST on (user request or power-restore policy)       │
 │  Redfish ComputerSystem.Reset / ipmitool power on                            │
 │   → phosphor-state-manager → chassis power-on target                         │
 │     (or x86-power-control on many x86 platforms)                             │
 │   → GPIO: pulse POWER_BTN# to the PCH/CPLD                                   │
 │   → PSU main 12V on → host rails → PS_PWROK → host CPU runs its BIOS         │
 │   → BMC monitors POST codes, sensors, SEL, fans, serial-over-LAN             │
 └──────────────────────────────────────────────────────────────────────────────┘
```

Service names and stage durations depend on the image and platform. "Service started" is not the same as "function ready"; see [Chapter 1](01_Hardware_and_Boot.md) §1.5.

## 5.8 Complete timeline (illustrative)

```text
 t=0        AC plugged in → PSU standby 12V/5VSB on
 +1-20 ms   standby buck/LDO rails ramp (3.3V, 1.8V, core, DDR)
 +~50 ms    PWRGOOD → BMC reset released → straps latched
 +0         reset vector: Boot ROM (AST2600) / first SPI instruction (AST2500)
 +~100 ms   SPL: clocks, DRAM training, relocate U-Boot
 +1-3 s     U-Boot: env, net, bootcmd → load FIT
 +3-10 s    Linux kernel: drivers, MTD partitions
 +~1 s      initramfs: overlay rootfs, switch_root
 +20-120 s  systemd: OpenBMC services → BMC state = Ready
 later      BMC powers on the host
```

## 5.9 Safety net: watchdog and dual flash

```text
  Boot from CS0 ──► boot watchdog / ABR armed ──► boot OK? ──yes──► Linux services the WDT
                                                       │no (hang or corrupt image)
                                                       ▼
                                  WDT timeout → reset, swap CS0 ↔ CS1
                                  → boot the golden image from the 2nd flash
```

This is how OpenBMC boards with two flashes survive a bad update. On AST2500 this is commonly done with a watchdog's alternate-boot function; AST2600 adds ABR (alternate boot recovery). Enablement is by strap/OTP and board design, so confirm it on your platform. `phosphor-bmc-code-mgmt` can also manage two image slots.

## 5.10 Quick answers

| Question | Answer |
| --- | --- |
| When does the BMC get power? | As soon as AC is connected, from the PSU **standby** rail (12V_STBY or 5VSB). |
| How is that power divided? | Regulators produce 3.3 V for I/O and flash, 1.8 V for I/O and PLLs, a ~1.1-1.2 V class core rail, and DDR rails (VDDQ, VPP, VTT). Total is a few watts. Exact values are in the datasheet and schematic. |
| What executes first? | AST2600: the internal Boot ROM. AST2500: the first word of SPI flash CS0, which is U-Boot's `_start` vector. |
| When does code start executing? | When reset (`SRST#`) is released after every rail reports power-good. |
| How does the BMC fetch code from SPI automatically? | The FMC memory-maps the flash, so CPU reads become SPI READ commands in hardware (XIP). |
| How is the BMC connected to the flash? | FMC CS0 (and optionally CS1), with CLK, CS# and IO0-IO3 for single, dual or quad SPI. |
| What does flashing do inside the chip? | Erase sets cells to `0xFF`; page-program clears bits to 0. The charge persists without power. |
| How do you flash it? | External programmer, U-Boot `sf`, Linux `/run/initramfs` or `flashcp`, Redfish UpdateService, or a host-side vendor utility. |
| What is the boot order? | ROM → SPL → U-Boot → Linux → initramfs → systemd → OpenBMC services → BMC Ready → host power-on. |

## Lab: see the stages yourself (read-only)

On an authorised lab BMC:

```sh
cat /proc/mtd                     # partitions; compare with the layout in 5.4
dmesg | grep -i -E 'spi|mtd|fmc' | head -n 30
systemctl list-jobs               # what is still starting
busctl get-property xyz.openbmc_project.State.BMC \
  /xyz/openbmc_project/state/bmc0 xyz.openbmc_project.State.BMC CurrentBMCState
```

Capture the serial console during a reboot and mark where each stage begins. In the OpenBMC source tree, read `meta-aspeed`, U-Boot's `arch/arm/mach-aspeed`, and `meta-phosphor/recipes-phosphor/initrdscripts`.

## Review

1. Why does the BMC boot while the server is "off"? **Answer:** it is powered from the PSU's standby rail, not the main rail.
2. Why must NOR flash be erased before writing? **Answer:** programming can only change bits from 1 to 0; only erase returns them to 1.
3. At what flash offset does the kernel FIT start in the 32 MiB static layout? **Answer:** `0x80000`.
4. What is the first code on an AST2600 versus an AST2500? **Answer:** the internal Boot ROM versus U-Boot's vector table at the start of SPI CS0.
5. A board boots the golden image after a bad update. Which mechanism did that? **Answer:** the boot watchdog / ABR swapping to CS1.

Next: [6. Redfish with curl: a cheat sheet](06_Redfish_Curl_Cheat_Sheet.md)
