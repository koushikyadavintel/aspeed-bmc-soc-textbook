# 3. Reliable Low-Level C

## 3.1 Undefined, unspecified, and implementation-defined

Undefined behavior imposes no requirements on the implementation: examples include out-of-bounds access, signed overflow, and dereferencing an invalid pointer. A successful run does not show that undefined behavior is absent.

Unspecified behavior allows a set of outcomes without requiring one documented choice. Implementation-defined behavior requires the implementation to document its choice. These categories are not synonyms for "random."

Optimization assumes the source respects C's rules. Turning optimization off can hide symptoms without fixing the program.

## 3.2 Parsing binary data safely

A network or firmware format defines bytes, lengths, endianness, and valid values. It does not define a native C struct layout.

```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

bool read_le16(const uint8_t *data, size_t length, size_t offset,
               uint16_t *result)
{
    if (data == NULL || result == NULL ||
        offset > length || length - offset < 2U) {
        return false;
    }
    *result = (uint16_t)((uint16_t)data[offset] |
                        ((uint16_t)data[offset + 1U] << 8));
    return true;
}
```

This helper targets implementations providing 8-bit `uint8_t` and 16-bit `uint16_t`. It reports failure explicitly; its caller must propagate a meaningful parse error rather than use an unchanged output.

The subtraction form avoids overflowing `offset + 2` during a bounds check. Byte-wise reads avoid unaligned integer-pointer dereferences and host-endian assumptions. For `data = {0x34, 0x12}`, offset zero yields `0x1234`.

Validate in layers: enclosing message length, header fields, command-specific minimum, declared counts, and each variable-length element. Reserved bits and unsupported versions need the protocol's defined handling. Do not accept a short successful response simply because a completion code was present.

## 3.3 Errors are part of the interface

Useful errors distinguish malformed input, unsupported operation, transient unavailability, permission failure, and internal failure. Returning zero for all failures confuses a legitimate measurement with an error.

For system calls, check the return before consuming outputs. `errno` is meaningful only when the function's contract says an error occurred. Capture it before cleanup calls can overwrite it. For operations returning an error value directly, do not assume they use `errno`.

If an operation can partially complete, expose that state. A write accepting some bytes is not equivalent to a full write; a firmware component transferred is not necessarily verified or activated.

## 3.4 Concurrency and device boundaries

`volatile` requests particular treatment of accesses; it is not a lock and does not make ordinary shared-memory races valid. Use the C atomic model, locks, or the relevant operating-system API.

An atomic operation may establish ordering only according to its memory-order argument and the program's synchronization pattern. An acquire operation is not a replacement for thinking about which release it observes.

In kernel code and drivers, use platform accessors and synchronization APIs for MMIO and DMA. A userspace pointer, a CPU virtual address, a physical address, and a device-visible DMA address can be different values. Casting between them does not establish a mapping.

## 3.5 A practical checking ladder

1. Compile with warnings and inspect every diagnostic.
2. Add unit tests for boundaries and error paths.
3. On a supported development compiler, use AddressSanitizer and UndefinedBehaviorSanitizer.
4. Use a separate ThreadSanitizer build for applicable threaded userspace programs.
5. Review ownership and protocol invariants that tools cannot infer.

Sanitizers change runtime behavior, require support, and do not detect every defect. Do not assume a target firmware image can accommodate their memory overhead.

## Review questions

- Why is casting a packet pointer to `struct header *` risky? **Answer:** bounds, alignment, padding, byte order, and object-access rules may all disagree.
- Is a 100% passing test suite proof of no undefined behavior? **Answer:** no; tests cover executions, not all possible paths.
- Does `volatile int ready` safely publish another thread's buffer? **Answer:** no; use a correct synchronization protocol.
- Why test offset `SIZE_MAX`? **Answer:** it exposes overflow-prone bounds checks without needing a huge allocation.

Next: [Interfaces and builds](04_Interfaces_Builds_and_Review.md).
