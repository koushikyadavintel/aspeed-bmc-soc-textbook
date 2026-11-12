# 2. Memory, Pointers, and Structured Data

## 2.1 Objects, addresses, and lifetime

An object occupies storage and has a type. A pointer can designate an object, an element, or the permitted one-past position of an array. A one-past pointer can be used for comparison and iteration but cannot be dereferenced.

```c
int values[3] = {10, 20, 30};
int *second = &values[1];
```

`values` is an array, not a pointer variable. Many expressions convert an array to a pointer to its first element, but `sizeof(values)` measures the array itself in this scope. Inside `void visit(int values[])`, the parameter is a pointer and `sizeof(values)` no longer measures the caller's array.

Automatic objects normally end their lifetime when the block exits. Returning the address of a local automatic variable creates a dangling pointer. Heap allocation extends lifetime until explicit release, but it does not eliminate ownership obligations.

## 2.2 Ownership and allocation

For each pointer-bearing interface, answer:

1. Who allocated the object?
2. Who may mutate it?
3. Who frees it?
4. How long may a borrower retain the pointer?

Before allocating `count * sizeof *items`, check multiplication overflow. A checked size is still not a guarantee that allocation succeeds.

```c
#include <stdint.h>
#include <stdlib.h>

int *allocate_readings(size_t count)
{
    if (count == 0 || count > SIZE_MAX / sizeof(int)) {
        return NULL;
    }
    return calloc(count, sizeof(int));
}
```

Here the documented failure result is `NULL`; the caller must distinguish its own invalid-count policy from resource exhaustion if its application needs detailed diagnostics. A production interface can return an error enum and an output pointer.

`free(NULL)` is permitted. Double-free and use-after-free are not. Setting one pointer to `NULL` does not invalidate other aliases to the freed object. With `realloc`, keep the original pointer until success; replacing it directly can leak the allocation on failure.

## 2.3 Strings are bounded data

A C string is a sequence of characters terminated by `'\0'`. A buffer containing bytes is not necessarily a string. `strlen` searches for a terminator; it does not know the allocation length.

For a protocol field described as length plus bytes, preserve that representation unless a string is actually needed. When converting, allocate room for the terminator and reject or deliberately encode embedded zero bytes according to the format.

`snprintf` returns the number of characters that would have been written, excluding the terminator, or a negative encoding error. Compare the successful nonnegative result against the destination size to detect truncation. "The buffer did not overflow" and "the complete value was retained" are different properties.

## 2.4 Structs, enums, and unions

A struct groups named fields; padding may appear between them or at the end. Do not serialize a struct by dumping its memory and assume another compiler or CPU will agree.

An enum names integral states. When reading an external integer, validate that it is a supported state before treating it as an enum value.

A union overlays storage. Track which representation is active through an explicit tag and follow the language rules; it is not a universal permission to reinterpret arbitrary bytes.

```c
enum reading_kind { READING_NUMERIC, READING_UNAVAILABLE };

struct reading {
    enum reading_kind kind;
    double value;
};
```

A richer interface can keep a numeric value and availability separately, just as sensor data models do. Never silently turn unavailable into numeric zero.

## 2.5 Files and resources

Open, operate, check results, and close. A short `fread` can mean end-of-file or error; use `feof` and `ferror` appropriately after a short result. `fclose` can report a write failure that was delayed by buffering. File descriptors, sockets, mutexes, and bus connections also have lifecycles; heap memory is only one resource category.

## Worked exercise

Design a function receiving a packet of `length` bytes and returning an owned copy.

**Answer outline:** reject invalid pointer/length combinations, define the zero-length case, check allocation, copy exactly the established length, and return ownership explicitly. Do not call `strlen` on a binary packet. Test empty data, embedded zeros, maximum permitted length, allocation failure, and repeated release behavior.

Next: [Reliable low-level C](03_Reliable_Low_Level_C.md).
