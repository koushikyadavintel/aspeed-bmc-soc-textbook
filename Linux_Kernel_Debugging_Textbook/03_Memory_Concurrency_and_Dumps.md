# 3. Memory Bugs, Concurrency, and Crash Dumps

## 3.1 Match the detector to the failure

| Tool | Main purpose | Important limit |
| --- | --- | --- |
| KASAN | Out-of-bounds/use-after-free detection | Mode/architecture/overhead constraints |
| KMSAN | Uninitialized-value detection | Supported configurations only |
| KCSAN | Data-race detection | Sampling and memory-model limits |
| Lockdep | Lock dependency/context checking | Reports observed dependency patterns |
| UBSAN | Selected undefined operations | Not a complete C correctness proof |
| kmemleak | Potential memory leaks | Heuristic reachability and configuration limits |

Enable one suitable diagnostic configuration rather than assuming every detector can be combined on a constrained BMC.

## 3.2 Reading KASAN evidence

KASAN reports can identify the bad access, allocation/free stacks, object boundaries, and access size. Generic, software-tag-based, and hardware-tag-based modes differ in support and overhead.

Use the earliest meaningful report. A use-after-free can later appear as a bogus pointer, corrupted list, or unrelated device crash. Repair the ownership/lifetime protocol, not just the line that dereferenced the stale object.

A missing report does not prove memory safety: the problematic execution may not have occurred, the mode may not cover it, or memory might be accessed outside the detector's scope.

## 3.3 Locking and races

A deadlock can involve lock order, missing completion, interrupt context, or a worker waiting for itself indirectly. A race can exist even when a particular run completes.

Lockdep tracks dependencies and can detect potential cycles before the exact deadlock happens. KCSAN helps find unsynchronized access patterns. Their reports still require context-sensitive analysis.

Changing a variable to `volatile` is not a valid general race fix. A correct fix establishes ownership, locking, atomic ordering, or a documented lifetime mechanism such as the relevant reference-count/RCU design.

## 3.4 Crash capture

Kdump reserves resources for a capture kernel and uses kexec-based transition to preserve/analyze the crashed kernel's memory. The capture kernel can expose `/proc/vmcore`.

Setup depends on architecture, kernel configuration, memory reservation, bootloader, storage/network paths, and operational policy. A small BMC may not have enough resources for a conventional setup.

Do not trigger a deliberate panic on a production machine to "see whether it works." Validate capture through an approved disposable-lab procedure.

A crash dump can contain credentials, documents, keys, and customer data. Restrict it like a memory disclosure, not like an ordinary public log.

## 3.5 Symbols and address translation

Analyze with exact matching kernel/module symbols and build information. KASLR, relocations, modules, and architecture affect addresses. A raw address fed to the wrong `vmlinux` can produce a convincing but incorrect function name.

Source line attribution is also affected by optimization and inlining. Keep disassembly and data-flow reasoning alongside source.

Tools such as `crash` or GDB can inspect dumps when supported. A tool opening a dump is not proof that every structure was interpreted with the right version/layout.

## Worked investigation

A driver crashes on removal while a periodic worker exists.

**Hypothesis:** removal frees state before the worker is cancelled and synchronized.

**Test:** inspect work scheduling, cancellation semantics, reference ownership, and KASAN evidence in a lab; reproduce removal under controlled load.

**Fix criterion:** no worker can access released state; repeated removal/reprobe and failure paths pass. Adding a delay before free is not a reliable ownership fix.

Next: [Investigation workbook](04_Investigation_Workbook_and_Reference.md).
