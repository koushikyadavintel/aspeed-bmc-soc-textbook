# ASPEED BMC SoCs: AST2600 and the AST27x0 Family

A hardware-level study guide to ASPEED's baseboard-management SoCs, built only from public sources: ASPEED's product pages, the Linux kernel device trees and bindings, U-Boot, and ASPEED's public GitHub tools.

| Chapter | Focus |
| --- | --- |
| [1. Family and generations](01_Family_and_Generations.md) | AST2500 to AST2700, the AST2620/2720/2750 variants, the AST1700 expander |
| [2. AST2600 hardware](02_AST2600_Hardware.md) | CPUs, fabric, address map, storage, network, host and management I/O, security engines |
| [3. AST27x0 hardware](03_AST27x0_Hardware.md) | Four processors, two bus domains, interrupt routing, mailboxes, LTPI, AST1700 |
| [4. Boot, security and software](04_Boot_Security_and_Software.md) | Secure-boot chains, TF-A/OP-TEE hooks, Linux and U-Boot support, SDK repositories |
| [5. Bring-up labs and reference](05_Bringup_Labs_and_Reference.md) | Evidence-driven bring-up, exercises with answers, glossary |
| [6. AST2600 vs AST27x0 comparison](06_AST2600_vs_AST27x0_Comparison.md) | Side-by-side table, porting checklist, symptom map |

**Prerequisites:** [C](../C_Programming_Textbook/00_README.md), [Arm basics](../ARMv8_A_Textbook/00_README.md), and the [OpenBMC](../OpenBMC_Textbook/00_README.md) overview. The AST2700 boot chain connects to [TF-A](../Trusted_Firmware_A_Textbook/00_README.md). The DC-SCM link is covered in the [DC-SCM textbook](../DC_SCM_Textbook/00_README.md).

## Images

Nine original diagrams are in [images/](images). Every diagram is drawn from the public sources cited in its footer. They are not ASPEED documents, and nothing is copied from a datasheet.

| Image | Used in |
| --- | --- |
| [01 family comparison](images/01_family_comparison.svg) | Chapter 1 |
| [09 AST27x0 variants](images/09_ast27x0_variants.svg) | Chapter 1 |
| [02 AST2600 block diagram](images/02_ast2600_block_diagram.svg) | Chapter 2 |
| [03 AST2600 address map](images/03_ast2600_address_map.svg) | Chapter 2 |
| [04 AST2600 boot flow](images/04_ast2600_boot_flow.svg) | Chapters 2, 4 |
| [05 AST2700 block diagram](images/05_ast2700_block_diagram.svg) | Chapter 3 |
| [06 AST2700 address map](images/06_ast2700_address_map.svg) | Chapter 3 |
| [07 AST2700 interrupt routing](images/07_ast2700_interrupt_routing.svg) | Chapter 3 |
| [08 AST2700 boot flow](images/08_ast2700_boot_flow.svg) | Chapter 4 |

## What this volume cannot give you

ASPEED's datasheets and programming guides are distributed under registration or NDA, and the author did not have them. So this volume does not contain register-level programming details, strap tables, pin multiplexing tables, power-rail sequences, or electrical limits for the SoC pins.

What it does give you is the **structure** of the chips: which processors exist, where each peripheral lives in the address space, how interrupts reach each processor, what boots first, what is verified, and which parts mainline Linux already describes. That structure is enough to read a device tree, plan a bring-up, and ask the right question of ASPEED's SDK documents.

## Source snapshot

| Source | Version used |
| --- | --- |
| ASPEED product pages (AST2500/2600/2620/2700/2720/2750/1700) | fetched 2026-10-22 |
| Linux kernel | `torvalds/linux` commit `7be4bc52fd9e0e55dc9a2e0232b89427d2c4b614` (2026-10-22) |
| U-Boot | `u-boot/u-boot` commit `ece349ade2973e220f524ce59e59711cc919263f` (2026-07-06) |
| ASPEED secure-boot tool | `AspeedTech-BMC/socsec` README (2026-10-22) |

Kernel device-tree contents change often. Re-check the files named in each chapter against your own tree before relying on an address.

## Conventions

- **Documented** means a public source states it. **Inferred** means it follows from device-tree nodes or naming but no document says it outright. Both are labelled.
- A product page that does not list a feature does not prove the silicon lacks it. A device-tree node that is absent does not prove the hardware lacks the block. It means mainline Linux does not describe it yet.
- Addresses are written `0x1E78_A000` with underscores for readability.

Next: [Chapter 1: Family and generations](01_Family_and_Generations.md)
