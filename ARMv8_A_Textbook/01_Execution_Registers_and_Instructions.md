# 1. Execution State, Registers, and Instructions

## 1.1 The contract and its implementation

An architecture defines programmer-visible behavior. A microarchitecture implements it with pipelines, caches, predictors, and execution units. Two compliant CPUs can execute the same program with very different performance.

Arm's A-profile targets application-class systems. M-profile and R-profile are different architectural families; their instruction, privilege, and interrupt models must not be substituted into A-profile explanations.

AArch64 is the 64-bit execution state; AArch32 is the 32-bit execution state. A particular CPU or exception level need not support both. "Armv8" alone is not a complete description of a target's instruction/features configuration.

## 1.2 Registers

AArch64 has 31 general-purpose registers `X0` through `X30`. Their `W0` through `W30` names access 32-bit views. Writing a `W` register clears the upper 32 bits of the corresponding `X` register.

The encoding that would be register 31 can mean the stack pointer or zero register depending on the instruction and operand position. `SP` is not an ordinary `X31` register; `XZR` reads as zero and discards writes.

The program counter is not a general-purpose register. AArch64 instructions are fixed at 4 bytes; address-generation instructions and branches provide PC-relative behavior.

## 1.3 Compute, load, store

```asm
add x0, x1, x2
ldr w3, [x4]
str w3, [x5, #4]
```

The first instruction adds register values. The second reads 4 bytes from the address in `X4` and writes `W3`, zeroing the upper half of `X3`. The third stores 4 bytes at `X5 + 4`.

Memory access size comes from the instruction, not the number of useful bits currently in a register. Signed extension and zero extension are different operations. An address must be mapped and permitted, and alignment requirements depend on the access type and control settings.

`mov` can be an alias or pseudo-operation for a suitable architectural encoding. An arbitrary 64-bit constant is not necessarily materialized by one instruction; inspect disassembly rather than counting source mnemonics.

## 1.4 Branches and flags

`B` branches; `BL` also writes a return address into `X30`. `RET` normally branches to the address held in `X30`.

`CMP` is an alias for a flag-setting subtraction whose result is discarded. Condition flags are N, Z, C, V. Signed and unsigned conditions interpret them differently.

```asm
cmp x0, x1
b.lo unsigned_less
```

`b.lo` tests unsigned lower; `b.lt` tests signed less. For subtraction, the carry flag represents the absence of a borrow, which explains unsigned conditions.

`CBZ`/`CBNZ` branch on zero/nonzero without using NZCV; `TBZ`/`TBNZ` test a bit. Choosing the right form depends on data flow, not a rule that every branch must follow `CMP`.

## 1.5 A complete leaf-function example

GNU-style AArch64 assembly:

```asm
.text
.global add_two
.type add_two, %function
add_two:
    add x0, x0, x1
    ret
.size add_two, .-add_two
```

Under the usual AAPCS64 integer calling convention, arguments arrive in `X0` and `X1`, and the result is returned in `X0`. This is a leaf function: it does not overwrite `X30` through a nested `BL`.

Instruction availability, syntax, object format, and ABI still depend on the target toolchain. This is not an x86 program and cannot run natively on an arbitrary Windows PC.

## Exercises

1. After writing `W0 = 0xffffffff`, what is `X0`? **Answer:** `0x00000000ffffffff`.
2. Does `ldr x0, [x1]` load the address or data at the address? **Answer:** data, of the instruction's 64-bit width.
3. Can signed and unsigned comparisons disagree for the same bits? **Answer:** yes; interpret the operands' ranges deliberately.

Next: [ABI, exceptions, and privilege](02_ABI_Exceptions_and_Privilege.md).
