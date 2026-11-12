# Chapter 2 - The Base Integer ISA (RV32I / RV64I)

[Index](00_README.md) | Prev: [Ch 1](01_Foundations.md) | Next: [Ch 3 - Standard Extensions](03_Standard_Extensions.md)

**Goals:** Learn the programmer's model, the six instruction formats, and every base instruction well enough to read and hand-assemble RISC-V code.

---

## 2.1 Programmer's model

### Registers

| Register | ABI name | Role | Saved by |
|----------|----------|------|----------|
| `x0` | `zero` | Hardwired zero | - |
| `x1` | `ra` | Return address | Caller |
| `x2` | `sp` | Stack pointer | Callee |
| `x3` | `gp` | Global pointer | - (linker-set, do not change) |
| `x4` | `tp` | Thread pointer | - (set by runtime/OS) |
| `x5`-`x7` | `t0`-`t2` | Temporaries | Caller |
| `x8` | `s0` / `fp` | Saved register / frame pointer | Callee |
| `x9` | `s1` | Saved register | Callee |
| `x10`-`x11` | `a0`-`a1` | Arguments and return values | Caller |
| `x12`-`x17` | `a2`-`a7` | Arguments | Caller |
| `x18`-`x27` | `s2`-`s11` | Saved registers | Callee |
| `x28`-`x31` | `t3`-`t6` | Temporaries | Caller |
| `pc` | - | Program counter (not a general register) | - |

- `RV32E`/`RV64E` have only `x0`-`x15`.
- In the hardware, only `x0` is special. The roles above are **software convention** (the ABI, Chapter 9).
- `pc` can be read only through instructions like `auipc`, `jal`, `jalr`; it cannot be a source or destination operand directly.

**Compressed-register subset:** many 16-bit instructions can name only `x8`-`x15` (`s0`,`s1`,`a0`-`a5`).

### Memory model basics for the programmer

- Loads/stores are **byte-addressed**.
- Misaligned accesses may be supported in hardware, emulated by a trap handler, or fault; the EEI decides (profiles like RVA23 require support through `Zicclsm`).
- Default memory consistency is **RVWMO** (Chapter 8).

## 2.2 Instruction formats

All base instructions are 32 bits. Six formats:

```
 31        25 24    20 19    15 14  12 11         7 6      0
+------------+--------+--------+------+------------+--------+
|   funct7   |  rs2   |  rs1   |funct3|     rd     | opcode | R-type
+------------+--------+--------+------+------------+--------+
|      imm[11:0]       |  rs1   |funct3|     rd     | opcode | I-type
+------------+--------+--------+------+------------+--------+
| imm[11:5]  |  rs2   |  rs1   |funct3|  imm[4:0]  | opcode | S-type
+------------+--------+--------+------+------------+--------+
|imm[12|10:5]|  rs2   |  rs1   |funct3|imm[4:1|11] | opcode | B-type
+------------+--------+--------+------+------------+--------+
|              imm[31:12]              |     rd     | opcode | U-type
+--------------------------------------+------------+--------+
|     imm[20|10:1|11|19:12]             |     rd     | opcode | J-type
+--------------------------------------+------------+--------+
```

| Format | Used by | Immediate |
|--------|---------|-----------|
| **R** | register-register ALU | none |
| **I** | register-immediate ALU, loads, `jalr`, `ecall`/`ebreak`, CSR ops, `fence` | 12-bit signed |
| **S** | stores | 12-bit signed, split in two fields |
| **B** | conditional branches | 13-bit signed (bit 0 implicit 0), multiples of 2 |
| **U** | `lui`, `auipc` | upper 20 bits |
| **J** | `jal` | 21-bit signed (bit 0 implicit 0), multiples of 2 |

Key regularities:

- `rs1`, `rs2`, `rd` are always in the same bit positions when present.
- The **sign bit of every immediate is bit 31** of the instruction.
- B and J immediates are rotated so that bit positions of most bits match across formats (less mux logic).
- Branch/jump offsets are in **bytes**, but bit 0 is dropped because instructions are at least 2-byte aligned (even with `C`; without `C`, bit 1 must also be zero or it traps at the target).

### Major opcodes (bits [6:0])

| Opcode | Hex | Name | Typical instructions |
|--------|-----|------|----------------------|
| `0000011` | 0x03 | LOAD | `lb lh lw ld lbu lhu lwu` |
| `0000111` | 0x07 | LOAD-FP | `flw fld flh`, vector loads |
| `0001111` | 0x0F | MISC-MEM | `fence fence.i cbo.*` |
| `0010011` | 0x13 | OP-IMM | `addi slti xori slli ...` |
| `0010111` | 0x17 | AUIPC | `auipc` |
| `0011011` | 0x1B | OP-IMM-32 | `addiw slliw ...` (RV64) |
| `0100011` | 0x23 | STORE | `sb sh sw sd` |
| `0100111` | 0x27 | STORE-FP | `fsw fsd`, vector stores |
| `0101111` | 0x2F | AMO | `lr sc amo*` |
| `0110011` | 0x33 | OP | `add sub sll ... mul div` |
| `0110111` | 0x37 | LUI | `lui` |
| `0111011` | 0x3B | OP-32 | `addw subw ... mulw` (RV64) |
| `1000011`... | 0x43-0x4F | MADD/MSUB/NMSUB/NMADD | FP fused multiply-add |
| `1010011` | 0x53 | OP-FP | FP arithmetic |
| `1010111` | 0x57 | OP-V | Vector arithmetic, `vsetvli` |
| `1100011` | 0x63 | BRANCH | `beq bne blt bge bltu bgeu` |
| `1100111` | 0x67 | JALR | `jalr` |
| `1101111` | 0x6F | JAL | `jal` |
| `1110011` | 0x73 | SYSTEM | `ecall ebreak csrr* mret sret wfi ...` |

Bits `[1:0]` = `11` for every 32-bit instruction; the table lists the full 7 bits.

## 2.3 Immediates and sign extension

- I/S/B/J immediates are **sign-extended** to XLEN.
- U-type immediate occupies bits 31:12; the low 12 bits are zero. On RV64, the 32-bit result is sign-extended to 64 bits.
- Shift amounts are in `imm[4:0]` (RV32) or `imm[5:0]` (RV64).

Ranges:

| Instruction type | Reach |
|------------------|-------|
| I-type immediate | -2048 ... +2047 |
| Branch (B) | +/- 4 KiB (-4096 ... +4094) |
| `jal` | +/- 1 MiB |
| `auipc` + `jalr` / `auipc`+`addi` | +/- 2 GiB (PC-relative) |
| `lui` + `addi` | any 32-bit constant |

## 2.4 The integer computational instructions

### Register-immediate (OP-IMM, I-type)

| Instruction | Operation | funct3 |
|-------------|-----------|--------|
| `addi rd, rs1, imm` | `rd = rs1 + imm` | 000 |
| `slti rd, rs1, imm` | `rd = (signed)rs1 < imm ? 1 : 0` | 010 |
| `sltiu rd, rs1, imm` | `rd = (unsigned)rs1 < (unsigned)imm ? 1 : 0` (imm sign-extended first) | 011 |
| `xori rd, rs1, imm` | bitwise xor | 100 |
| `ori rd, rs1, imm` | bitwise or | 110 |
| `andi rd, rs1, imm` | bitwise and | 111 |
| `slli rd, rs1, shamt` | logical shift left | 001 |
| `srli rd, rs1, shamt` | logical shift right | 101, `imm[11:5]=0000000` |
| `srai rd, rs1, shamt` | arithmetic shift right | 101, `imm[11:5]=0100000` |

- `addi rd, rs1, 0` is the **move** (`mv`); `addi x0, x0, 0` is the canonical **nop**.
- `sltiu rd, rs1, 1` sets `rd` to 1 if `rs1 == 0` (`seqz`).
- `xori rd, rs1, -1` is bitwise NOT (`not`).

### Register-register (OP, R-type)

| Instruction | Operation | funct3 | funct7 |
|-------------|-----------|--------|--------|
| `add` | `rs1 + rs2` | 000 | 0000000 |
| `sub` | `rs1 - rs2` | 000 | 0100000 |
| `sll` | shift left by the low 5 (RV32) or 6 (RV64) bits of `rs2` | 001 | 0000000 |
| `slt` | signed set-less-than | 010 | 0000000 |
| `sltu` | unsigned set-less-than | 011 | 0000000 |
| `xor` | | 100 | 0000000 |
| `srl` | logical shift right | 101 | 0000000 |
| `sra` | arithmetic shift right | 101 | 0100000 |
| `or` | | 110 | 0000000 |
| `and` | | 111 | 0000000 |

- `sltu rd, x0, rs2` sets `rd` to 1 if `rs2 != 0` (`snez`).
- Arithmetic **never traps** on overflow. There are no carry or overflow flags. To detect unsigned add overflow: `add t0,a0,a1; sltu t1,t0,a0` (carry out in `t1`).

### Upper-immediate

| Instruction | Operation |
|-------------|-----------|
| `lui rd, imm20` | `rd = imm20 << 12` (sign-extended on RV64) |
| `auipc rd, imm20` | `rd = pc + (imm20 << 12)` (pc of the `auipc` itself) |

### RV64-only word operations

On RV64 the base ops work on 64-bit values. Special `*W` instructions operate on the lower 32 bits and **sign-extend the 32-bit result to 64 bits**:

`addiw`, `slliw`, `srliw`, `sraiw`, `addw`, `subw`, `sllw`, `srlw`, `sraw`.

- Opcodes: OP-IMM-32 (0x1B) and OP-32 (0x3B).
- Shift immediates in `*W` forms are 5 bits.
- `addiw rd, rs1, 0` = **`sext.w`**, the standard way to sign-extend a 32-bit value.
- A very common ABI convention: 32-bit values live **sign-extended** in 64-bit registers (even unsigned 32-bit values).

### Constant materialization

| Goal | Sequence |
|------|----------|
| Small constant (-2048..2047) | `addi rd, x0, imm` (`li`) |
| 32-bit constant | `lui rd, hi20` ; `addi rd, rd, lo12` |
| Fix for negative low part | If bit 11 of the constant is 1, `lo12` is negative, so use `hi20 + 1` |
| 64-bit constant | Several `lui/addi/slli` steps, or load from a constant pool |

Worked example: `0x12345FFF`
- Low 12 bits = `0xFFF` = -1 (sign-extended), so `hi20 = 0x12345 + 1 = 0x12346`.
- `lui a0, 0x12346` ; `addi a0, a0, -1`.
- Result: `0x12346000 - 1 = 0x12345FFF`. Correct.

Assemblers do this for you: `li a0, 0x12345FFF`.

## 2.5 Control transfer

### Unconditional jumps

| Instruction | Operation |
|-------------|-----------|
| `jal rd, offset` | `rd = pc + 4; pc += offset` (J-type, +/-1 MiB) |
| `jalr rd, offset(rs1)` | `t = pc + 4; pc = (rs1 + offset) & ~1; rd = t` |

- Using `rd = x0` discards the link: `j label` = `jal x0, label`; `jr rs` = `jalr x0, 0(rs)`.
- `ret` = `jalr x0, 0(ra)`.
- `call` (far) = `auipc ra, hi20` + `jalr ra, lo12(ra)`; `tail` uses `t1` instead of `ra`.
- If the target is misaligned for `IALIGN`, an **instruction-address-misaligned** exception is raised at the jump (RV32/64 without `C` require 4-byte alignment).

### Conditional branches (B-type, compare-and-branch)

| Instruction | Condition | funct3 |
|-------------|-----------|--------|
| `beq rs1, rs2, off` | `rs1 == rs2` | 000 |
| `bne` | `!=` | 001 |
| `blt` | signed `<` | 100 |
| `bge` | signed `>=` | 101 |
| `bltu` | unsigned `<` | 110 |
| `bgeu` | unsigned `>=` | 111 |

Only these six exist. The others are pseudoinstructions with swapped operands: `bgt a,b,L` = `blt b,a,L`; `ble`, `bgtu`, `bleu` similar. Compare with zero: `beqz`, `bnez`, `blez`, `bgez`, `bltz`, `bgtz`.

Branches are **not** predicated or delayed. Software convention (and some predictors) treat backward branches as taken and forward as not taken.

## 2.6 Loads and stores

Loads (I-type) and stores (S-type) compute `address = rs1 + sign_extend(imm12)`.

| Load | Width | Extension | funct3 |
|------|-------|-----------|--------|
| `lb` | 8 | sign | 000 |
| `lh` | 16 | sign | 001 |
| `lw` | 32 | sign (RV64) | 010 |
| `ld` | 64 | RV64 only | 011 |
| `lbu` | 8 | zero | 100 |
| `lhu` | 16 | zero | 101 |
| `lwu` | 32 | zero, RV64 only | 110 |

| Store | Width | funct3 |
|-------|-------|--------|
| `sb` | 8 | 000 |
| `sh` | 16 | 001 |
| `sw` | 32 | 010 |
| `sd` | 64, RV64 only | 011 |

Notes:

- There is no scaled or indexed addressing mode in the base ISA. Array indexing needs shift + add (or `sh1add/sh2add/sh3add` from `Zba`).
- Alignment: natural alignment is guaranteed to work and be atomic in a hart-local sense. Misaligned behavior is environment-defined.
- A load with `rd = x0` still performs the access (and can fault) but discards the result.

## 2.7 Memory ordering and system instructions

### `fence`

```
fence pred, succ     # pred/succ drawn from i, o, r, w
```

- Orders accesses of the `pred` set before accesses of the `succ` set as observed by other harts and devices.
- `i` = device input, `o` = device output, `r` = memory read, `w` = memory write.
- `fence rw, rw` is a full barrier. `fence` alone (no operands) assembles as `fence iorw, iorw`.
- `fence.tso` (`fm=1000`, `rw,rw`): load->load/store and store->store ordering, but not store->load.
- **`pause`** (`Zihintpause`): a hint encoded as `fence` with `pred=w`, `succ=0`; tells the hart to spin-wait politely.

### `fence.i` (`Zifencei`)

Synchronizes the instruction stream of the current hart with its own prior stores. Required after writing code (JIT, loaders). Does **not** by itself synchronize other harts (use IPI + `fence.i` on each, e.g., via SBI RFENCE).

### Environment calls and breakpoints

| Instruction | Effect |
|-------------|--------|
| `ecall` | Request service from the next-more-privileged environment: U->S, S->M (or SBI), VS->HS |
| `ebreak` | Raises a breakpoint exception (debugger hook) |
| `wfi` | Wait for interrupt (hint-ish; may be implemented as a `nop`). Privileged. |
| `mret`, `sret`, `mnret`, `dret` | Return from a trap/NMI/debug (privileged) |
| `sfence.vma` | Order page-table updates with address translation (privileged) |
| `unimp` / `c.unimp` | Pseudoinstruction for an illegal instruction (all-zero encoding or `csrrw x0,cycle,x0`) |

### CSR instructions (`Zicsr`)

| Instruction | Operation |
|-------------|-----------|
| `csrrw rd, csr, rs1` | `t = csr; csr = rs1; rd = t` (if `rd = x0`, the **read is skipped**) |
| `csrrs rd, csr, rs1` | `t = csr; csr = t OR rs1; rd = t` (if `rs1 = x0`, **no write**) |
| `csrrc rd, csr, rs1` | `t = csr; csr = t AND NOT rs1; rd = t` (if `rs1 = x0`, no write) |
| `csrrwi/csrrsi/csrrci` | Same but with a 5-bit zero-extended immediate (`uimm`) instead of `rs1` |

Pseudoinstructions: `csrr rd, csr` (= `csrrs rd,csr,x0`), `csrw csr, rs` (= `csrrw x0,csr,rs`), `csrs`, `csrc`, `csrwi`, `csrsi`, `csrci`, `rdcycle`, `rdtime`, `rdinstret`, `frcsr`, `fscsr`, `frrm` etc.

All CSR read-modify-write instructions are **atomic** with respect to the hart. Writing a read-only CSR or accessing one without sufficient privilege raises **illegal-instruction** (or virtual-instruction in virtualized contexts).

## 2.8 Pseudoinstructions (cheat sheet)

The assembler expands these into real instructions.

| Pseudo | Expansion |
|--------|-----------|
| `nop` | `addi x0, x0, 0` |
| `li rd, imm` | `addi` / `lui+addi` / longer sequence |
| `mv rd, rs` | `addi rd, rs, 0` |
| `not rd, rs` | `xori rd, rs, -1` |
| `neg rd, rs` | `sub rd, x0, rs` |
| `negw rd, rs` | `subw rd, x0, rs` |
| `sext.w rd, rs` | `addiw rd, rs, 0` |
| `seqz rd, rs` | `sltiu rd, rs, 1` |
| `snez rd, rs` | `sltu rd, x0, rs` |
| `sltz rd, rs` | `slt rd, rs, x0` |
| `sgtz rd, rs` | `slt rd, x0, rs` |
| `beqz rs, L` / `bnez rs, L` | `beq/bne rs, x0, L` |
| `blez/bgez/bltz/bgtz rs, L` | compare with `x0` |
| `bgt/ble/bgtu/bleu a,b,L` | `blt/bge/bltu/bgeu b,a,L` |
| `j L` | `jal x0, L` |
| `jal L` | `jal ra, L` |
| `jr rs` | `jalr x0, 0(rs)` |
| `jalr rs` | `jalr ra, 0(rs)` |
| `ret` | `jalr x0, 0(ra)` |
| `call sym` | `auipc ra, %pcrel_hi(sym)`; `jalr ra, %pcrel_lo(...)(ra)` |
| `tail sym` | same with `t1` and `x0` link |
| `la rd, sym` | `auipc rd, %pcrel_hi` + `addi rd, rd, %pcrel_lo` (non-PIC) or GOT load (`-fPIC`) |
| `lla rd, sym` | local address, always PC-relative |
| `lw rd, sym` | `auipc rd, hi` + `lw rd, lo(rd)` (load global) |
| `sw rs, sym, rt` | `auipc rt, hi` + `sw rs, lo(rt)` (store global, needs temp) |
| `fence` | `fence iorw, iorw` |
| `csrr/csrw/...` | see 2.7 |
| `rdcycle rd` | `csrrs rd, cycle, x0` |
| `rdtime rd` | `csrrs rd, time, x0` |
| `rdinstret rd` | `csrrs rd, instret, x0` |
| `zext.b rd, rs` | `andi rd, rs, 255` |
| `zext.w rd, rs` | `add.uw rd, rs, x0` (`Zba`) or `slli`+`srli` |

### The `%hi` / `%lo` relocation functions

- `%hi(sym)` / `%lo(sym)` - absolute (non-PIC). `lui t0, %hi(sym); addi t0,t0,%lo(sym)`.
- `%pcrel_hi(label)` / `%pcrel_lo(label)` - PC-relative; **`%pcrel_lo` refers to the label of the `auipc`**, not the symbol:

```asm
1:  auipc t0, %pcrel_hi(msg)
    addi  t0, t0, %pcrel_lo(1b)
```

- `%tprel_*`, `%tls_*`, `%got_pcrel_hi` for TLS and GOT forms (Chapter 9).

## 2.9 Complete instruction listing, RV32I base

| Mnemonic | Format | Semantics |
|----------|--------|-----------|
| `lui` | U | `rd = imm << 12` |
| `auipc` | U | `rd = pc + (imm << 12)` |
| `jal` | J | `rd = pc+4; pc += imm` |
| `jalr` | I | `rd = pc+4; pc = (rs1+imm)&~1` |
| `beq bne blt bge bltu bgeu` | B | conditional PC-relative |
| `lb lh lw lbu lhu` | I | loads |
| `sb sh sw` | S | stores |
| `addi slti sltiu xori ori andi slli srli srai` | I | ALU immediate |
| `add sub sll slt sltu xor srl sra or and` | R | ALU register |
| `fence` | I | memory ordering |
| `ecall ebreak` | I | traps |

**RV64I additions:** `lwu ld sd`, `addiw slliw srliw sraiw`, `addw subw sllw srlw sraw`; shifts take 6-bit shift amounts.

**Zicsr:** `csrrw csrrs csrrc csrrwi csrrsi csrrci`. **Zifencei:** `fence.i`.

## 2.10 Reading encodings: worked examples

Verify by composing the fields (all values in hex are the final 32-bit word).

**`addi a0, a0, 1`** -> I-type: imm=`000000000001`, rs1=10 (`01010`), funct3=`000`, rd=10, opcode=`0010011`.
`0000 0000 0001 0101 0000 0101 0001 0011` = **`0x00150513`**.

**`add a0, a1, a2`** -> R-type: funct7=0, rs2=12 (`01100`), rs1=11 (`01011`), funct3=0, rd=10 (`01010`), opcode=`0110011`.
= **`0x00C58533`**.

**`lw a0, 8(sp)`** -> I-type: imm=8, rs1=2, funct3=`010`, rd=10, opcode=`0000011`.
= **`0x00812503`**.

**`sw a0, 8(sp)`** -> S-type: imm[11:5]=0, rs2=10, rs1=2, funct3=`010`, imm[4:0]=`01000`, opcode=`0100011`.
= **`0x00A12423`**.

**`beq a0, a1, +8`** -> B-type: imm=8 -> imm[12]=0, imm[10:5]=0, imm[4:1]=`0100`, imm[11]=0; rs2=11, rs1=10, funct3=0, opcode=`1100011`.
= **`0x00B50463`**.

**`lui a0, 0x12345`** -> `imm20=0x12345`, rd=10, opcode=`0110111` = **`0x12345537`**.

**`ret`** -> `jalr x0, 0(ra)` = **`0x00008067`**.

**`nop`** -> `addi x0, x0, 0` = **`0x00000013`**.

**`ecall`** = `0x00000073`; **`ebreak`** = `0x00100073`; **`mret`** = `0x30200073`; **`sret`** = `0x10200073`; **`wfi`** = `0x10500073`.

## 2.11 Hand-compiled examples

### Sum an array (RV64)

```c
long sum(const long *a, long n) {
    long s = 0;
    for (long i = 0; i < n; i++) s += a[i];
    return s;
}
```

```asm
sum:
    li    t0, 0              # s = 0
    ble   a1, x0, 2f         # if n <= 0 skip
1:  ld    t1, 0(a0)          # t1 = *a
    add   t0, t0, t1         # s += t1
    addi  a0, a0, 8          # a++
    addi  a1, a1, -1         # n--
    bnez  a1, 1b
2:  mv    a0, t0
    ret
```

### `strlen` (RV64)

```asm
strlen:
    mv   t0, a0
1:  lbu  t1, 0(t0)
    addi t0, t0, 1
    bnez t1, 1b
    sub  a0, t0, a0
    addi a0, a0, -1
    ret
```

### Function with a stack frame

```asm
func:
    addi sp, sp, -16        # allocate (keep 16-byte alignment)
    sd   ra, 8(sp)          # save return address
    sd   s0, 0(sp)          # save callee-saved reg
    mv   s0, a0
    call helper
    add  a0, a0, s0
    ld   s0, 0(sp)
    ld   ra, 8(sp)
    addi sp, sp, 16
    ret
```

### Unsigned carry / multi-word add (128-bit on RV64)

```asm
# (a1:a0) + (a3:a2) -> (a1:a0)
    add  a0, a0, a2
    sltu t0, a0, a2          # carry out of low word
    add  a1, a1, a3
    add  a1, a1, t0
```

## 2.12 Frequently asked "why?" about the base ISA

| Question | Answer |
|----------|--------|
| Why no flags register? | Flags create hidden state and serialization. Branches compare registers directly. |
| Why no `mov`? | `addi rd, rs, 0` suffices; fewer opcodes. |
| Why does overflow not trap? | Languages that need it test explicitly; avoids precise-trap cost on every add. |
| Why compare-and-branch only to registers? | Keeps decode simple; immediates would eat encoding space. |
| Why 12-bit immediates? | Balance between instruction density and encoding space. |
| Why do `lui`/`addi` need the "+1" correction? | Because `addi`'s immediate is signed. |
| Why `auipc`? | PC-relative addressing for position-independent code and +/-2 GiB reach. |
| Why does division by zero not trap? | Defined results: quotient all ones, remainder = dividend (see `M` in Chapter 3). |

## 2.13 Chapter summary

- 32 integer registers (`x0` = 0), a separate `pc`, six instruction formats, load/store architecture.
- Immediates are always sign-extended; large constants use `lui`/`auipc` + `addi`/load/store.
- No flags, no delay slots, no trapping arithmetic, compare-and-branch.
- RV64 adds 64-bit loads/stores and `*W` instructions that produce sign-extended 32-bit results.
- CSR access and system instructions come from `Zicsr`, `Zifencei`, and the privileged architecture.

### Check yourself

1. Encode `sub a0, a1, a2`.
2. What is the largest forward branch distance of `beq`?
3. How do you load `0xDEADBEEF` into `a0` on RV32?
4. What does `csrrs x0, mstatus, t0` do, and why is `rd = x0` useful?
5. Why must `%pcrel_lo` reference the `auipc` label instead of the symbol?

<details><summary>Answers</summary>

1. funct7=`0100000`, rs2=12, rs1=11, funct3=0, rd=10, opcode=`0110011`: `0x40C58533`.
2. +4094 bytes (13-bit signed offset, even).
3. Low 12 bits `0xEEF` has bit 11 = 1 so it is negative: `lui a0, 0xDEADC` ; `addi a0, a0, -273` (`0xEEF` as signed is -273). (`li a0, 0xDEADBEEF` does this.)
4. It sets (ORs) the bits in `t0` into `mstatus` without reading the old value into a register (`rd = x0` discards it; `csrrs` with `rd = x0` still writes).
5. The low-12 part must be computed from the PC-relative offset of the `auipc`, not from the symbol address alone.
</details>

Next: [Chapter 3 - Standard Extensions](03_Standard_Extensions.md)
