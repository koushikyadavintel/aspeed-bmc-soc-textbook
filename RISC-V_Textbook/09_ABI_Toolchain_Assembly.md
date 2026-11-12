# Chapter 9 - ABI, ELF, Toolchain, and Assembly Programming

[Index](00_README.md) | Prev: [Ch 8](08_Memory_Model_Atomics.md) | Next: [Ch 10 - Boot, SBI, Firmware, Linux](10_Boot_SBI_Firmware_Linux.md)

**Goals:** Know the calling convention and data layout, ELF/relocation details, how compilers and linkers treat RISC-V (including relaxation), how to write assembly, and how to build and run a bare-metal program.

> Source: the RISC-V ELF psABI document (https://github.com/riscv-non-isa/riscv-elf-psabi-doc) is the authority. Compiler flag spellings change between releases; verify against your GCC/LLVM version **[verify]**.

---

## 9.1 ABI names

An ABI is chosen with `-mabi=`:

| ABI | `int` | `long` | pointer | FP args passed in |
|-----|-------|--------|---------|-------------------|
| `ilp32` | 32 | 32 | 32 | integer regs (soft-float) |
| `ilp32f` | 32 | 32 | 32 | single-precision in `fa*` |
| `ilp32d` | 32 | 32 | 32 | single and double in `fa*` |
| `ilp32e` | 32 | 32 | 32 | RV32E (16 regs), soft-float |
| `lp64` | 32 | 64 | 64 | soft-float |
| `lp64f` | 32 | 64 | 64 | single in `fa*` |
| `lp64d` | 32 | 64 | 64 | single and double in `fa*` |
| `lp64e` | 32 | 64 | 64 | RV64E |

- **The ABI must be compatible with the `-march`:** `lp64d` requires `D`; `ilp32f` requires `F`.
- Linux distributions standardize on **`lp64d`** (64-bit) with `rv64gc`/RVA profiles.

### Data type sizes and alignment (LP64)

| Type | Size | Alignment |
|------|------|-----------|
| `char` (**unsigned by default**!) | 1 | 1 |
| `short` | 2 | 2 |
| `int` | 4 | 4 |
| `long`, `long long` | 8 | 8 |
| pointer | 8 | 8 |
| `float` | 4 | 4 |
| `double` | 8 | 8 |
| `long double` (IEEE binary128) | 16 | 16 |
| `_Float16`/`__fp16` | 2 | 2 |
| `__int128` | 16 | 16 |

- `char` is **unsigned** in the RISC-V psABI (like Arm); portable code must not assume signed `char`.
- On RV64, 32-bit values are kept **sign-extended to 64 bits** in registers, *even `unsigned int`* (so comparisons and `lwu`/`sext.w` conventions work). Callers/callees rely on it for arguments and return values.
- Stack alignment is **16 bytes** at call boundaries (RV32E/ILP32E: 4 bytes).
- Structures follow natural alignment rules; bit-field layout follows the psABI.

## 9.2 Register usage (recap)

| Class | Registers | Preserved across calls? |
|-------|-----------|--------------------------|
| Return address | `ra` | No (caller-saved) |
| Stack pointer | `sp` | Yes |
| Global pointer | `gp` | Unallocatable; fixed by the linker/runtime |
| Thread pointer | `tp` | Unallocatable; fixed by runtime |
| Temporaries | `t0`-`t6`, `ft0`-`ft11` | No |
| Arguments / returns | `a0`-`a7`, `fa0`-`fa7` | No |
| Saved | `s0`-`s11`, `fs0`-`fs11` | **Yes** |
| Vector | `v0`-`v31`, `vl`, `vtype` | No (caller-saved) **[verify details for `vxrm/vxsat`]** |

`t0` is also the **alternate link register** (used by millicode/`Zcmt`-style routines); `t1` is conventionally used by `tail`; `t2` is the `lpad` label register for CFI (`Zicfilp`), `t3`-`t4` appear in PLT stubs.

## 9.3 Calling convention

### Integer and pointer arguments

- First 8 integer/pointer arguments -> `a0`-`a7`; the rest go on the stack.
- Return value -> `a0` (and `a1` for 2*XLEN results).
- Arguments of size <= XLEN occupy one register; size 2*XLEN occupy a register pair (aligned to an even register number if the argument has 2*XLEN alignment); larger aggregates are passed **by reference** (pointer in a register).
- Small aggregates (<= 2*XLEN) go in up to two registers.
- A struct larger than 2*XLEN is returned via a hidden pointer in `a0` (the caller allocates space).

### Floating-point (hard-float ABIs)

- First 8 FP scalars -> `fa0`-`fa7`; when exhausted use integer registers, then stack.
- Structs with 1 or 2 FP members (or an int + a FP) may be passed in FP/int registers ("flattening") - follow psABI rules.
- Returns: `fa0`, `fa1`.
- **Variadic functions:** FP arguments are passed in **integer registers**, like integers, even with `lp64d`.

### Stack frame layout

```
high addresses
+----------------------+  <- sp at function entry (16-byte aligned)
| stack arguments      |  (caller's outgoing args)
+----------------------+  <- sp after caller's call (entry sp)
| saved ra             |
| saved s0 (fp)        |
| saved s1..s11        |
| local variables      |
| outgoing args        |
+----------------------+  <- sp (16-byte aligned)
low addresses
```

- No red zone below `sp`: signal handlers/interrupts may clobber it.
- Frame pointer is `s0/fp` (optional; `-fno-omit-frame-pointer` for stack unwinding or tooling).
- Shadow stack (`Zicfiss`) is separate and holds only return addresses (Chapter 12).

### Prologue/epilogue (-O0 style, leaf-friendly)

```asm
func:
    addi  sp, sp, -32
    sd    ra, 24(sp)
    sd    s0, 16(sp)
    addi  s0, sp, 32          # frame pointer = old sp
    ...
    ld    ra, 24(sp)
    ld    s0, 16(sp)
    addi  sp, sp, 32
    ret
```

### Examples: how args map

```c
long f(int a, long b, double c, char *d, struct S s);
// a -> a0 (sign-extended), b -> a1, c -> fa0 (lp64d), d -> a2, s -> a3 (small) or pointer in a3 (large)
```

## 9.4 ELF files

| Field | Value |
|-------|-------|
| `e_machine` | `EM_RISCV` = **243** |
| `EI_CLASS` | `ELFCLASS32` (RV32) or `ELFCLASS64` (RV64) |
| Endianness | `ELFDATA2LSB` (little) |
| `e_flags` | bitfield below |

`e_flags`:

| Flag | Value | Meaning |
|------|-------|---------|
| `EF_RISCV_RVC` | `0x0001` | Uses compressed instructions |
| `EF_RISCV_FLOAT_ABI_SOFT` | `0x0000` | Soft-float |
| `EF_RISCV_FLOAT_ABI_SINGLE` | `0x0002` | Single-precision hard-float |
| `EF_RISCV_FLOAT_ABI_DOUBLE` | `0x0004` | Double-precision hard-float |
| `EF_RISCV_FLOAT_ABI_QUAD` | `0x0006` | Quad |
| `EF_RISCV_RVE` | `0x0008` | RV32E/RV64E |
| `EF_RISCV_TSO` | `0x0010` | Requires Ztso |

The linker rejects mixing incompatible ABIs. The **`.riscv.attributes`** section (type `SHT_RISCV_ATTRIBUTES`) records `Tag_RISCV_arch` (e.g., `rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0...`), `Tag_RISCV_stack_align`, and `Tag_RISCV_unaligned_access`. Inspect with `readelf -A file`.

### Sections

| Section | Content |
|---------|---------|
| `.text` | Code |
| `.rodata` | Read-only data |
| `.data` / `.bss` | Initialized / zero-initialized data |
| `.sdata` / `.sbss` | Small data (within +/-2 KiB of `gp`) |
| `.tdata` / `.tbss` | Thread-local storage templates |
| `.got`, `.plt`, `.got.plt` | Dynamic linking |
| `.init_array`/`.fini_array` | Constructors/destructors |
| `.riscv.attributes` | ISA/ABI attributes |

## 9.5 Relocations

Relocations are `Elf_Rela` (explicit addend). Commonly seen:

| Number | Name | Used by |
|--------|------|---------|
| 1 / 2 | `R_RISCV_32` / `R_RISCV_64` | Absolute data |
| 3 | `R_RISCV_RELATIVE` | Dynamic base + addend |
| 4 | `R_RISCV_COPY` | Copy relocation |
| 5 | `R_RISCV_JUMP_SLOT` | PLT/GOT jump slot |
| 16 | `R_RISCV_BRANCH` | Conditional branch (B-type) |
| 17 | `R_RISCV_JAL` | `jal` (J-type) |
| 18 | `R_RISCV_CALL` | `auipc+jalr` pair (deprecated in favor of `CALL_PLT`) |
| 19 | `R_RISCV_CALL_PLT` | `auipc+jalr` through PLT |
| 20 | `R_RISCV_GOT_HI20` | `%got_pcrel_hi` |
| 21 | `R_RISCV_TLS_GOT_HI20` | Initial-exec TLS |
| 22 | `R_RISCV_TLS_GD_HI20` | General-dynamic TLS |
| 23 | `R_RISCV_PCREL_HI20` | `auipc` upper |
| 24 / 25 | `R_RISCV_PCREL_LO12_I` / `_S` | Paired with `PCREL_HI20` |
| 26 | `R_RISCV_HI20` | `lui` upper (absolute) |
| 27 / 28 | `R_RISCV_LO12_I` / `_S` | Absolute lower |
| 29-32 | `R_RISCV_TPREL_HI20/LO12_I/LO12_S/ADD` | Local-exec TLS |
| 43 | `R_RISCV_ALIGN` | Alignment padding (relaxation) |
| 44 / 45 | `R_RISCV_RVC_BRANCH` / `RVC_JUMP` | Compressed branches/jumps |
| 51 | `R_RISCV_RELAX` | Marks the preceding reloc as relaxable |

`%pcrel_lo` relocations point at the **label of the `auipc`** whose `%pcrel_hi` they pair with (so the linker knows the hi/lo pair share one PC offset).

### Linker relaxation

Because instruction counts differ by distance, the linker **shrinks** code after layout:

| Source sequence | Relaxed to |
|-----------------|------------|
| `auipc ra; jalr ra` (`call`) | `jal ra` if within +/-1 MiB |
| `auipc t0; addi t0` (`la`) | `addi` from `gp` if in `.sdata` window; or shorter forms |
| `lui; addi` (absolute) | single `addi`/`lui` when addresses fit |
| Alignment `R_RISCV_ALIGN` | Nops removed/adjusted |

Control with `-mrelax`/`-mno-relax` (compiler/assembler) and `--relax`/`--no-relax` (linker); `.option norelax` in assembly. **Gotcha:** setting `gp` itself must be done with `norelax`, otherwise the linker relaxes the `la gp,...` into a `gp`-relative operation of `gp` (circular).

### Global pointer (`gp`) convention

The linker defines `__global_pointer$ = .sdata_start + 0x800`. Data within +/-2 KiB are accessible in one instruction. Startup code **must** initialize `gp`:

```asm
.option push
.option norelax
    la gp, __global_pointer$
.option pop
```

### Code models

| Model | Meaning |
|-------|---------|
| `-mcmodel=medlow` | Code and data in the low 2 GiB or top 2 GiB of the address space (`lui`+`addi`) |
| `-mcmodel=medany` | All code and data within a +/-2 GiB window of the PC (`auipc`); usable at any address. Linux kernel uses this |
| `large` | Experimental for >2 GiB spreading **[verify]** |

### Position-independent code and GOT/PLT

With `-fPIC`, `la sym` becomes `auipc t0, %got_pcrel_hi(sym); ld t0, %pcrel_lo(1b)(t0)`; calls use `call sym@plt`. The GOT slot holds the symbol address.

### Thread-local storage models

| Model | Sequence idea |
|-------|---------------|
| Local-exec | `lui t0,%tprel_hi(v); add t0,t0,tp,%tprel_add(v); lw a0,%tprel_lo(v)(t0)` |
| Initial-exec | Load offset from GOT, add `tp` |
| General-dynamic | `la.tls.gd`; `call __tls_get_addr@plt` |
| TLS descriptors (`-mtls-dialect=desc`) | Faster dynamic TLS via descriptor call **[verify toolchain support]** |

## 9.6 Toolchain overview

| Piece | GNU | LLVM |
|-------|-----|------|
| Compiler | `riscv64-unknown-elf-gcc`, `riscv64-linux-gnu-gcc` | `clang --target=riscv64-...` |
| Assembler | `as` (binutils) | `llvm-mc`, integrated assembler |
| Linker | `ld` | `ld.lld` |
| Disassembler | `objdump -d` | `llvm-objdump -d` |
| C library | newlib (bare metal), glibc (Linux), musl, picolibc | same |
| Debugger | `gdb` (riscv64-unknown-elf-gdb or multiarch) | `lldb` |
| Simulators | Spike (reference), QEMU, Renode, gem5, Verilator models | same |

Common triplets: `riscv64-unknown-elf` (bare-metal newlib), `riscv64-unknown-linux-gnu` (glibc), `riscv64-linux-gnu` (Debian/Ubuntu cross package), `riscv64-linux-musl`, `riscv32-unknown-elf`.

### Installing

- Debian/Ubuntu: `apt install gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu qemu-user qemu-system-misc` (bare-metal: `gcc-riscv64-unknown-elf`).
- Build from source: `git clone https://github.com/riscv-collab/riscv-gnu-toolchain`, then `./configure --prefix=/opt/riscv --with-arch=rv64gc --with-abi=lp64d && make` (newlib) or `make linux` (glibc). Add `--enable-multilib` for multiple arch/ABI libraries.

### Important `-march` rules

```
-march=rv64gc                       # IMAFDC + Zicsr + Zifencei
-march=rv64imafdc_zicsr_zifencei    # explicit (needed in newer GCC when not using 'g')
-march=rv64gcv_zba_zbb_zbs          # add vector and bit-manip
-march=rva23u64                     # profile name (recent toolchains) [verify]
-mabi=lp64d
```

- Since the 2019 ISA split, `Zicsr`/`Zifencei` are separate; GCC >= 12 no longer assumes them for plain `rv64imafd`. Add them or use `g`/`-misa-spec=2.2`.
- `-mtune=`/`-mcpu=` pick scheduling models (e.g., `sifive-u74`, `sifive-p670`, `generic-ooo`, `rocket`) **[verify names]**.
- Misaligned access policy: `-mstrict-align` / `-mno-strict-align`.
- Small data threshold: `-msmall-data-limit=N`.
- Frame pointer: `-fno-omit-frame-pointer`.

### Handy commands

```
riscv64-unknown-elf-objdump -d -M no-aliases a.elf   # raw instruction names
riscv64-unknown-elf-objdump -dr a.o                  # show relocations
riscv64-unknown-elf-readelf -A a.elf                 # ISA attributes
riscv64-unknown-elf-readelf -h a.elf                 # ELF header and flags
riscv64-unknown-elf-nm -n a.elf                      # symbols by address
riscv64-unknown-elf-size a.elf
riscv64-unknown-elf-objcopy -O binary a.elf a.bin
riscv64-unknown-elf-addr2line -e a.elf 0x80000100
```

## 9.7 Assembler syntax and directives

### Operand syntax

```asm
    addi a0, a0, 1
    lw   a1, 4(a0)           # offset(base)
    lw   a1, %lo(sym)(a2)
    beq  a0, a1, 1f          # numeric local labels: 1b = previous 1:, 1f = next 1:
    csrr t0, mstatus
    fadd.s fa0, fa1, fa2, rtz  # optional rounding-mode operand
```

Register names: `x0`-`x31` or ABI names; `f0`-`f31` or `ft0` etc.; `v0`-`v31`.

### Directives

| Directive | Purpose |
|-----------|---------|
| `.text`, `.data`, `.bss`, `.section name,"flags",@type` | Select section |
| `.globl sym`, `.weak sym`, `.local sym` | Symbol binding |
| `.type sym, @function`, `.size sym, .-sym` | ELF symbol type/size |
| `.align n` | In RISC-V GNU as: alignment as **2^n** bytes (n=2 -> 4 bytes). Prefer `.balign` (bytes) or `.p2align` (explicit). |
| `.byte .half .word .dword .quad .string .asciz .ascii` | Data |
| `.zero n`, `.space n`, `.skip n` | Reserve bytes |
| `.equ sym, expr`, `.set` | Constants |
| `.macro`/`.endm`, `.rept`/`.endr` | Macros / repetition |
| `.option rvc / norvc` | Allow/forbid compressed encodings |
| `.option relax / norelax` | Allow/forbid linker relaxation |
| `.option push / pop` | Save/restore option state |
| `.option arch, +zba` | Enable extension for following code |
| `.attribute arch, "rv64gc"` | Set ISA attribute |
| `.insn` | Hand-encode an instruction (custom extensions) |
| `.cfi_*` | DWARF call-frame info |
| `.dtprelword`, `.dtpreldword` | TLS offsets |

### `.insn` for custom instructions

```asm
# custom-0 opcode (0x0b), R-format: funct3=0, funct7=0
.insn r 0x0b, 0, 0, a0, a1, a2     # my_op a0, a1, a2
```

Custom opcode spaces: custom-0 `0x0b`, custom-1 `0x2b`, custom-2 `0x5b`, custom-3 `0x7b`.

### Macro example

```asm
.macro PUSH reg
    addi sp, sp, -8
    sd   \reg, 0(sp)
.endm
.macro POP reg
    ld   \reg, 0(sp)
    addi sp, sp, 8
.endm
```

## 9.8 Inline assembly in C

```c
static inline unsigned long read_csr_mstatus(void) {
    unsigned long v;
    asm volatile ("csrr %0, mstatus" : "=r"(v));
    return v;
}
static inline void fence_rw_rw(void) { asm volatile ("fence rw, rw" ::: "memory"); }

#define csr_write(csr, val) \
    asm volatile ("csrw " #csr ", %0" :: "rK"(val) : "memory")
```

`"K"` allows 5-bit unsigned immediate constraints for `csrw` with immediate forms. Add `"memory"` clobber to stop compiler reordering around barriers.

## 9.9 Complete bare-metal example (QEMU `virt`, RV64)

Machine facts for QEMU `virt`: RAM at `0x8000_0000`, UART (16550) at `0x1000_0000`, CLINT at `0x0200_0000`, PLIC at `0x0C00_0000`. With `-bios none -kernel prog.elf`, execution begins at the ELF entry (`0x8000_0000`) in **M-mode**, `a0 = hartid`.

**`start.S`**

```asm
    .section .text.init
    .globl _start
_start:
    csrr  t0, mhartid
    bnez  t0, park              # only hart 0 continues
.option push
.option norelax
    la    gp, __global_pointer$
.option pop
    la    sp, _stack_top
    la    t0, __bss_start       # clear .bss
    la    t1, __bss_end
1:  bgeu  t0, t1, 2f
    sd    zero, 0(t0)
    addi  t0, t0, 8
    j     1b
2:  call  main
park:
    wfi
    j     park
```

**`link.ld`**

```
OUTPUT_ARCH(riscv)
ENTRY(_start)
MEMORY { RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 128M }
SECTIONS {
  .text   : { *(.text.init) *(.text .text.*) } > RAM
  .rodata : { *(.rodata .rodata.*) } > RAM
  .data   : { *(.data .data.*) } > RAM
  .sdata  : { __global_pointer$ = . + 0x800; *(.sdata .sdata.*) } > RAM
  .sbss   : { *(.sbss .sbss.*) } > RAM
  .bss    : { . = ALIGN(8); __bss_start = .; *(.bss .bss.*) *(COMMON) . = ALIGN(8); __bss_end = .; } > RAM
  . = ALIGN(16);
  . += 0x10000;                /* 64 KiB stack */
  _stack_top = .;
}
```

**`main.c`**

```c
#define UART0 ((volatile unsigned char *)0x10000000UL)

static void putc_uart(char c) {
    while (!(UART0[5] & 0x20)) { }   /* LSR bit 5: transmit holding register empty */
    UART0[0] = (unsigned char)c;
}
static void puts_uart(const char *s) { while (*s) putc_uart(*s++); }

int main(void) {
    puts_uart("Hello, RISC-V!\n");
    return 0;
}
```

**Build and run**

```
riscv64-unknown-elf-gcc -march=rv64gc -mabi=lp64d -mcmodel=medany \
    -nostdlib -ffreestanding -T link.ld start.S main.c -o hello.elf
qemu-system-riscv64 -machine virt -nographic -bios none -kernel hello.elf
# exit QEMU: Ctrl-A, then X
```

To run with OpenSBI instead (S-mode payload), drop `-bios none` (default firmware is OpenSBI); your code then enters in **S-mode** at `0x8020_0000` with `a0 = hartid`, `a1 = DTB`, and uses SBI calls (Chapter 10).

## 9.10 Reading compiler output

```c
long add3(long a, long b, long c) { return a + b + c; }
```

`-O2` produces:

```asm
add3:
    add  a0, a0, a1
    add  a0, a0, a2
    ret
```

A small loop with `Zba`:

```c
long sum(long *a, long n) { long s=0; for (long i=0;i<n;i++) s += a[i]; return s; }
```

At `-O2` compilers use pointer increment; with `-march=rv64gc_zba` indexed accesses use `sh3add`. Use Compiler Explorer (godbolt.org) with RISC-V targets to experiment.

## 9.11 Common pitfalls

| Pitfall | Explanation |
|---------|-------------|
| `char` signedness | Unsigned by default |
| Using `-march=rv64gc` objects with `lp64` (soft-float) libraries | ABI mismatch; link errors/crash. Match `-mabi` everywhere |
| Forgetting `gp` init or doing it with relaxation on | Wrong data addresses |
| `.align` confusion | `.align n` is 2^n in RISC-V gas |
| `li` for 64-bit constants is long | Up to 8 instructions; use a literal pool for hot code |
| Missing `norelax` around `gp` setup | Described above |
| `-mcmodel=medlow` at high addresses (like `0xFFFF...` kernel VA) | Use `medany` |
| `ecall` return: forgetting `mepc += 4` | Infinite trap loop |
| Alignment assumptions | Misaligned loads may trap on cores without hardware support |
| Large immediates in `addi` | 12-bit signed only; assembler errors out of range |
| Mixing 32-bit values assuming zero-extension on RV64 | They are sign-extended; use `zext.w`/`add.uw` when needed |

## 9.12 Chapter summary

- ABIs combine data model and float handling; `lp64d` for Linux 64-bit; `char` is unsigned; 32-bit values are sign-extended in 64-bit registers.
- Arguments in `a0-a7/fa0-fa7`; callee-saved `s0-s11/fs0-fs11/sp`; 16-byte stack alignment, no red zone.
- ELF `EM_RISCV=243`; relocation pairs `PCREL_HI20`/`PCREL_LO12` and linker relaxation shrink code; initialize `gp` with `norelax`.
- Use `-march`/`-mabi` consistently; remember `Zicsr`/`Zifencei` split.
- Bare-metal bring-up needs: startup code, linker script, stack, `.bss` clear, `gp` init, and a console.

### Check yourself

1. In which registers are the first FP arguments passed under `lp64d`? And under `lp64`?
2. What values do `e_machine` and the float-ABI flags have for a `lp64d` RV64 binary?
3. Why must `%pcrel_lo` refer to the `auipc` label?
4. What does `-mcmodel=medany` allow?
5. Why does startup code wrap `la gp` in `.option norelax`?

<details><summary>Answers</summary>

1. `fa0`-`fa7` (under `lp64d`); integer registers `a0`-`a7` under `lp64`.
2. `243`; `EF_RISCV_FLOAT_ABI_DOUBLE` (`0x4`), plus `EF_RISCV_RVC` (`0x1`) if compressed code is present.
3. The offset to compute is relative to the `auipc` instruction, not the instruction using the low part.
4. Code/data anywhere in the address space, within a +/-2 GiB PC-relative window.
5. Otherwise the linker may relax the `la gp` into a `gp`-relative access, which depends on `gp` itself.
</details>

Next: [Chapter 10 - Boot, SBI, Firmware, Linux](10_Boot_SBI_Firmware_Linux.md)
