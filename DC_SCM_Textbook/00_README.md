# OCP DC-SCM and LTPI: A Hardware Study Guide

The Datacenter Secure Control Module (DC-SCM) specification defines a small pluggable card that holds a server's BMC and security parts, and the connector (DC-SCI) that joins it to the motherboard. This volume explains the hardware, the signals, the power sequence, the LVDS link (LTPI) that carries slow signals, and the difference between **DC-SCM 2.0 and 2.1**.

| Chapter | Focus |
| --- | --- |
| [1. Architecture and roles](01_Architecture_and_Roles.md) | HPM, SCM, DC-SCI, single and dual node, "Plug-and-Code" |
| [2. Mechanical and connector](02_Mechanical_and_Connector.md) | HFF (EFF, IFF), VFF, SFF-TA-1002 4C+ connector, PCB thickness options, pin regions |
| [3. DC-SCI signals](03_DC_SCI_Signals.md) | PCIe, SPI, eSPI, NC-SI, I2C/I3C, USB, PECI, JTAG, SGPIO and their rules |
| [4. Power, boot and FRU](04_Power_Boot_and_FRU.md) | Power states, discovery sequence, electrical limits, HPM FRU record |
| [5. LTPI](05_LTPI.md) | LVDS electrical, frames, channels, training, errors, reference IP |
| [6. DC-SCM 2.0 vs 2.1](06_DC_SCM_2_0_vs_2_1.md) | The full difference, compatibility checklist, LTPI revisions |
| [7. ASPEED BMCs on DC-SCM](07_ASPEED_on_DC_SCM_and_Review.md) | AST2600 and AST2700 placement, design review checklist, exercises, glossary |

**Prerequisites:** [PCIe](../PCIe_Textbook/00_README.md) and [MCTP](../MCTP_Textbook/00_README.md) basics, plus the [ASPEED SoC textbook](../ASPEED_BMC_SoC_Textbook/00_README.md) for the BMC side.

## Images

Ten original diagrams are in [images/](images). They are redrawn from the specification text and cite their sources. No figure is copied from the OCP documents; the specification's own figures are the authority for dimensions.

| Image | Used in |
| --- | --- |
| [01 system overview](images/01_dcscm_system_overview.svg) | Chapter 1 |
| [02 dual node](images/02_dcscm_dual_node.svg) | Chapter 1 |
| [03 form factors and connectors](images/03_dcscm_form_factors.svg) | Chapter 2 |
| [04 connector pin regions](images/04_dcsci_connector_regions.svg) | Chapters 2, 3 |
| [05 power sequence](images/05_dcscm_power_sequence.svg) | Chapter 4 |
| [06 LTPI electrical](images/06_ltpi_electrical.svg) | Chapter 5 |
| [07 LTPI frame pipeline](images/07_ltpi_frame_pipeline.svg) | Chapter 5 |
| [08 LTPI training state machine](images/08_ltpi_training_state_machine.svg) | Chapter 5 |
| [09 DC-SCM 2.0 vs 2.1](images/09_dcscm_2_0_vs_2_1.svg) | Chapter 6 |
| [10 ASPEED mapping](images/10_aspeed_to_dcscm_mapping.svg) | Chapter 7 |

## Source snapshot and limits

| Document | Version read | Notes |
| --- | --- | --- |
| OCP DC-SCM Specification | **Revision 2.1, Version 1.1** | PDF linked from Antmicro's DC-SCM carrier-card repository |
| OCP DC-SCM 2 LTPI Specification | **Revision 1.2, Version 1.0 RC3** (11 Aug 2025) | PDF linked from the OCP LTPI IP repository's guide; an **RC3** copy |
| OCP LTPI IP User Guide | Version 1.2 | `opencomputeproject/HWMgmt-Module-DCSCM-LTPI`, MIT code and CC BY 4.0 documents |
| ASPEED product pages | fetched 2026-10-22 | see the [ASPEED SoC volume](../ASPEED_BMC_SoC_Textbook/00_README.md) |

**Important limits.**

- The DC-SCM **2.0** document itself was not available to me. The 2.0-to-2.1 differences in Chapter 6 come from the **revision-history table inside the 2.1 document**, cross-checked against the 2.1 body text. They are as reliable as that table, and it records changes, not every unchanged item.
- OCP's own specification pages returned errors during research, so I used the PDFs that other OCP-linked repositories publish. Check opencompute.org for the current revision before designing hardware.
- The specs are released under the Open Web Foundation Final Specification Agreement (OWFa 1.0); trademarks (I2C, I3C, USB, PCIe, eSPI) belong to their owners. This volume is an independent study text, not an OCP document.
- This is a learning guide, not a compliance reference. Dimensions, pinouts and timing for a real design must come from the specification and its pinout spreadsheet.

Next: [Chapter 1: Architecture and roles](01_Architecture_and_Roles.md)
