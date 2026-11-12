# 1. Foundations, Safe Labs, and Useful Evidence

## 1.1 What makes kernel debugging different?

The kernel manages processes, memory, devices, filesystems, and networking. A kernel defect can affect unrelated applications or the whole machine.

Kernel execution can occur in process context, interrupt handlers, deferred work, and other constrained contexts. Whether code may sleep, which locks are legal, and which memory allocation choices are appropriate depend on context and kernel configuration.

An application's failed read does not prove a kernel bug. The failure can originate in permissions, a bad file descriptor, protocol state, the filesystem, a driver, or hardware.

## 1.2 Build a recovery path first

Use a VM snapshot or documented board recovery method, a known-good kernel/boot option, serial/early console where needed, and sufficient space for logs.

Keep source, configuration, exact `vmlinux`/debug symbols, modules, compiler identity, and image hashes. A kernel version string alone is not sufficient to prove symbol compatibility.

Do not expose a QEMU GDB stub or KGDB path to an untrusted network. A debugger grants powerful control over the guest or target.

## 1.3 Start with observation

On an authorized Linux system:

```sh
uname -a
cat /proc/version
cat /proc/cmdline
dmesg --level=err,warn
journalctl -k -b --no-pager
```

Availability and permissions differ, particularly on minimal BMC images. Save bounded evidence locally. Logs can contain addresses, inventory, and secrets; do not post them unfiltered.

The last log before a hang is not necessarily the cause. Messages can be buffered, rate-limited, dropped, or emitted asynchronously.

## 1.4 Reading a call trace

A useful report can contain:

- Exception/panic/warning type and CPU/task context.
- Faulting instruction and registers.
- Call stack.
- Taint state and loaded modules.
- Kernel/build identity.
- Earlier related warnings.

A warning is not necessarily fatal, and an oops may allow the kernel to continue in a compromised state. Later faults can be consequences. Prefer the earliest relevant report.

Stack traces can be incomplete due to missing unwind information, optimization, corrupted state, or architecture limits. A printed function name is evidence, not proof that it caused the bad input.

## 1.5 Form hypotheses that can fail

Use:

```text
symptom -> controlled reproduction -> evidence -> hypothesis
        -> distinguishing experiment -> result -> revised conclusion
```

Example: "The sensor stops updating after host power-off." Competing hypotheses include legitimate device power loss, daemon policy, a driver timeout, and stale cache.

A useful first experiment compares the hardware/protocol source, daemon status, and API status across the transition. Recompiling the kernel first tests too many things at once.

## Exercise

A stack trace ends in a memory-copy helper. Should you fix that helper?

**Answer:** first inspect its callers, pointer origin, length, lifetime, and the earliest memory-corruption evidence. A generic helper may simply be where an invalid input finally became visible.

Next: [Tracing and latency](02_Tracing_Performance_and_Latency.md).
