# Armv8-A Architecture: A Systems Programmer's Textbook

| Chapter | Focus |
| --- | --- |
| [1. Execution and registers](01_Execution_Registers_and_Instructions.md) | Architecture, AArch64, data movement, branches, flags |
| [2. Calls and exceptions](02_ABI_Exceptions_and_Privilege.md) | ABI, stack, ELs, exception entry/return |
| [3. Memory and ordering](03_Memory_Translation_and_Ordering.md) | Translation, attributes, TLBs, barriers, atomics |
| [4. System integration](04_Interrupts_Virtualization_and_Labs.md) | GIC, virtualization, TrustZone, SIMD, practical investigation |

**Prerequisites:** [C](../C_Programming_Textbook/00_README.md), binary/hex notation. **Baseline:** AArch64 concepts used on common Armv8-A systems. Optional features and later revisions are not universally available.

The [Arm Architecture Reference Manual](https://developer.arm.com/documentation/) is normative. The [AAPCS64](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst) defines procedure-call conventions; architecture and ABI are different contracts.

Follow with [TF-A](../Trusted_Firmware_A_Textbook/00_README.md) and compare against [RISC-V](../RISC-V_Textbook/00_README.md).
