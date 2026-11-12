# 1. Values, Types, and Control Flow

## 1.1 What a program promises

C describes operations on objects and values in an abstract machine. A compiler translates a valid program into a target implementation. It does not promise to turn every plausible-looking source file into predictable behavior.

```c
#include <stdio.h>

int main(void)
{
    unsigned total = 0;
    for (unsigned i = 1; i <= 5; ++i) {
        total += i;
    }
    printf("total=%u\n", total);
    return 0;
}
```

`stdio.h` declares `printf`; `main` is the hosted-program entry function; braces establish blocks; the loop visits 1 through 5. The expected output is `total=15`. A freestanding firmware environment may provide a different startup contract and no standard output.

On a Linux development host with GCC:

```sh
gcc -std=c17 -Wall -Wextra -Wpedantic -Wconversion -g total.c -o total
./total
```

Warnings reveal suspicious code; they do not establish correctness. Read the first warning and fix its cause rather than casting away a mismatch.

## 1.2 Types are operational rules

| Type family | Intended use | Frequent trap |
| --- | --- | --- |
| `_Bool` / `bool` through `stdbool.h` | True/false state | Assuming external binary representation |
| `char` | Character-sized storage | Assuming it is always signed or always 8 bits |
| Signed integer | Values with negative range | Signed overflow is undefined |
| Unsigned integer | Modular arithmetic, masks | Mixed signed/unsigned comparisons |
| Floating point | Approximate real-number computation | Comparing computed results as exact decimal values |
| Pointer | Address-like reference to an object/function | Ignoring lifetime and bounds |

`sizeof(char)` is always 1, but `CHAR_BIT` defines its bit width. `int` is not universally 32 bits. `<stdint.h>` provides exact-width types such as `uint32_t` when the implementation can provide them. `<stddef.h>` supplies `size_t` for object sizes; print it with `%zu`.

Integer promotions affect expressions before assignment. Assigning a result to a large type does not retroactively prevent overflow in smaller operands. Convert intentionally before the operation when needed, and establish that the destination range is sufficient.

## 1.3 Operators and conditions

`=` assigns; `==` compares. `&&` and `||` short-circuit and produce logical results; `&` and `|` operate bitwise. Parenthesize mixed operations when the meaning is not immediately clear.

```c
if (buffer != NULL && length > 0) {
    /* A later access must still fit the actual allocation. */
}
```

The second condition is not evaluated if the first is false. This only checks two conditions; a non-null pointer does not prove that `length` bytes exist.

`if` selects a path, `switch` selects among integral cases, and loops repeat. A missing `break` can fall through into a later case. `continue` skips the remaining body, while `break` exits the nearest loop or switch.

For array loops, the usual invariant is `0 <= i < length`. A loop ending at `i <= length` accesses one extra element if it reads `array[i]`.

## 1.4 Functions and scope

Declare the interface before a call:

```c
static unsigned clamp_percent(unsigned value)
{
    return value > 100U ? 100U : value;
}
```

Parameters are passed by value. A function changes a caller's object by receiving a pointer to it, not by receiving its former value. Arrays used as function parameters adjust to pointer parameters; the function does not automatically receive an element count.

Scope answers where a name can be used. Storage duration answers how long an object exists. Linkage answers whether declarations in different scopes or translation units denote the same entity. These are separate questions. File-scope `static` typically limits linkage; block-scope `static` gives an object lifetime across calls.

## 1.5 Exercise and answer guide

1. Why is `printf("%d", sizeof(int))` incorrect? **Answer:** `sizeof` yields `size_t`; use `%zu`.
2. Why can `-1 < some_unsigned` surprise you? **Answer:** the usual arithmetic conversions may convert the negative operand to unsigned.
3. What does the loop above print? **Answer:** 15; trace the accumulator after each iteration.
4. Does passing an integer to a function let that function change the caller's integer? **Answer:** no; pass a suitable pointer and define mutation in the interface.

Next: [Memory and data structures](02_Memory_and_Data_Structures.md).
