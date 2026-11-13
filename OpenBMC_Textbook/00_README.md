# OpenBMC: From Reset to Platform Management

This volume combines the boot-sequence, OpenBMC-internals, BMC-flash-image, and bring-up questions into one connected system.

| Chapter | Focus |
| --- | --- |
| [1. Hardware and boot](01_Hardware_and_Boot.md) | BMC/host boundary, reset, ROM, bootloader, kernel, systemd |
| [2. D-Bus to Redfish](02_DBus_Sensors_and_Redfish.md) | Discovery, inventory, sensors, associations, API translation |
| [3. Images and updates](03_Flash_Images_and_Updates.md) | Storage, containers, persistence, update state, image analysis |
| [4. Bring-up workbook](04_Bringup_Workbook_and_Reference.md) | Evidence-driven diagnosis, labs, acceptance criteria, glossary |
| [5. Power, SPI flash, and boot walkthrough](05_Power_SPI_Flash_and_Boot_Walkthrough.md) | Standby power, SPI wiring and commands, flash layout, flashing methods, first instruction, stage timeline, dual-flash recovery |
| [6. Redfish with curl](06_Redfish_Curl_Cheat_Sheet.md) | Discovery, power control, `ResetType` values, safe curl defaults |

**Prerequisites:** basic Linux and the [C volume](../C_Programming_Textbook/00_README.md). Read the [Yocto volume](../Yocto_BMC_Build_Textbook/00_README.md) for how these artifacts are built.

**Outcomes:** trace a value across layers, distinguish an image from an update payload, identify the earliest failed handoff, and define a measurable bring-up result.

Primary sources: [OpenBMC docs](https://github.com/openbmc/docs), [interface definitions](https://github.com/openbmc/phosphor-dbus-interfaces), [entity-manager](https://github.com/openbmc/entity-manager), [dbus-sensors](https://github.com/openbmc/dbus-sensors), [bmcweb](https://github.com/openbmc/bmcweb). Actual components depend on the image.

The [short session guide](../OpenBMC_Boot_to_Redfish_Architecture.md) is a companion, not a different architecture.
