# Systems Engineering Textbook Library

An organized learning library covering firmware, BMC bring-up, computer architecture, platform-management protocols, C, Linux debugging, and enterprise RAG.

**Compiled: 2026-10-22.** These are independent teaching notes, not official specifications or product documentation. Read explanations to build a mental model, use the exercises to test it, and consult the linked primary sources for exact requirements.

## Library

| Volume | Start here | What you will learn |
| --- | --- | --- |
| C programming | [C textbook](C_Programming_Textbook/00_README.md) | Types, control flow, memory, interfaces, polymorphism, compilation |
| Armv8-A | [Arm textbook](ARMv8_A_Textbook/00_README.md) | AArch64, ABI, exceptions, virtual memory, ordering, interrupts |
| Trusted Firmware-A | [TF-A textbook](Trusted_Firmware_A_Textbook/00_README.md) | Boot stages, trust, EL3 services, PSCI, platform ports |
| UEFI | [UEFI textbook](UEFI_Textbook/00_README.md) | Boot manager, protocols, PI phases, OS handoff, Secure Boot |
| PCI Express | [PCIe textbook](PCIe_Textbook/00_README.md) | Links, enumeration, TLPs, DMA, interrupts, diagnosis |
| OpenBMC | [OpenBMC textbook](OpenBMC_Textbook/00_README.md) | Reset to Redfish, D-Bus, sensors, flash, recovery, bring-up |
| Yocto and image construction | [Build textbook](Yocto_BMC_Build_Textbook/00_README.md) | Recipes, task graphs, packages, rootfs, BSPs, devtool |
| MCTP | [MCTP textbook](MCTP_Textbook/00_README.md) | EIDs, bindings, discovery, fragmentation, Linux sockets |
| PLDM | [PLDM textbook](PLDM_Textbook/00_README.md) | Discovery, PDRs, sensors, effecters, events, firmware update |
| Linux kernel debugging | [Debugging textbook](Linux_Kernel_Debugging_Textbook/00_README.md) | Logs, symbols, tracing, sanitizers, crashes, reproducibility |
| Enterprise RAG | [RAG textbook](Enterprise_RAG_Textbook/00_README.md) | Ingestion, retrieval, evaluation, deployment, Intel public projects |
| RISC-V | [Existing RISC-V textbook](RISC-V_Textbook/00_README.md) | ISA, privilege, vectors, firmware, implementations, reference tables |
| ASPEED BMC SoCs | [AST2600 and AST27x0 textbook](ASPEED_BMC_SoC_Textbook/00_README.md) | CPUs, address maps, interrupt routing, boot and secure boot, bring-up, with 9 diagrams |
| OCP DC-SCM and LTPI | [DC-SCM textbook](DC_SCM_Textbook/00_README.md) | form factors, 168-pin connector, signals, power sequence, FRU, LVDS link, 2.0 vs 2.1, with 10 diagrams |

The [original OpenBMC session guide](OpenBMC_Boot_to_Redfish_Architecture.md) remains available as a shorter instructor-oriented companion.

For presenting Yocto to a BMC team, use the [60-minute slide deck](Yocto_for_BMC_Team_Presentation.md) with its companion [end-to-end flow and diagrams](Yocto_How_It_Works_Flow.md).

## Reading paths

- **New to systems:** C -> Arm Chapters 1-2 -> OpenBMC Chapters 1-2 -> Yocto.
- **BMC bring-up engineer:** OpenBMC -> Yocto -> Linux debugging -> MCTP -> PLDM -> PCIe.
- **Arm firmware engineer:** C -> Arm -> TF-A -> UEFI -> Linux debugging.
- **Management-protocol engineer:** OpenBMC Chapter 2 -> MCTP -> PLDM -> PCIe Chapter 4.
- **AI application engineer:** Enterprise RAG; use the other volumes when working with firmware data.
- **Architecture comparison:** Arm alongside the RISC-V volume. Do not equate Arm EL3 with RISC-V M-mode feature-for-feature.
- **BMC hardware engineer:** ASPEED SoCs -> DC-SCM (Chapters 1-4, then 5 and 6) -> PCIe -> MCTP.
- **Modular-server designer:** DC-SCM Chapters 1-4 -> DC-SCM Chapter 6 (2.0 vs 2.1) -> LTPI (Chapter 5).

Each of the first eleven volumes has four substantive chapters. The ASPEED and DC-SCM volumes are longer (five and seven chapters) and include original diagrams. All volumes have worked examples, exercises with answer guides, a glossary or reference table, and primary-source reading. Chapters can be read independently, but follow the numbered sequence on a first pass.

## Provenance and coverage

The first twelve volumes were organized from the actual locally stored learning conversations, not just their sidebar titles. [Coverage and editorial decisions](CHAT_COVERAGE.md) records the topic mapping and exclusions. Raw conversations, local storage identifiers, internal company instructions, and private source material are deliberately absent.

The ASPEED and DC-SCM volumes were added on request after those conversations, from public sources only: ASPEED's product pages, the Linux and U-Boot sources, ASPEED's public GitHub tools, and the OCP DC-SCM and LTPI specifications. They do not use ASPEED datasheets, which are not public. Each volume's README lists exactly what was read and what was not.

The RISC-V volume predates this expansion and is retained rather than represented as newly revalidated. Its own source snapshot and uncertainty labels still apply. New chapters are original syntheses, not copies of the source manuals or a verbatim transcript.

See [source notes](SOURCES.md) for the checked public references, access limitations, and version-sensitive claims.

## Lab conventions

- Shell examples in the textbooks target **Linux**, a Linux VM, or a supported WSL2 environment unless stated otherwise. They are not PowerShell commands.
- Use authorized lab equipment and a recovery plan. Observation-only commands are preferred; tracing configuration and debugging can still change timing or expose sensitive data.
- Device names, addresses, service names, image layouts, and output filenames are examples unless explicitly tied to a documented platform.
- No chapter instructs you to flash unknown firmware, disable production authentication, probe unknown I2C devices, or expose debugging interfaces to a network.
- Specification requirements, common implementation patterns, and hypothetical examples are different categories. A successful example does not certify a real product.

## Using and improving the library

Start with the learning objectives; after each chapter, explain its worked example without looking. Keep actual board measurements and confidential debugging evidence in an approved private location, not in this repository.

When correcting a chapter, cite a public source, identify the affected version, and state whether the correction changes a general rule or a platform-specific example. Third-party documentation and trademarks retain their owners' rights. Public availability of a linked specification does not imply permission to reproduce it wholesale.
