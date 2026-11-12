# Chat-to-textbook coverage

The workspace's saved learning conversations were read to identify the actual questions, explanations, and follow-up topics. Repeated partial responses were consolidated; an uncompleted answer was not treated as evidence that an explanation had been delivered.

## Topic mapping

| Conversation topic | Coverage |
| --- | --- |
| Boot sequence and architecture overview | [OpenBMC](OpenBMC_Textbook/00_README.md), especially reset-to-userspace and the sensor-to-Redfish trace |
| Linux kernel debugging basics | [Linux kernel debugging](Linux_Kernel_Debugging_Textbook/00_README.md) |
| Learn PCIe from scratch | [PCIe](PCIe_Textbook/00_README.md) |
| MCTP learning resources | [MCTP](MCTP_Textbook/00_README.md) |
| Learn PLDM from scratch | [PLDM](PLDM_Textbook/00_README.md) |
| OpenBMC internals learning guide | [OpenBMC](OpenBMC_Textbook/00_README.md) |
| Learn UEFI from scratch | [UEFI](UEFI_Textbook/00_README.md) |
| Learn Trusted Firmware-A basics | [TF-A](Trusted_Firmware_A_Textbook/00_README.md) |
| Learn ARMv8-A architecture basics | [Armv8-A](ARMv8_A_Textbook/00_README.md) |
| Intel AI for Enterprise RAG overview | [Enterprise RAG](Enterprise_RAG_Textbook/00_README.md), including the public repository migration |
| BMC flash image architecture | [OpenBMC Chapters 3-4](OpenBMC_Textbook/03_Flash_Images_and_Updates.md), with build-side details in [Yocto](Yocto_BMC_Build_Textbook/00_README.md) |
| Learn C programming concepts | [C](C_Programming_Textbook/00_README.md), including the specific polymorphism/overloading follow-up |
| Organizing study materials | [C compilation](C_Programming_Textbook/04_Interfaces_Builds_and_Review.md), [Yocto task graph](Yocto_BMC_Build_Textbook/02_From_Source_to_Image.md), [component workflow](Yocto_BMC_Build_Textbook/03_Public_BSP_Walkthrough.md), [image analysis](OpenBMC_Textbook/03_Flash_Images_and_Updates.md) |
| Use ghcp on phone | Scope note below; not a firmware subject |

The existing [RISC-V volume](RISC-V_Textbook/00_README.md) is included as the library's original textbook, independently of the screenshot topics.

## Editorial corrections

- A BMC can manage an off host only while the BMC has its required power and working resources. "Always on" is not an unconditional electrical guarantee.
- MCTP fragmentation arithmetic must account for the actual packet payload limit. The message-type byte begins the message; it is not a new header repeated in every continuation fragment.
- MCTP EIDs, physical bus addresses, PCIe BDFs, and PLDM TIDs are different identifiers.
- A userspace sensor program does not directly call the kernel's `i2c_transfer()` function. A possible call chain must respect the userspace/kernel boundary.
- HTTP `POST` and power-on self-test are unrelated meanings of the same word. An update reference without its procedure is ambiguous.
- A capsule, filesystem image, and raw flash dump are not interchangeable.
- An ordinary nested AArch64 call must preserve its own return address before using `bl`.
- Enterprise RAG's older repository and newer repository do not have identical deployment assumptions. Hardware and software claims are release-specific.

## Public-content boundary

One conversation mixed public build-system questions with company-internal workflow material. Only the general, publicly documented mechanisms were carried forward. Internal repository names, private release URLs, branch-to-product mappings, scripts, and internal deployment procedures were not included. The public NXP BSP README was checked separately; it was not replaced with a private vendor workflow.

The phone-access conversation is an account/device-policy question, not enough material for a technical textbook. Its reusable guidance is: use supported clients and follow the organization's account, device-management, and data-handling policies; do not copy work chats or credentials to personal devices without permission. This library makes no claim that a particular employer permits a particular mobile workflow.

## Limits

The coverage is of the named, recoverable learning conversations in this workspace, plus the existing RISC-V files. It does not claim access to every chat in every application, missing attachments, or deleted conversations. Commands were not executed on a real BMC, Arm model, PCIe endpoint, Kubernetes cluster, or Yocto build host during authoring; the final validation checks document structure, local links, and publication contents, not hardware certification.
