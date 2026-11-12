# 2. Function Calls, Exceptions, and Privilege

## 2.1 ABI is not the instruction set

The instruction set says what `BL`, `STP`, and `RET` do. AAPCS64 says which registers carry arguments, which a callee must preserve, and how stack alignment works.

Common integer/pointer arguments use `X0`-`X7`; `X0` is used for many scalar results. `X19`-`X28` are callee-saved, `X29` is commonly a frame pointer, and `X30` is the link register. `X18` is platform-specific; do not casually use it as scratch. Vector registers and aggregates have additional rules.

The stack must respect ABI alignment, including 16-byte alignment at public interfaces. A function's frame size and save set depend on what it does.

## 2.2 Why a nested call must preserve its return address

```asm
.text
.global add_then_increment
.type add_then_increment, %function
add_then_increment:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    bl add_two
    add x0, x0, #1
    ldp x29, x30, [sp], #16
    ret
.size add_then_increment, .-add_then_increment
```

The caller's return address initially resides in `X30`. `BL add_two` overwrites it with the address following that call. Saving and restoring `X30` allows the outer function to return correctly.

A bare sequence `bl some_function; ret` is generally not a valid ordinary nested-call wrapper: it loses the original return address. A tail call uses a different control-flow pattern and ABI reasoning.

## 2.3 Exception levels

| Level | Typical use |
| --- | --- |
| EL0 | Applications |
| EL1 | OS kernel |
| EL2 | Hypervisor |
| EL3 | Secure monitor/runtime firmware |

Implementation and system design determine which levels and states exist. Exception level is not a process identity, a CPU number, or a memory address range.

A user syscall commonly uses `SVC`, leading to a configured exception path. Firmware calls may use `SMC`; virtualization can intercept calls depending on configuration. `HVC` is a hypervisor-call instruction. These are interfaces with defined calling conventions, not arbitrary jumps into privileged code.

## 2.4 Exception entry and return

Exceptions include synchronous faults, IRQ, FIQ, and SError categories. On entry, hardware records return state in the target level's exception-link/status registers and dispatches through the vector table configured at that level.

Useful diagnostic registers can include:

- `ELR_ELx`: saved return address.
- `SPSR_ELx`: saved processor state.
- `ESR_ELx`: syndrome describing applicable exception classes.
- `FAR_ELx`: fault address when valid for that exception.
- `VBAR_ELx`: exception-vector base.

Not every field is meaningful for every exception. Decode the syndrome class and validity information before treating an address as the causal access.

`ERET` restores exception return state; it is not the same operation as a subroutine `RET`. Restoring an invalid target state can itself fail.

## 2.5 Privilege and security are different axes

TrustZone separates Secure and Non-secure resources. In the traditional model, the ordinary OS runs Non-secure, while EL3 coordinates transitions and protected services. Secure EL1 software can be an optional trusted OS.

An application at Non-secure EL0 is not "less secure EL1"; privilege and security state answer different questions. Features such as Secure EL2 and later Realm support are revision/implementation-dependent and outside the baseline model.

## Exercise

A data abort reports an address. What else is needed?

**Answer:** execution level/state, instruction and saved PC, syndrome class and access details, validity of FAR, translation context, relevant page-table state, and exact binary/symbols. A faulting address alone cannot identify whether the root cause was a stale pointer, permissions, mapping, or device state.

Next: [Memory and ordering](03_Memory_Translation_and_Ordering.md).
