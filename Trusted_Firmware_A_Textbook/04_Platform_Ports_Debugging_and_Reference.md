# 4. Platform Ports, Build Evidence, and Debugging

## 4.1 Where responsibilities live

The TF-A source separates common stage/runtime code, architectural support, libraries, drivers, platform ports, and host tools. Exact paths change, but common areas include `bl1`, `bl2`, `bl31`, `services`, `lib`, `drivers`, `plat`, and `tools`.

Start with the chosen platform's build description and porting documentation. A platform port supplies memory layout, image loading policy, console setup, CPU topology, interrupt setup, and power-management integration.

Copying a neighboring platform's constants is not bring-up. Establish the SoC's actual memory map, secure attribution, SRAM/DRAM availability, and reset behavior.

## 4.2 Build-time choices are architectural choices

Build flags can select architecture, platform, debug behavior, authentication, dispatcher, payload, and boot flow. An output called `bl31.bin` does not reveal those choices.

A schematic build command is:

```text
make PLAT=<supported-platform> CROSS_COMPILE=<toolchain-prefix> \
     DEBUG=1 all
```

This is intentionally a template, not a runnable board recipe. Read the selected port's documentation for required payloads, dependencies, and targets. Some flows require FIP generation and supplied BL33/BL32 images.

Retain the command/configuration, commit, ELF files, maps, binaries, and toolchain identity. Debug output and assertions can expose information or alter timing; debug firmware is not a production default.

## 4.3 Memory-map checklist

For every component establish:

1. Storage location and image format.
2. Load address and maximum size.
3. Runtime address and permissions.
4. Stack/heap/translation-table areas.
5. Overlap with other resident or temporary components.
6. Secure/non-secure attribution and DMA visibility.

An image can fit in its file allocation but overwrite runtime memory after expansion or relocation. Check the actual footprint.

## 4.4 Failure localization

| Failure | Candidate boundary |
| --- | --- |
| No early UART | Reset entry, clock/pin/UART setup, console configuration |
| Authentication rejects image | Trust anchor, metadata, algorithm/configuration, compatibility |
| BL31 exception | Entry state, mapping, platform initialization, invalid register access |
| BL33 silent | Wrong entry/EL, UART differences, payload failure |
| Secondary CPU fails | Topology, power controller, mailbox/entry, coherency |
| Resume fails | Retained state, warm path, interrupts/timers, cache maintenance |

Use stage markers, exception syndromes, map files, and matching disassembly. Do not add broad logging that prints keys or confidential buffers.

## 4.5 Capstone and answer guide

Choose a documented model or development platform. Draw its complete flow, identify which components are TF-A and which are not, and inspect the built package without programming hardware.

**Success criteria:** explain who authenticates each image, where BL31 remains, how BL33 enters the OS, and which path services a later PSCI request.

**Answer guide:** label missing optional stages explicitly. A model run demonstrates that model/configuration, not the electrical or recovery behavior of a real board.

## Glossary

| Term | Meaning |
| --- | --- |
| BL31 | Common AArch64 EL3 runtime stage |
| FIP | Firmware Image Package |
| SMCCC | Secure Monitor Call Calling Convention |
| PSCI | Power State Coordination Interface |
| TBB | Trusted Board Boot |
| Trust anchor | Root key/state relied on by verification |
| Warm entry | Entry path after selected reset/power transitions |
| Secure payload | Optional protected-world software |

Return to [contents](00_README.md) or continue with [UEFI](../UEFI_Textbook/00_README.md).
