# 3. Platform Initialization, EDK II, and Trust

## 3.1 UEFI and PI answer different questions

UEFI defines interfaces for the pre-OS/OS boundary. Platform Initialization specifies a common architecture for firmware internals.

In a common PI-style flow:

```text
SEC -> PEI -> DXE -> boot-device selection -> OS loader
```

- SEC handles earliest security/startup responsibilities and initial execution conditions.
- PEI establishes enough permanent resources, particularly memory, for later initialization.
- DXE dispatches drivers and builds much of the UEFI service/protocol environment.
- Boot selection chooses and launches the next boot application.

Actual platforms can arrange early initialization differently, and not all startup code is portable PI code.

## 3.2 EDK II is an implementation framework

EDK II organizes modules, packages, platform descriptions, libraries, and build descriptions. Typical metadata includes INF module descriptions, DEC package declarations, DSC platform composition, and FDF flash-layout descriptions.

A library class expresses an interface that the platform resolves to an implementation. A firmware volume packages firmware files; an EFI executable on the ESP is not the same artifact as an entire firmware volume.

Build success proves neither correct flash placement nor a valid board port. The platform description, CPU architecture, toolchain, and early silicon initialization must agree.

## 3.3 Secure Boot keys and policy

Secure Boot checks selected UEFI executable images against configured authorization and revocation policy. Common concepts include:

| Item | Role |
| --- | --- |
| PK | Platform ownership/policy anchor for key management |
| KEK | Keys authorized for relevant database updates |
| `db` | Authorized signatures/hashes |
| `dbx` | Forbidden/revoked signatures/hashes |

The precise authenticated-variable rules are specified by UEFI. A key name alone is not a complete policy explanation.

Secure Boot does not authenticate all application behavior after OS startup, and does not automatically prove that the platform's earliest immutable boot code and every firmware component were verified.

Measured boot records measurements; Secure Boot enforces authorization. One does not imply the other.

## 3.4 Updates and capsules

Capsules encapsulate update data and metadata for supported update flows. Firmware Management Protocol and OS facilities can participate, depending on implementation.

Checking compatibility, authorization, version policy, installation, power-loss safety, and activation remains necessary. A capsule is not a raw flash dump merely because both contain firmware.

Do not infer that a BMC-specific `.cap.bin` uses standard UEFI capsule semantics. Its consumer must be identified through the actual platform procedure.

## 3.5 Recovery is part of the design

Before modifying firmware, know the recovery mechanism, trust-key ownership, variable-storage handling, and supported rollback behavior. Changing Secure Boot keys can prevent an otherwise valid OS loader from starting.

Use disposable VM firmware/variable files for learning. Do not experiment with a production motherboard's key databases or SPI storage.

## Exercises

1. Why can a valid image signature still be rejected? **Answer:** key not authorized, revocation, policy, or format/architecture mismatch.
2. Does a signed loader prove the kernel and all modules are authorized? **Answer:** only if the subsequent verified chain and policy establish that.
3. What is wrong with "UEFI always starts at SEC"? **Answer:** it conflates an interface standard with a common PI implementation flow.

Next: [Labs and reference](04_Labs_Debugging_and_Reference.md).
