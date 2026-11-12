# 3. EL3 Runtime Services, SMCCC, and PSCI

## 3.1 The OS still needs firmware

After boot, the normal OS may request CPU on/off, suspend, system reset, or other services requiring platform coordination. BL31 provides a dispatcher and service infrastructure so callers can use a defined interface rather than private register sequences.

The SMC instruction enters a configured exception/firmware path. It is not a C function call: registers, function identifiers, security state, calling width, and return conventions follow the relevant ABI.

SMCCC describes calling conventions. PSCI defines particular power-management operations. TF-A implements services and platform hooks. Keep these three layers separate.

## 3.2 Typical PSCI CPU_ON flow

```text
OS requests CPU_ON(target, entry, context)
 -> configured SMC/HVC conduit
 -> firmware validates request/state
 -> platform power-control operations
 -> target CPU warm-entry path
 -> target begins at authorized entry context
```

A hypervisor can provide an HVC-facing conduit or virtualize PSCI for guests. Direct calls from the normal OS to EL3 are a common arrangement, not the only arrangement.

Validation includes target identity, supported state, entry conditions, and coordination. Success means the operation was accepted according to the interface; the observer still needs to confirm expected CPU behavior.

## 3.3 State machines matter

CPU power state, cluster state, and system state interact. A CPU may be online, transitioning, idle, suspended, or powered off. A request valid in one state can be denied or unnecessary in another.

Platform hooks implement operations against power controllers, interconnects, caches, and interrupt state. Correct cache/coherency handling is essential when bringing a core into or out of participation.

A return from suspend that leaves the timer, GIC state, or memory attributes wrong can produce failures long after the actual firmware mistake.

## 3.4 Context and trust boundaries

EL3 must preserve and restore the caller's architectural state according to its interface. Normal-world arguments are untrusted inputs even when they originate from an OS kernel. A firmware service with unchecked physical addresses can undermine the memory boundary.

Secure payload dispatchers or partition-management components coordinate secure-world execution according to the selected architecture. The details vary; do not assume every TF-A build contains the same trusted OS or dispatcher.

SMC fast/yielding call classifications and service ownership affect allowed behavior and execution expectations. A long hardware operation cannot simply ignore the calling convention's constraints.

## 3.5 Debugging a failed firmware call

Record:

- The interface version and conduit.
- Function identifier and documented argument meanings.
- Calling CPU and target identity.
- Return value/error category.
- State immediately before and after.
- Platform power-controller evidence and warm-entry logs.

Do not diagnose solely from an OS symptom such as "CPU offline." The request can fail in the OS, hypervisor, firmware validation, platform power sequencing, or secondary entry path.

## Exercises and answers

1. Is every SMC a PSCI call? **No:** many service families use SMC conventions.
2. Can a guest's CPU_ON necessarily power a physical core? **No:** a hypervisor may implement virtual CPU lifecycle instead.
3. Does a cold-boot pass validate suspend/resume? **No:** retained state and warm-entry paths differ.
4. Is EL3 ordinary root privilege? **No:** it is a different architectural execution level and trust boundary.

Next: [Platform ports and debugging](04_Platform_Ports_Debugging_and_Reference.md).
