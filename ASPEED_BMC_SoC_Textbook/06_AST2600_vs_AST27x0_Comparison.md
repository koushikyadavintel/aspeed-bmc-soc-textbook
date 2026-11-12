# 6. AST2600 vs AST27x0: Side-by-Side Comparison

This chapter condenses Chapters 1-5 into one comparison and a porting checklist. Same conventions apply: **documented** facts come from public sources; **inferred** items are labelled.

## 6.1 Mental model

| Generation | Chip | One line |
| --- | --- | --- |
| 6th | AST2500 | Arm11, DDR3/DDR4 |
| 7th | AST2600 | 2× Cortex-A7 (32-bit) + Cortex-M3, DDR4, 28 nm |
| 8th | AST2700 / 2720 / 2750 | 4× Cortex-A35 (64-bit) + 2× Cortex-M4 + RISC-V boot MCU, DDR5, 12 nm |

AST2600 to AST2700 is a far bigger jump than AST2500 to AST2600. The ISA changes from Armv7-A to Armv8-A (AArch64), memory moves to DDR5, the interrupt architecture changes, the boot chain gains a new processor and a hardware root of trust (Caliptra) arrives.

## 6.2 AST2600 summary

- **Compute:** 2× Cortex-A7 with TrustZone, plus an embedded Cortex-M3; Arm GIC at `0x4046_1000` and SCU interrupt aggregators at SCU `+0x560`/`+0x570`.
- **Memory:** DDR4-1600, 16-bit: 16 × 1600 / 8 = **3.2 GB/s**, shared by CPUs, video/KVM, VGA frame buffer and DMA. EVB DRAM at `0x8000_0000`.
- **Fabric:** one flat AHB/APB window `0x1E60_0000`-`0x1E7A_xxxx`; I2C bus N at `0x1E78_A000 + 0x80×(N+1)`. MAC numbering is not address-monotonic (MAC1 `0x1E68_0000` sits above MAC2 `0x1E67_0000`).
- **SCU** `0x1E6E_2000`: clocks, resets, straps, pin mux, silicon ID (`+0x14`), SMP release (`+0x180`).
- **Storage:** FMC `0x1E62_0000` (boot SPI), SPI1/SPI2, SD ×2, eMMC.
- **Host-facing:** LPC with KCS1-4/iBT/snoop, eSPI (silicon; not in `aspeed-g6.dtsi`), VUART ×4, PCIe 2D VGA + GFX + video engine, USB 2.0 vHub.
- **Management I/O:** 16× I2C, 6× I3C, PECI, GPIO/SGPIO, ADC ×2, PWM/TACH, FSI ×2, WDT ×4, UART1-9.
- **Security:** SBC `0x1E6F_2000`, HACE, ACRY, OTP. ROM verifies a `socsec`-signed SPL in SRAM (≤60 KB; 64 KB incl. 512 B signature on A1+), with `--revision_id` 0-64 anti-rollback.
- **Sibling:** AST2620, pin-compatible, 1.2 GHz A7, no VGA listed.

## 6.3 AST27x0 summary

- **Processors:** PSP = 4× Cortex-A35 @ 1.6 GHz (Linux); SSP and TSP = Cortex-M4 @ 400 MHz; BMCU = Ibex RISC-V running SPL in M-mode.
- **Caches (derived from DT):** L1I 2-way, L1D 4-way, shared 512 KiB L2 8-way. GICv3 distributor `0x1220_0000`; PSCI over SMC.
- **Domains:** `soc0` ("Main Domain", `0x1000_0000`, SCU0 `0x12C0_2000`) and `soc1` (IO side, `0x1400_0000`, SCU1 `0x14C0_2000`); two pinctrl blocks; 15 UARTs (EVB console UART12 at `0x14C3_3B00`).
- **Memory:** DDR5-3200, 16-bit = **6.4 GB/s**; DRAM at `0x4_0000_0000`; TF-A (`0x4_3000_0000`, 512 KiB) and OP-TEE (`0x4_3008_0000`, 16 MiB) reserved `no-map`.
- **Interrupts:** INTC0 hwirq 0-127 → GIC SPI 0-127; 256-383 → SSP NVIC 0-127; 426-553 → TSP NVIC 0-127; INTC1 cascades plus extra INTC1 instances over LTPI. The same peripheral has different IRQ numbers on different cores.
- **IPC:** mailboxes mbox0/1 (soc0) and mbox2 (soc1) plus software interrupts; no public message protocol.
- **Connectivity:** PCIe Gen4, USB 3.2, UFS 3.1, CAN 2.0B, VGA + DP 1.1a, LTPI 1 Gb/s.
- **Boot:** BMCU SPL at flash offset `0x80` → FIT → (inferred) TF-A BL31 → OP-TEE → U-Boot → Linux. Caliptra's exact role is not public.
- **Variants:** AST2720 (pin-compatible, no VGA/iKVM/DP listed), AST2750 (dual-node), AST1700 (LTPI I/O expander, not a BMC).

## 6.4 Side-by-side table

| Dimension | AST2600 | AST27x0 | Why it matters |
| --- | --- | --- | --- |
| Process | 28 nm | 12 nm | Power and performance |
| Main CPU | 2× Cortex-A7, Armv7-A, 32-bit | 4× Cortex-A35, Armv8-A, AArch64 @ 1.6 GHz | New toolchain, `ARCH=arm64`, new userspace |
| Coprocessors | 1× Cortex-M3 | 2× Cortex-M4 @ 400 MHz (SSP, TSP) | Real-time offload with Zephyr |
| First-stage CPU | A7 runs SPL | Ibex RISC-V BMCU runs SPL | RISC-V toolchain and JTAG |
| Privilege model | Armv7 modes + TrustZone | EL0-EL3, TF-A (PSCI), OP-TEE | Full secure-firmware stack |
| DRAM | DDR4-1600, 16-bit, 3.2 GB/s | DDR5-3200, 16-bit, 6.4 GB/s | 2× bandwidth for KVM and DMA |
| DRAM base | `0x8000_0000` | `0x4_0000_0000` | 32-bit address assumptions break |
| Bus structure | One AHB window | `soc0` + `soc1` | `devmem` scripts not portable |
| System control | One SCU | SCU0 + SCU1 | Pinmux/clock/reset split by domain |
| Interrupts | GIC + SCU aggregators | GICv3 + INTC0/INTC1, four targets | IRQ numbers depend on target core |
| IPC | Limited | 3 mailboxes + SW interrupts | Multi-core firmware design |
| Root of trust | SBC + OTP + `socsec` | Caliptra + BMCU | New provisioning flow |
| PCIe | Endpoint (VGA) | Gen4, root-complex capable | BMC can host devices |
| USB | USB 2.0 vHub/EHCI | USB 3.2 xHCI + USB 2.0 vHub | Faster virtual media |
| Storage | SPI NOR, eMMC, SD | + UFS 3.1 | Larger, faster storage |
| Remote I/O | External CPLD for LTPI | Native LTPI + AST1700 | Simpler DC-SCM designs |
| CAN | No | 2.0B | — |
| UARTs | 9 (+4 VUART) | 15 | Console moves (UART12 on EVB) |
| Multi-node | No | AST2750: two nodes | One BMC per two hosts |
| Pin-compatible sibling | AST2620 | AST2720 | Same board, fewer features |
| Linux DT | `arch/arm/.../aspeed-g6.dtsi` | `arch/arm64/.../aspeed-g7-{a35,soc0,soc1}.dtsi` | Mainline still catching up |
| U-Boot | `mach-aspeed/ast2600` | `mach-aspeed/ast2700` + `ibex-ast2700_defconfig` | Two U-Boot builds |

## 6.5 Porting checklist: AST2600 → AST2700

1. **Three toolchains:** AArch64 (A35), Arm Cortex-M (M4s), RISC-V (BMCU).
2. **Image layout:** SPL at flash offset `0x80`, loading a FIT with TF-A, OP-TEE and U-Boot.
3. **Device tree:** pinctrl groups belong to `soc0-pinctrl` or `soc1-pinctrl`.
4. **Interrupts:** confirm the INTC routing range first; unrouted hwirqs never fire.
5. **Memory:** keep Linux off TF-A/OP-TEE `no-map` regions; audit 32-bit address assumptions.
6. **Secure boot:** plan Caliptra provisioning with ASPEED early.
7. **Drivers:** expect the ASPEED SDK kernel for I2C, I3C, MAC, PCIe and video until mainline catches up.
8. **DC-SCM:** LTPI moves from a CPLD into the SoC ([DC-SCM chapter 7](../DC_SCM_Textbook/07_ASPEED_on_DC_SCM_and_Review.md)).

## 6.6 Bring-up symptom map

| Symptom | AST2600, check first | AST2700, check first |
| --- | --- | --- |
| No UART output | Straps, ROM signature check, UART pinmux | BMCU SPL at `0x80`, RISC-V boot, UART12 pins in soc1 |
| Dies after SPL | DDR4 training | DDR5 training, FIT load, TF-A entry |
| Peripheral missing | SCU pinmux, clock gate | Which SCU/pinctrl domain; mainline vs SDK DT |
| No interrupts | GIC/SCU INTC | INTC0/INTC1 range and target core |

## Review

1. AST2600 I2C bus 9 address? **Answer:** `0x1E78_A000 + 0x80×10 = 0x1E78_A500`.
2. AST2700 peak DRAM bandwidth? **Answer:** 16 × 3200 / 8 = 6.4 GB/s.
3. First mutable code on AST2700 runs on? **Answer:** the Ibex RISC-V BMCU.
4. INTC0 hwirq 430? **Answer:** TSP NVIC line 4.
5. Why can't AST2600 SPL grow? **Answer:** ROM verifies and runs it from SRAM; 60/64 KB cap.
6. AST2720 fitted and KVM missing: bug? **Answer:** probably not; no VGA/iKVM listed.
7. Is the AST1700 a BMC? **Answer:** no; it is an LTPI I/O expander.

Return to [contents](00_README.md)
