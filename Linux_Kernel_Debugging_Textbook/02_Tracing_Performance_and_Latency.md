# 2. Tracing, Performance, and Latency

## 2.1 Choose the least disruptive observable

| Question | First candidate |
| --- | --- |
| Did a driver report a failure? | Kernel log / focused dynamic debug |
| Which state transitions occurred? | Existing tracepoints |
| Which function path ran? | Filtered function/function-graph tracing |
| Where was CPU time spent? | Sampling with perf |
| Why did a task wait? | Scheduler/lock/I/O events |
| Need a custom correlated view? | Carefully scoped eBPF |

Do not trace every function to answer one narrow device question. Trace volume and instrumentation can change timing enough to hide the problem.

## 2.2 printk and dynamic debug

Logging is good for rare state changes and errors. Excessive logging can alter scheduling, overwhelm storage, or make a serial console the bottleneck.

Dynamic debug can enable selected existing debug callsites when configured. Match a file, module, function, or format narrowly. Check the target's supported controls and restore the prior setting after the experiment.

Do not print raw credentials, complete firmware payloads, or uncontrolled user buffers. Rate limiting protects capacity but can hide repetitive evidence; record when it is active.

## 2.3 Tracepoints and ftrace

Tracepoints expose structured kernel events. ftrace provides event and function-tracing mechanisms through tracefs. On many systems its mount location is `/sys/kernel/tracing`; older paths can appear under debugfs.

Read-only discovery:

```sh
cat /sys/kernel/tracing/available_tracers
head -n 30 /sys/kernel/tracing/available_events
```

These files exist only when configured/mounted and permitted. Their absence is a configuration observation, not proof that the kernel has no tracing facilities.

A controlled trace experiment should:

1. Capture the previous configuration.
2. Choose a narrow event/filter set and bounded buffer.
3. Start tracing just before the reproducer.
4. Stop promptly after the event.
5. Check lost-event indicators and timestamp basis.
6. Restore the original settings.

The book does not provide a broad global tracing-on command because a shared machine can already have another tracing consumer.

## 2.4 CPU time is not wall-clock latency

A slow request can spend little time on CPU while waiting for a bus, lock, worker, timer, or remote endpoint. A CPU profile alone can miss the dominant delay.

For an illustrative request:

```text
1 ms CPU + 80 ms device wait + 4 ms scheduler delay = 85 ms wall time
```

Optimize the 80 ms component only after establishing why it exists. More CPU cores do not necessarily shorten a mandatory hardware timeout.

For `perf`, choose appropriate permissions, events, sampling rate, symbol availability, and workload scope. Results are estimates subject to sampling bias and overhead.

## 2.5 eBPF and instrumentation limits

eBPF can collect structured observations at supported hooks, subject to verifier rules, privilege, kernel features, and tooling. A program loading successfully does not show that its interpretation or event correlation is correct.

Kernel internal functions and layouts are not all stable interfaces. Prefer existing tracepoints where they answer the question. Bounded maps and output, cleanup, and sensitive-data handling are part of a valid experiment.

## Exercise

A request becomes fast when full tracing is enabled.

**Answer guide:** consider a timing-sensitive race, changed scheduling, altered power state, and measurement mistakes. Reduce instrumentation, repeat, and look for an invariant failure rather than declaring the issue fixed.

Next: [Memory, concurrency, and dumps](03_Memory_Concurrency_and_Dumps.md).
