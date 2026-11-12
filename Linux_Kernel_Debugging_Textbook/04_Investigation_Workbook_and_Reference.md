# 4. Investigation Workbook and Verification

## 4.1 Interactive debugging

QEMU's GDB stub and KGDB support breakpoints, register/memory inspection, and stepping in supported setups. Their connection path and execution model differ.

Stopping one or all CPUs changes timing. Hardware can continue running while software is stopped; watchdogs and DMA can affect the result. Stepping is excellent for deterministic control flow and sometimes poor for races.

Keep debugger connections local or appropriately isolated. Use the exact target configuration's documentation rather than assuming one command works on every architecture.

## 4.2 Reproduce and bisect carefully

A good reproducer is bounded, records preconditions, and has a clear pass/fail/indeterminate result.

Git bisection narrows a regression only if the good/bad predicate is reliable. A build failure or unrelated boot failure at an intermediate commit is not automatically evidence of the original regression; mark it as untestable when appropriate.

Control kernel config, firmware, device tree, userspace, hardware, load, and timing. Otherwise the "first bad commit" may really be an uncontrolled environment change.

## 4.3 A BMC-focused capstone

Symptom: a protocol-derived temperature becomes unavailable after an endpoint reset.

1. Record target, image, endpoint identity, and reset conditions.
2. Compare kernel/binding status before and after.
3. Check MCTP rediscovery and route/address state.
4. Check PLDM identity/capability/PDR refresh.
5. Check daemon object lifecycle and D-Bus availability.
6. Check Redfish representation.
7. Add narrow tracing only at the first unexplained boundary.

**Answer guide:** the cause may be stale upper-layer state rather than a kernel defect. A Linux-debugging workflow includes proving that the kernel is not the failed layer.

## 4.4 Verify the fix rather than the absence of a crash

Define:

- Original reproducer passes with the intended output.
- Error and recovery paths behave correctly.
- Repeated runs meet an explicit count/duration appropriate to the bug.
- No new warnings, leaks, races, or timeouts appear in applicable checks.
- Instrumentation is removed or returned to its intended configuration.
- Neighboring behaviors, power states, and lifecycle transitions still work.

For a latency bug, compare distributions and tail latency under a defined workload; one faster run is not a measurable improvement.

For a lifetime bug, test cancellation, concurrent operations, removal, and partial initialization failures, not only the happy path.

## 4.5 Review questions

1. Why retain the first warning? **Answer:** later faults may be consequences.
2. Why can a VM pass fail to prove a board fix? **Answer:** hardware paths and timing differ.
3. Does adding a sleep repair a race? **Answer:** generally no; synchronization must establish the required invariant.
4. What does a clean KASAN run prove? **Answer:** only that the exercised execution produced no detected covered error under that configuration.

## Glossary

| Term | Meaning |
| --- | --- |
| Oops | Kernel fault report that may not immediately stop execution |
| Panic | Kernel termination path |
| Tracepoint | Structured instrumentation hook |
| ftrace | Kernel tracing framework |
| KASAN | Kernel Address Sanitizer |
| Lockdep | Runtime lock-dependency validator |
| vmcore | Captured crashed-kernel memory image |
| Reproducer | Procedure/program reliably exercising a symptom |
| Bisect | Search for a regression boundary among revisions |

Return to [contents](00_README.md) or the [library](../README.md).
