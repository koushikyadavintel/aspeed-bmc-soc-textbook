# 4. Interrupts, Virtualization, and System Investigation

## 4.1 Interrupts are routed events

Many Arm systems use a Generic Interrupt Controller. GIC versions differ; learn the version actually implemented.

In a common GICv3 model, the distributor manages shared peripheral interrupts, redistributors support per-CPU interrupt state, CPU interfaces acknowledge/complete interrupts, and an optional ITS translates device events into LPIs.

An interrupt's existence does not prove delivery. Check:

```text
source asserted -> device enable -> controller routing/priority
 -> CPU masking/state -> vector -> handler -> acknowledge/completion
```

Edge-triggered and level-triggered sources have different obligations. Returning from a handler without clearing a level-triggered device condition can immediately retrigger it.

## 4.2 Virtualization

A hypervisor at EL2 can control guest execution, trap selected operations, and apply stage-2 translation. Guest stage 1 translates guest virtual to intermediate physical; stage 2 translates intermediate physical to system physical.

An IOMMU handles device-originated translations; it is not automatically the same thing as a CPU's stage-2 MMU. Virtualizing CPU memory without controlling DMA can leave an isolation gap.

Virtual interrupts and timer virtualization require additional controller and hypervisor support. A feature bit does not establish an entire usable virtualization platform.

## 4.3 SIMD, floating point, and optional features

AArch64 commonly provides FP/Advanced SIMD registers `V0`-`V31`, viewed at different element sizes. The ABI defines preservation and argument rules. Privileged configuration can enable or trap access.

SVE is a separate optional scalable-vector extension, not another name for Advanced SIMD. Cryptography, pointer authentication, memory tagging, and later security features require explicit architectural/implementation support.

Build configuration, runtime detection, kernel support, and ABI must agree. Do not infer every optional instruction from a marketing label.

## 4.4 Lab: inspect generated code

On a Linux host with an AArch64 GNU cross-toolchain:

```sh
aarch64-linux-gnu-gcc -O1 -g -c arithmetic.c -o arithmetic.o
aarch64-linux-gnu-objdump -dr arithmetic.o
```

Use a simple C function such as adding two unsigned long values. Inspect argument registers, result register, instruction widths, and whether the function is a leaf.

Then add a call to an external function. Explain link-register preservation, relocations, and any stack frame. Optimization can change the shape; inspect the actual output instead of requiring one fixed prologue.

The example is a user-space object-code exercise, not a claim that privileged registers can be read from an ordinary process.

## 4.5 Lab: reason through a fault

Given a hypothetical data abort:

1. Identify current EL and security state.
2. Decode the exception class and reported access.
3. Locate the saved PC in matching symbols/disassembly.
4. Establish the pointer's origin and intended mapping.
5. Distinguish translation, permission, alignment, and device-access causes.
6. Propose one minimal test.

**Answer guide:** do not begin by changing page tables. First show which access failed and why the available syndrome supports that hypothesis.

## Glossary

| Term | Meaning |
| --- | --- |
| AArch64 | Arm 64-bit execution state |
| EL | Exception level |
| ABI | Binary-level calling/data contract |
| GIC | Generic Interrupt Controller |
| TLB | Translation lookaside buffer |
| MMIO | Device registers accessed through mapped addresses |
| Stage 2 | Hypervisor-controlled guest physical translation |
| TrustZone | Secure/Non-secure system separation mechanisms |
| PSCI | Standard CPU/system power-management interface |

Return to [contents](00_README.md) or continue with [TF-A](../Trusted_Firmware_A_Textbook/00_README.md).
