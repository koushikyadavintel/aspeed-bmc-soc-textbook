# Trusted Firmware-A: Boot, Trust, and Runtime Services

| Chapter | Focus |
| --- | --- |
| [1. Stages and handoffs](01_Boot_Stages_and_Handoffs.md) | BL1/BL2/BL31/BL32/BL33 and platform variations |
| [2. Chain of trust](02_Images_and_Chain_of_Trust.md) | FIP, authentication, rollback, measured boot |
| [3. Runtime services](03_Runtime_Services_and_PSCI.md) | SMC, SMCCC, PSCI, context management |
| [4. Porting and labs](04_Platform_Ports_Debugging_and_Reference.md) | Source organization, memory maps, build evidence, failure analysis |

**Prerequisites:** [Arm ELs and memory](../ARMv8_A_Textbook/00_README.md), C, boot fundamentals.

Source: [TF-A firmware design](https://trustedfirmware-a.readthedocs.io/en/latest/design/firmware-design.html), [project docs](https://trustedfirmware-a.readthedocs.io/en/latest/), [source](https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git/).

This volume uses the common AArch64 TrustZone model. AArch32 and Realm-enabled flows differ. TF-A is not a universal component of every BMC.
