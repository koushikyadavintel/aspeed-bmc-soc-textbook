# C Programming for Systems Work

Learn enough C to reason about firmware services, interfaces, memory ownership, binary data, and build artifacts.

| Chapter | Focus |
| --- | --- |
| [1. Values and control flow](01_Values_and_Control_Flow.md) | Translation units, types, operators, decisions, loops, functions |
| [2. Memory and data structures](02_Memory_and_Data_Structures.md) | Arrays, pointers, strings, allocation, structs, files |
| [3. Reliable low-level C](03_Reliable_Low_Level_C.md) | Undefined behavior, binary parsing, errors, concurrency boundaries |
| [4. Interfaces and builds](04_Interfaces_Builds_and_Review.md) | Polymorphism, overloading, headers, compiler/linker stages, labs |

**Prerequisites:** basic computer use. **Baseline:** C17 examples; `_Generic` comes from C11. Optional later C features are not assumed.

**Outcomes:** explain pointer lifetime, parse bounded data without alignment assumptions, distinguish compilation from linking, and explain why C has neither ordinary function overloading nor virtual classes.

Primary reading: [GCC compilation stages](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html), [WG14 documents](https://www.open-std.org/jtc1/sc22/wg14/www/docs/). The [collection source notes](../SOURCES.md) distinguish drafts from published standards.

Next: [Chapter 1](01_Values_and_Control_Flow.md).
