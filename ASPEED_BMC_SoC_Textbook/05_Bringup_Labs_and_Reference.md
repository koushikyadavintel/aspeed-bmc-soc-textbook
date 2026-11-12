# 5. Bring-up Labs and Reference

This chapter turns the previous four into a working method, then collects exercises and a glossary.

## 5.1 The bring-up ladder

Bring up a BMC board one rung at a time. Do not move up until the current rung has evidence.

| Rung | Question | Evidence you can gather | Typical failure signature |
| --- | --- | --- | --- |
| 1. Power | Are all rails present, in order and stable? | scope or logger on rails and reset | brown-out loops, reset glitch, no activity |
| 2. Clock and reset | Does the SoC leave reset? | reset line level, watchdog pin behaviour | held in reset or periodic resets |
| 3. Straps and boot source | Which boot path was selected? | strap pin levels at reset release | wrong flash selected, boot ROM idle |
| 4. First stage | Does verified SPL run? | UART banner, flash read activity | silence after reset; signature rejected |
| 5. DRAM | Does DRAM train and pass a test? | SPL memory messages, U-Boot memory test | crash right after SPL; random corruption |
| 6. U-Boot | Can you interact and load the kernel? | prompt, `printenv`, flash read | environment missing, wrong FIT address |
| 7. Kernel | Does it reach userspace? | kernel log, root mount | no `stdout-path`, no rootfs |
| 8. Drivers | Do blocks probe? | `dmesg`, `/proc/iomem`, `/proc/interrupts` | probe deferral, missing pinctrl group |
| 9. Services | Do OpenBMC services publish data? | `systemctl`, D-Bus | see the [OpenBMC textbook](../OpenBMC_Textbook/04_Bringup_Workbook_and_Reference.md) |

Record one line of evidence per rung. A written ladder makes a regression obvious and a handover possible.

## 5.2 What to ask ASPEED for

The public sources stop where datasheets begin. When you request documentation under your agreement, ask for:

1. Supply rails, tolerances and the power-up and power-down sequence.
2. Reset sources, reset pin timing and which blocks the watchdog resets.
3. The strap table and boot-source selection.
4. The pin multiplexing table and pin-to-function conflicts.
5. DRAM training requirements, supported densities and layout guidance.
6. OTP map, secure-boot modes and key formats, and the AST2700 Caliptra interaction.
7. Debug access: JTAG, serial and trace support, including the RISC-V boot MCU.
8. The register guide for each block you will program.

## 5.3 Reading a device tree like a hardware engineer

A device-tree node is a compact hardware description. Practise on `aspeed-g6.dtsi` and the g7 files.

```text
bus@1e78a000 {                      // parent window, 4 KiB at 0x1E78_A000
    ranges = <0 0x1e78a000 0x1000>;
    i2c0: i2c@80 {
        #address-cells = <1>;
        #size-cells = <0>;
        reg = <0x80 0x80>;          // offset +0x80 in the window, 0x80 bytes
        compatible = "aspeed,ast2600-i2c-bus";
        clocks = <&syscon ASPEED_CLK_APB2>;
        resets = <&syscon ASPEED_RESET_I2C>;
        interrupts = <GIC_SPI 110 IRQ_TYPE_LEVEL_HIGH>;
        bus-frequency = <100000>;
        pinctrl-names = "default";
        pinctrl-0 = <&pinctrl_i2c1_default>;
        status = "disabled";
    };
    ...
};
```

*Source: `aspeed-g6.dtsi` (torvalds/linux, commit `7be4bc52`), `i2c0` node, comments added.*

Read each property as a hardware fact:

- `reg` is the register window. Add it to the parent's base to get the physical address.
- `interrupts` / `interrupts-extended` is the wire to an interrupt controller. On AST2700 the number is local to INTC0 or INTC1, not a GIC SPI.
- `clocks` / `resets` point at the SCU gate and reset bit; a block with a disabled clock reads as zero or hangs.
- `pinctrl-0` selects the pin-mux group; without it the signal may never leave the package.
- `status = "disabled"` is the default for most nodes. A board's `.dts` enables the blocks that are wired.
- **Names can be off by one.** Controller `i2c0` uses the pin group `pinctrl_i2c1_default`. Node labels are zero-based while pin-group names are one-based. Check the group against the datasheet rather than trusting the label.

## 5.4 Exercises with answers

**1. Compute the I2C controller register address for bus 5 on an AST2600.** `0x1E78_A000 + 0x80 × (5+1) = 0x1E78_A300`. Matches `i2c5` at `@300`.

**2. An AST2700 driver registers hwirq 100 on INTC0. Which GIC SPI does the A35 receive?** The range 0-127 is linear one-to-one, so GIC SPI 100.

**3. Firmware on the SSP wants the same peripheral interrupt. Does it see line 100?** Not by that number. INTC0 hwirq 100 is a local input that the table wires to GIC SPI 100, i.e. to the A35. The SSP's NVIC lines come from the separate range 256-383. How a peripheral interrupt is steered to the SSP is router configuration; take it from ASPEED's SDK rather than guessing, and expect a different line number on the M4.

**4. Estimate the AST2600's peak DRAM bandwidth.** 16 bit × 1600 Mb/s = 25.6 Gb/s = 3.2 GB/s.

**5. A 1 GiB EVB DRAM window starts at `0x4_0000_0000` on AST2700. At what address does it end?** `0x4_0000_0000 + 0x4000_0000 = 0x4_4000_0000` (exclusive). The TF-A and OP-TEE reservations at `0x4_3000_0000` and `0x4_3008_0000` lie inside it, so Linux must not use them (`no-map`).

**6. How big is the OP-TEE reservation?** `0x1000000` bytes = 16 MiB.

**7. Which AST27x0 parts list LTPI?** AST2700, AST2720, AST2750 and the AST1700 expander.

**8. You flash an image built for an AST2600 onto a board fitted with an AST2620. Is that expected to work?** ASPEED lists the AST2620 as pin-to-pin compatible with the AST2600, and the same Cortex-A7 architecture, but the AST2620 page lists a 1.2 GHz A7 and no VGA. Check clocks and any VGA-dependent features. Do not assume equality.

## 5.5 Glossary

| Term | Meaning |
| --- | --- |
| AHB / AHBC | Arm's Advanced High-performance Bus and the AST2600 AHB controller |
| APLIC | Advanced Platform-Level Interrupt Controller (RISC-V) |
| BMCU | AST2700 boot MCU (RISC-V, Ibex) named in the Linux binding |
| Caliptra | OCP open silicon root-of-trust IP integrated in AST2700 |
| FIT | Flattened Image Tree, U-Boot's multi-image container |
| FMC | Flash Memory Controller, boot SPI controller |
| GIC | Arm Generic Interrupt Controller |
| HACE | Hash and Crypto Engine |
| INTC0 / INTC1 | AST2700 primary and secondary interrupt controllers |
| LTPI | LVDS Tunneling Protocol and Interface from OCP DC-SCM |
| NVIC | Nested vectored interrupt controller in a Cortex-M |
| OTP | One-time-programmable memory |
| PSP / SSP / TSP | primary, secondary, tertiary service processors in AST2700 |
| SBC | Secure Boot Controller (AST2600) |
| SCU | System Control Unit: clocks, resets, straps, pin mux |
| SPL | Secondary Program Loader, U-Boot's first stage |

## 5.6 Where to go next

- [DC-SCM textbook](../DC_SCM_Textbook/00_README.md): how these BMCs sit on a modular server and how LTPI works.
- [OpenBMC textbook](../OpenBMC_Textbook/00_README.md): what runs on top.
- [Trusted Firmware-A](../Trusted_Firmware_A_Textbook/00_README.md): the AST2700 EL3 firmware hooks.
- [Armv8-A](../ARMv8_A_Textbook/00_README.md): exception levels and GICv3 behind the A35.
- Primary sources: [ASPEED server products](https://www.aspeedtech.com/), [Linux ASPEED device trees](https://github.com/torvalds/linux/tree/master/arch/arm64/boot/dts/aspeed), [U-Boot](https://docs.u-boot.org/), [socsec](https://github.com/AspeedTech-BMC/socsec).

Return to [contents](00_README.md)
