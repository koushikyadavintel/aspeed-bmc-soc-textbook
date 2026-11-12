# 4. Interfaces, Polymorphism, and Build Artifacts

## 4.1 Answering the overloading question

C does not provide C++-style function overloading: two functions cannot share an ordinary external name merely because their parameter types differ. Use distinct names or a deliberately designed generic interface.

Reusing a variable name in an inner scope is **shadowing**, not "variable overloading." It often makes debugging harder.

C11 `_Generic` selects an expression according to a controlling expression's type:

```c
static int add_int(int a, int b) { return a + b; }
static double add_double(double a, double b) { return a + b; }

#define add(a, b) _Generic((a), int: add_int, double: add_double)(a, b)
```

This example deliberately supports two first-argument types. It is not general overload resolution, does not establish a mixed-type policy, and does not prevent overflow in `add_int`. The controlling expression is not evaluated; actual arguments to the selected function still are. Avoid macros that evaluate a side-effecting argument repeatedly.

## 4.2 Runtime polymorphism

A struct can contain a function pointer implementing a shared operation:

```c
#include <stdio.h>

struct sensor {
    double (*read)(const void *context);
    const void *context;
};

static double read_constant(const void *context)
{
    return *(const double *)context;
}

int main(void)
{
    const double temperature = 42.5;
    const struct sensor sensor = {read_constant, &temperature};
    printf("%.1f\n", sensor.read(sensor.context));
    return 0;
}
```

Expected output: `42.5`. The callback and context must agree about the actual object type and lifetime. A production measurement interface should also return availability and error information; the example isolates dispatch mechanics rather than inventing a sensor error policy.

This technique underlies many C driver and service interfaces. It provides dynamic dispatch without classes or automatic lifetime management.

## 4.3 From text to execution

```text
source .c -> preprocessed .i -> assembly .s -> object .o -> executable
```

- The preprocessor expands includes, conditional directives, and macros.
- The compiler performs language analysis and generates target code, commonly represented as assembly.
- The assembler produces machine code and relocation information in an object.
- The linker combines objects and libraries, resolves symbols, and assigns layout.
- A runtime loader may still need shared libraries before a hosted executable can run.

GCC can stop at each stage:

```sh
gcc -std=c17 -E example.c -o example.i
gcc -std=c17 -S example.c -o example.s
gcc -std=c17 -c example.c -o example.o
gcc example.o -o example
```

A header declares an interface; it does not automatically supply its implementation. A missing declaration is a compile-time problem. A declared but unresolved external function is generally a link-time problem. A missing shared library can be a runtime-loader problem.

Static archives package object files. Shared libraries defer some binding until load or runtime. A package adds files and metadata for installation. A firmware image adds a filesystem and other boot components. These are different transformations, expanded in the [Yocto textbook](../Yocto_BMC_Build_Textbook/00_README.md).

## 4.4 Capstone and answer guide

Create a two-file sensor simulator: a public header declares a read function; one implementation returns a sample and status; the main program formats the result.

Success criteria:

1. Builds with C17 warnings enabled.
2. Uses a length or typed object rather than an unbounded string.
3. Distinguishes unavailable from zero.
4. Has no pointer to an expired local.
5. Separately demonstrates a compile failure, a link failure, and a valid executable.

**Answer guide:** put declarations and shared types in the header, include it in both source files, compile each source into an object, then link both. Remove one implementation object to demonstrate an unresolved symbol without changing the valid source.

## Glossary

| Term | Meaning |
| --- | --- |
| Translation unit | Source after preprocessing and its included declarations |
| ABI | Binary contract for calls, types, symbols, and object conventions |
| Lifetime | Interval during which an object exists |
| Ownership | Responsibility for retaining and releasing a resource |
| Relocation | Record used to resolve an address-dependent reference |
| Undefined behavior | Behavior for which C imposes no requirements |
| Dispatch | Selecting an operation implementation |

Return to [volume contents](00_README.md) or continue to [Armv8-A](../ARMv8_A_Textbook/00_README.md).
