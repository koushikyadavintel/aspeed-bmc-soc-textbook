# PLDM: Platform Data, Control, and Firmware Update

| Chapter | Focus |
| --- | --- |
| [1. Messages and discovery](01_Messages_Identity_and_Discovery.md) | Types, commands, TIDs, instance IDs, capability negotiation |
| [2. Platform data models](02_PDRs_Sensors_Effecters_and_Events.md) | PDRs, entities, numeric/state sensors, controls, events |
| [3. Firmware update](03_Firmware_Update_State_Machine.md) | Update Agent/Device roles, pull transfer, verification, activation |
| [4. Integration workbook](04_OpenBMC_Integration_and_Workbook.md) | libpldm, daemon responsibility, trace diagnosis, glossary |

**Prerequisites:** [MCTP](../MCTP_Textbook/00_README.md), [OpenBMC](../OpenBMC_Textbook/00_README.md), binary parsing.

Sources: [DMTF PMCI](https://www.dmtf.org/standards/pmci), DSP0240 Base, DSP0241 over MCTP, DSP0248 monitoring/control, DSP0257 FRU, DSP0267 update; [OpenBMC PLDM](https://github.com/openbmc/pldm), [libpldm](https://github.com/openbmc/libpldm).

The book explains standard concepts without assuming every endpoint supports every type, command, or revision.
