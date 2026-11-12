# Linux Kernel Debugging: Evidence Before Changes

| Chapter | Focus |
| --- | --- |
| [1. Foundations and evidence](01_Foundations_Labs_and_Evidence.md) | Execution context, safe labs, logs, hypotheses |
| [2. Tracing and latency](02_Tracing_Performance_and_Latency.md) | Dynamic debug, tracepoints, ftrace, perf, eBPF |
| [3. Memory and concurrency](03_Memory_Concurrency_and_Dumps.md) | KASAN, KCSAN, lockdep, crash dumps, symbols |
| [4. Investigation workbook](04_Investigation_Workbook_and_Reference.md) | Reproduction, bisection, interactive debugging, verification |

**Prerequisites:** [C and ownership](../C_Programming_Textbook/00_README.md), Linux process/file basics, architecture fundamentals.

Sources: [kernel debugging guide](https://docs.kernel.org/process/debugging/index.html), [ftrace](https://docs.kernel.org/trace/ftrace.html), [KASAN](https://docs.kernel.org/dev-tools/kasan.html), [lockdep](https://docs.kernel.org/locking/lockdep-design.html), [kdump](https://docs.kernel.org/admin-guide/kdump/kdump.html).

Use a disposable VM or authorized development board. Crash/debug tooling, kernel configuration, architectures, and resource budgets vary. This book does not ask you to crash a production system.
