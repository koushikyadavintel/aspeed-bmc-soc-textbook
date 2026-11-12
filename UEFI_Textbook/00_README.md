# UEFI and Platform Firmware

| Chapter | Focus |
| --- | --- |
| [1. Boot foundations](01_Boot_Manager_ESP_and_Variables.md) | Firmware, ESP, boot entries, image loading |
| [2. Interfaces and handoff](02_Protocols_Services_and_OS_Handoff.md) | Handles, protocols, Boot/Runtime Services, memory map |
| [3. Initialization and trust](03_PI_Phases_and_Secure_Boot.md) | PI architecture, EDK II, Secure Boot, capsules |
| [4. Labs and diagnosis](04_Labs_Debugging_and_Reference.md) | Read-only inspection, firmware development, review |

**Prerequisites:** C and boot concepts. Learn [Arm](../ARMv8_A_Textbook/00_README.md) and [TF-A](../Trusted_Firmware_A_Textbook/00_README.md) when targeting Arm systems; UEFI also exists on other architectures.

Authoritative reading: [UEFI specifications](https://uefi.org/specifications), [EDK II](https://github.com/tianocore/edk2). UEFI pages could not be fetched during authoring; see [access notes](../SOURCES.md). No current-version claim is made.
