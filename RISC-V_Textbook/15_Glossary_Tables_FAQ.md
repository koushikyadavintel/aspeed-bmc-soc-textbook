# Chapter 15 - Glossary, Quick-Reference Tables, Checklists, FAQ, and Resources

[Index](00_README.md) | Prev: [Ch 14](14_Emerging_Topics.md)

This chapter is the **dictionary**. Use Ctrl+F. Entries point to the chapter with details.

---

## 15.1 Glossary (A-Z)

| Term | Definition | Ch |
|------|------------|----|
| **A (extension)** | Atomics: `Zaamo` + `Zalrsc` | 3 |
| **ABI** | Application Binary Interface: calling convention, data layout, object format | 9 |
| **ACLINT** | Advanced CLINT: split timer/software-interrupt devices (MTIMER, MSWI, SSWI) | 7 |
| **AIA** | Advanced Interrupt Architecture: APLIC + IMSIC | 7 |
| **AMO** | Atomic Memory Operation (`amoadd`, `amoswap`, ...) | 3, 8 |
| **APLIC** | Advanced PLIC; converts wired interrupts to MSIs or direct delivery | 7 |
| **AQ / RL** | Acquire / Release annotation bits on atomics | 8 |
| **ASID** | Address Space Identifier, tags TLB entries | 6 |
| **AVL** | Application Vector Length (requested element count) | 4 |
| **B (extension)** | Bit manipulation = `Zba` + `Zbb` + `Zbs` | 3 |
| **Bare** | `satp.MODE = 0`: no translation | 6 |
| **BRS** | Boot and Runtime Services platform spec **[verify]** | 10 |
| **C (extension)** | Compressed 16-bit instructions | 3 |
| **CBO** | Cache-Block Operation (`cbo.clean/flush/inval/zero`) | 3 |
| **CLINT** | Core-Local Interruptor: `mtime`, `mtimecmp`, `msip` | 7 |
| **CoVE** | Confidential VM Extension (AP-TEE) | 12 |
| **CSR** | Control and Status Register | 5 |
| **CTR** | Control Transfer Records (branch history) | 13 |
| **D (extension)** | Double-precision FP | 3 |
| **Debug Mode** | Special hart state controlled by the Debug Module | 13 |
| **Delegation** | `medeleg`/`mideleg` routing traps to S-mode | 5 |
| **DM / DTM / DMI** | Debug Module / Transport Module / Module Interface | 13 |
| **DTB / DTS** | Device Tree Blob / Source | 10 |
| **E (base)** | Embedded base with 16 integer registers | 1 |
| **E-Trace / N-Trace** | Instruction trace specifications | 13 |
| **EEI** | Execution Environment Interface | 1 |
| **ELEN** | Max vector element width | 4 |
| **ELF** | Executable and Linkable Format | 9 |
| **ELP** | Expected Landing Pad state (CFI) | 12 |
| **EMUL** | Effective LMUL of a vector memory/widening operand | 4 |
| **F (extension)** | Single-precision FP | 3 |
| **Fault-only-first** | Vector load that trims `vl` instead of trapping after element 0 | 4 |
| **FENCE** | Memory-ordering instruction; `FENCE.I` for instruction fetch | 8 |
| **FLEN** | FP register width | 3 |
| **FWFT** | SBI Firmware Features extension | 10 |
| **G** | Shorthand for `IMAFD_Zicsr_Zifencei` | 1 |
| **G-stage** | Guest-physical to host-physical translation | 7 |
| **gp** | Global pointer register (`x3`) | 9 |
| **H (extension)** | Hypervisor extension | 7 |
| **Hart** | Hardware thread | 1 |
| **HS-mode** | Hypervisor-extended supervisor mode | 7 |
| **HSM** | SBI Hart State Management | 10 |
| **I (base)** | Integer base ISA | 2 |
| **IALIGN / ILEN** | Instruction alignment / maximum length | 1 |
| **IMSIC** | Incoming MSI Controller (AIA) | 7 |
| **IOMMU** | I/O memory management unit | 7 |
| **IOPMP** | Physical memory protection for bus masters **[verify]** | 12 |
| **LMUL** | Vector register group multiplier | 4 |
| **LR/SC** | Load-Reserved / Store-Conditional | 8 |
| **M (extension)** | Integer multiply/divide | 3 |
| **M-mode** | Machine mode, highest privilege | 5 |
| **MMIO** | Memory-mapped I/O | 8 |
| **MOP** | May-Be-Operation (`Zimop`) | 3 |
| **MSI** | Message-Signaled Interrupt | 7 |
| **NAPOT** | Naturally aligned power-of-two (PMP regions, PTEs) | 5, 6 |
| **NaN-boxing** | Storing narrow FP values in wide registers with upper bits set | 3 |
| **OpenSBI** | Reference M-mode SBI implementation | 10 |
| **OS-A** | OS-class platform specification | 1, 10 |
| **PBMT** | Page-Based Memory Types (`Svpbmt`) | 6 |
| **PLIC** | Platform-Level Interrupt Controller | 7 |
| **PMA** | Physical Memory Attributes | 5, 11 |
| **PMP** | Physical Memory Protection | 5 |
| **PMU** | Performance Monitoring Unit | 13 |
| **Profile** | Named set of mandatory/optional extensions (e.g., RVA23) | 1, 3 |
| **psABI** | Processor-specific ABI | 9 |
| **PTE** | Page-Table Entry | 6 |
| **RERI** | RAS Error-record Register Interface | 13 |
| **RoCC** | Rocket Custom Coprocessor interface | 11 |
| **RSW** | Reserved for SoftWare bits in PTE | 6 |
| **RV32I / RV64I / RV32E / RV64E** | Base ISAs | 1, 2 |
| **RVA23** | Application-processor profile generation of 2023 (U64 and S64 variants) | 3 |
| **RVC** | Informal name for the C extension | 3 |
| **RVV** | RISC-V Vector extension | 4 |
| **RVWMO** | RISC-V Weak Memory Ordering | 8 |
| **S-mode** | Supervisor mode | 5 |
| **SBI** | Supervisor Binary Interface | 10 |
| **SEW** | Selected element width | 4 |
| **Shadow stack** | Separate return-address stack (`Zicfiss`) | 12 |
| **Smepmp** | Machine-mode enhanced PMP | 5, 12 |
| **SRST** | SBI System Reset extension | 10 |
| **Sstc** | Supervisor timer compare extension | 5 |
| **Sv32/39/48/57** | Virtual-memory schemes | 6 |
| **TLB** | Translation Lookaside Buffer | 6 |
| **Trap** | Transfer of control due to exception or interrupt | 1, 5 |
| **TSO / Ztso** | Total Store Ordering / its extension | 8 |
| **TSM / TVM** | TEE Security Manager / TEE VM (CoVE) | 12 |
| **U-mode** | User mode | 5 |
| **UNSPECIFIED** | Behavior intentionally left open by the spec | 1 |
| **V (extension / bit)** | Vector extension; also hypervisor virtualization-mode bit | 4, 7 |
| **vl / vtype / vstart** | Vector length / type / start CSRs | 4 |
| **VLEN** | Vector register width in bits | 4 |
| **VMID** | Virtual-machine ID tagging G-stage TLB entries | 7 |
| **VS / VU** | Virtual supervisor / virtual user mode (guest) | 7 |
| **WARL / WLRL / WPRI** | CSR field behaviors | 5 |
| **WFI** | Wait For Interrupt | 5 |
| **XLEN** | Integer register width | 1 |
| **Z extensions** | Multi-letter standard extensions starting with Z | 1, 3 |

---

## 15.2 Extension index (alphabetical)

`R` = Ratified, `D` = Draft/other, `P` = profile-defined behavior, **[v]** = verify status.

| Name | Meaning | Ch |
|------|---------|----|
| `A` | Atomics | 3 |
| `B` | Bit-manip (Zba+Zbb+Zbs) | 3 |
| `C` | Compressed | 3 |
| `D`, `F`, `Q` | Double, single, quad FP | 3 |
| `H` | Hypervisor | 7 |
| `I`, `E` | Integer bases | 2 |
| `M` | Multiply/divide | 3 |
| `P` | Packed SIMD **[v]** | 14 |
| `V` | Vector | 4 |
| `Sdtrig` | Debug triggers | 13 |
| `Sha` | Augmented hypervisor (profile name) | 7 |
| `Shcounterenw`, `Shgatpa`, `Shtvala`, `Shvsatpa`, `Shvstvala`, `Shvstvecd` | Hypervisor behavior guarantees (P) | 7 |
| `Smaia`, `Ssaia` | AIA CSRs (machine/supervisor) | 7 |
| `Smcdeleg`, `Ssccfg` | Counter delegation **[v]** | 13 |
| `Smcntrpmf` | Cycle/instret privilege filtering **[v]** | 13 |
| `Smcsrind`, `Sscsrind` | Indirect CSR access | 5 |
| `Smctr`, `Ssctr` | Control transfer records **[v]** | 13 |
| `Smdbltrp`, `Ssdbltrp` | Double trap handling **[v]** | 5, 13 |
| `Smepmp` | Enhanced PMP | 5 |
| `Smmpm`, `Smnpm`, `Ssnpm`, `Sspm`, `Supm` | Pointer masking | 12 |
| `Smmtt` | Memory tracking tables **[v]** | 12 |
| `Smrnmi` | Resumable NMI | 5, 13 |
| `Smstateen`, `Ssstateen` | State enable | 5 |
| `Ss1p13` | Supervisor architecture v1.13 | 5 |
| `Ssccptr` | Hardware page-table reads from main memory (P) | 6 |
| `Sscofpmf` | Counter overflow and filtering | 13 |
| `Sscounterenw` | Writable counter enables (P) | 5 |
| `Ssqosid` | QoS identifiers **[v]** | 14 |
| `Sstc` | Supervisor timer compare | 5 |
| `Sstvala`, `Sstvecd` | `stval`/`stvec` behavior guarantees (P) | 5 |
| `Ssstrict` | Strict reserved-encoding behavior (P) | 3 |
| `Ssu64xl` | UXLEN=64 supported (P) | 3 |
| `Sv32`, `Sv39`, `Sv48`, `Sv57` | Page-based virtual memory | 6 |
| `Svade`, `Svadu` | A/D bit fault vs hardware update | 6 |
| `Svbare` | `satp` Bare mode supported (P) | 6 |
| `Svinval` | Fine-grained TLB invalidation | 6 |
| `Svnapot` | 64 KiB NAPOT pages | 6 |
| `Svpbmt` | Page-based memory types | 6 |
| `Svrsw60t59b` | Free PTE bits 60:59 for software **[v]** | 6 |
| `Svukte` | User-address side-channel hardening **[v]** | 14 |
| `Svvptc` | Bounded visibility of invalid->valid PTE | 6 |
| `Za64rs`, `Za128rs` | Reservation set size (P) | 3, 8 |
| `Zaamo`, `Zalrsc` | AMO / LR-SC subsets | 3 |
| `Zabha` | Byte/halfword atomics | 3 |
| `Zacas` | Compare-and-swap | 3 |
| `Zalasr` | Load-acquire/store-release **[v]** | 3, 8 |
| `Zama16b` | 16-byte misaligned atomicity granule (P) | 3 |
| `Zawrs` | Wait on reservation set | 3 |
| `Zba`, `Zbb`, `Zbc`, `Zbs` | Bit manipulation components | 3 |
| `Zbkb`, `Zbkc`, `Zbkx` | Crypto bit-manip, carry-less, crossbar | 3 |
| `Zca`, `Zcb`, `Zcd`, `Zcf` | Compressed components | 3 |
| `Zclsd`, `Zilsd` | RV32 load/store pair **[v]** | 3 |
| `Zcmop`, `Zimop` | May-be-operations | 3 |
| `Zcmp`, `Zcmt` | Push/pop macros, table jumps | 3 |
| `Zfa` | Additional FP | 3 |
| `Zfbfmin` | BF16 convert | 3 |
| `Zfh`, `Zfhmin` | Half-precision FP | 3 |
| `Zfinx`, `Zdinx`, `Zhinx`, `Zhinxmin` | FP in integer registers | 3 |
| `Zic64b` | 64-byte cache blocks (P) | 3 |
| `Zicbom`, `Zicbop`, `Zicboz` | Cache-block management/prefetch/zero | 3 |
| `Ziccamoa`, `Ziccamoc`, `Ziccif`, `Zicclsm`, `Ziccrse` | Main-memory behavior guarantees (P) | 3 |
| `Zicfilp`, `Zicfiss` | Landing pads, shadow stack | 12 |
| `Zicntr`, `Zihpm` | Counters | 3, 13 |
| `Zicond` | Conditional zero | 3 |
| `Zicsr`, `Zifencei` | CSR instructions, fence.i | 2 |
| `Zihintntl`, `Zihintpause` | Hints | 3 |
| `Zjid` | I-cache coherence **[D]** | 14 |
| `Zk`, `Zkn`, `Zks`, `Zknd`, `Zkne`, `Zknh`, `Zksed`, `Zksh`, `Zkr`, `Zkt` | Scalar crypto | 3 |
| `Zmmul` | Multiply only | 3 |
| `Ztso` | Total store ordering | 8 |
| `Zve32x` ... `Zve64d`, `Zvl*b` | Embedded vector, min VLEN | 4 |
| `Zvbb`, `Zvbc`, `Zvkb`, `Zvkg`, `Zvkned`, `Zvknha`, `Zvknhb`, `Zvksed`, `Zvksh`, `Zvkt` | Vector crypto and bit-manip | 4 |
| `Zvfh`, `Zvfhmin`, `Zvfbfmin`, `Zvfbfwma` | Vector FP16/BF16 | 4 |
| `X*` | Vendor-specific extensions (e.g., `Xthead*`) | 11 |

---

## 15.3 CSR quick reference

### User-level

| CSR | Addr | Notes |
|-----|------|-------|
| `fflags`, `frm`, `fcsr` | 0x001, 0x002, 0x003 | FP flags, rounding mode, combined |
| `vstart`, `vxsat`, `vxrm`, `vcsr` | 0x008, 0x009, 0x00A, 0x00F | Vector state |
| `ssp` | 0x011 | Shadow stack pointer (`Zicfiss`) |
| `seed` | 0x015 | Entropy (`Zkr`) |
| `jvt` | 0x017 | Jump vector table (`Zcmt`) |
| `cycle`, `time`, `instret` | 0xC00, 0xC01, 0xC02 | Counters |
| `hpmcounter3`...`31` | 0xC03...0xC1F | Event counters |
| `vl`, `vtype`, `vlenb` | 0xC20, 0xC21, 0xC22 | Vector |

### Supervisor-level

| CSR | Addr |
|-----|------|
| `sstatus` | 0x100 |
| `sie` | 0x104 |
| `stvec` | 0x105 |
| `scounteren` | 0x106 |
| `senvcfg` | 0x10A |
| `sscratch` | 0x140 |
| `sepc` | 0x141 |
| `scause` | 0x142 |
| `stval` | 0x143 |
| `sip` | 0x144 |
| `stimecmp` | 0x14D |
| `satp` | 0x180 |
| `scountovf` | 0xDA0 |

### Hypervisor/VS-level

| CSR | Addr | CSR | Addr |
|-----|------|-----|------|
| `hstatus` | 0x600 | `vsstatus` | 0x200 |
| `hedeleg` | 0x602 | `vsie` | 0x204 |
| `hideleg` | 0x603 | `vstvec` | 0x205 |
| `hie` | 0x604 | `vsscratch` | 0x240 |
| `htimedelta` | 0x605 | `vsepc` | 0x241 |
| `hcounteren` | 0x606 | `vscause` | 0x242 |
| `hgeie` | 0x607 | `vstval` | 0x243 |
| `henvcfg` | 0x60A | `vsip` | 0x244 |
| `htval` | 0x643 | `vstimecmp` | 0x24D |
| `hip` | 0x644 | `vsatp` | 0x280 |
| `hvip` | 0x645 | | |
| `htinst` | 0x64A | | |
| `hgatp` | 0x680 | | |
| `hgeip` | 0xE12 | | |

### Machine-level

| CSR | Addr | CSR | Addr |
|-----|------|-----|------|
| `mvendorid` | 0xF11 | `mcounteren` | 0x306 |
| `marchid` | 0xF12 | `menvcfg` | 0x30A |
| `mimpid` | 0xF13 | `mcountinhibit` | 0x320 |
| `mhartid` | 0xF14 | `mscratch` | 0x340 |
| `mconfigptr` | 0xF15 | `mepc` | 0x341 |
| `mstatus` | 0x300 | `mcause` | 0x342 |
| `misa` | 0x301 | `mtval` | 0x343 |
| `medeleg` | 0x302 | `mip` | 0x344 |
| `mideleg` | 0x303 | `mtinst` | 0x34A |
| `mie` | 0x304 | `mtval2` | 0x34B |
| `mtvec` | 0x305 | `mseccfg` | 0x747 |
| `mstatush` | 0x310 | `mcycle` | 0xB00 |
| `pmpcfg0`..`15` | 0x3A0..0x3AF | `minstret` | 0xB02 |
| `pmpaddr0`..`63` | 0x3B0..0x3EF | `mhpmcounter3`.. | 0xB03.. |
| `mhpmevent3`.. | 0x323.. | | |

### Debug

| CSR | Addr |
|-----|------|
| `tselect`, `tdata1`, `tdata2`, `tdata3`, `tinfo`, `tcontrol` | 0x7A0, 0x7A1, 0x7A2, 0x7A3, 0x7A4, 0x7A5 |
| `mcontext`, `scontext`, `hcontext` | 0x7A8, 0x7AA, 0x6A8 |
| `dcsr`, `dpc`, `dscratch0`, `dscratch1` | 0x7B0, 0x7B1, 0x7B2, 0x7B3 |

### AIA (selected)

`miselect` 0x350, `mireg` 0x351, `mtopei` 0x35C, `mtopi` 0xFB0, `siselect` 0x150, `sireg` 0x151, `stopei` 0x15C, `stopi` 0xDB0, `hvictl` 0x609 **[verify addresses against the AIA spec]**.

---

## 15.4 Instruction encodings: opcode map

(Low 2 bits are `11` for 32-bit instructions. Index = bits `[6:2]`.)

| `[6:5]` \ `[4:2]` | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |
|------|-----|-----|-----|-----|-----|-----|-----|-----|
| 00 | LOAD | LOAD-FP | custom-0 | MISC-MEM | OP-IMM | AUIPC | OP-IMM-32 | 48-bit |
| 01 | STORE | STORE-FP | custom-1 | AMO | OP | LUI | OP-32 | 64-bit |
| 10 | MADD | MSUB | NMSUB | NMADD | OP-FP | OP-V | custom-2 / RV128 | 48-bit |
| 11 | BRANCH | JALR | reserved | JAL | SYSTEM | OP-VE / reserved | custom-3 / RV128 | >= 80-bit |

Custom opcode values: custom-0 `0x0B`, custom-1 `0x2B`, custom-2 `0x5B`, custom-3 `0x7B`.

### Common fixed encodings

| Instruction | Encoding |
|-------------|----------|
| `nop` | `0x00000013` |
| `ret` | `0x00008067` |
| `ecall` | `0x00000073` |
| `ebreak` | `0x00100073` |
| `mret` | `0x30200073` |
| `sret` | `0x10200073` |
| `dret` | `0x7B200073` |
| `wfi` | `0x10500073` |
| `sfence.vma x0, x0` | `0x12000073` |
| `fence.i` | `0x0000100F` |
| `fence rw, rw` | `0x0330000F` |
| `pause` | `0x0100000F` |
| `unimp` (32-bit) | `0xC0001073` |
| `c.nop` | `0x0001` |
| `c.ebreak` | `0x9002` |

---

## 15.5 Debugging checklists

### Illegal-instruction exception (cause 2)

1. Is the extension implemented (`misa`, DTB `riscv,isa-extensions`)? Is it **enabled** (`mstatus.FS/VS`, `menvcfg`, `mstateen`)?
2. FP/vector instruction with `FS`/`VS` = Off? OS enables on first use.
3. CSR access above your privilege or read-only write? Is the CSR present (`time` often traps)?
4. Using `.option arch` correct? Check `riscv64-...-objdump -d` against `-march`.
5. Misaligned PC target with no `C`? (Reports as instruction address misaligned, cause 0.)
6. `mtval` holds the instruction bits on many implementations.

### No interrupts arriving

1. `mstatus.MIE`/`sstatus.SIE` set? Specific `mie`/`sie` bit set? `mideleg` correct?
2. Controller side: PLIC priority > threshold, source enabled for the right context, claim/complete done? AIA `eidelivery`/`eithreshold`/`eie`.
3. Timer: `mtimecmp`/`stimecmp` programmed in the future? `menvcfg.STCE`? Timebase correct?
4. Vector table: `mtvec` mode and alignment; handler saves/restores context.
5. Interrupt still pending after handler: did you clear the cause (device, `mtimecmp`, `sip.SSIP`)?

### Page fault loop

1. Read `scause`, `stval` (faulting VA), `sepc`.
2. Walk the page table by hand for `stval`. PTE `V`, `R/W/X`, `U`, `A/D` (`Svade`).
3. `SUM`/`MXR` as needed. Canonical address? `satp` mode and root PPN?
4. Missing `sfence.vma` after PTE change?
5. Page table memory inaccessible via PMP (access fault vs page fault).

### Hang right after reset/boot

1. JTAG halt; read `pc`, `mcause`, `mepc`, `mtval`.
2. Stack pointer valid? `.bss` cleared? `gp` initialized with `norelax`?
3. Linker script addresses match RAM map? (`-mcmodel=medany`)
4. DRAM initialized before touching it?
5. UART configured; try SBI console.

### Unaligned access behavior

Hardware may trap and emulate (slow) or support natively. Linux `riscv_hwprobe` `CPUPERF_0` reports speed class; `-mstrict-align` avoids misaligned accesses in compiled code.

### Atomics/locking bugs

See Chapter 8 section 8.14.

---

## 15.6 Frequently asked questions

**Q1. Is RISC-V free to use?** The specification is open and royalty-free; implementations can be proprietary or open. Trademarks (the RISC-V name/logo) are governed by RISC-V International.

**Q2. What does RV64GC mean?** `RV64I` + `M A F D` + `Zicsr` + `Zifencei` (that's `G`) + `C`.

**Q3. What should I target for a new Linux-class binary?** Today `rv64gc` is the widest baseline; newer distros and hardware are moving to **RVA23** (adds vector, hypervisor, many extras). Pick based on your target distro/hardware.

**Q4. How do I know which extensions my CPU supports?** `/proc/cpuinfo` (`isa`), device tree `riscv,isa-extensions`, `riscv_hwprobe`, or `misa` in M-mode (single letters only).

**Q5. Why is there no flags register?** Simplicity and scaling: fewer hidden dependencies and easier superscalar design.

**Q6. Why doesn't integer overflow or divide-by-zero trap?** The base ISA never traps on arithmetic; software checks explicitly. Divide-by-zero returns all ones.

**Q7. What is a hart?** A hardware thread: a resource that fetches/executes instructions. Core != hart if SMT.

**Q8. Difference between mepc and sepc?** `mepc` is saved PC for traps taken to M; `sepc` for traps taken to S. `mret`/`sret` use the matching one.

**Q9. How do I switch from M-mode to S-mode?** Set `mstatus.MPP = S`, `mepc` = entry, configure `medeleg/mideleg`, PMP, `satp = 0`, then `mret`.

**Q10. How does a user program make a system call?** `ecall` with syscall number in `a7`, args in `a0`-`a5`, result in `a0` (Linux ABI). The kernel traps (cause 8), advances `sepc` by 4.

**Q11. How does the kernel talk to firmware?** SBI via `ecall` from S-mode (`a7` = EID, `a6` = FID).

**Q12. What is the difference between PMP and paging?** PMP restricts **physical** address ranges (M-mode controlled, few entries, produces access faults). Paging translates and restricts **virtual** addresses (S-mode controlled, per-page, produces page faults).

**Q13. What is a page fault vs access fault?** Page fault: translation/permission failure in page tables. Access fault: PMP/PMA violation (including during page walks).

**Q14. How big is the address space?** Sv39 = 512 GiB virtual (256 GiB per half); Sv48 = 256 TiB; Sv57 = 128 PiB. Physical addresses up to 56 bits.

**Q15. Why does `ld` of a 32-bit value need sign extension on RV64?** The ABI keeps 32-bit values sign-extended; use `lw` (sign-extending) or `lwu` (zero-extending) as appropriate.

**Q16. Why are there `W` instructions only on RV64?** They operate on 32-bit values in 64-bit registers with sign-extended results (`addw`, `sllw`...).

**Q17. What are `lui` + `addi` for?** Build 32-bit constants; remember the sign-correction when bit 11 is set.

**Q18. Is the stack 16-byte aligned?** Yes at call boundaries in standard ABIs (RV32E/RV64E reduce this).

**Q19. How do I atomically increment a counter?** `amoadd.w`/`amoadd.d`.

**Q20. How do I write a spinlock?** `amoswap.w.aq` to acquire, `amoswap.w.rl x0, x0, (lock)` to release; add `pause`/`wrs.nto`.

**Q21. Why did my x86 lock-free code break?** x86 is TSO; RISC-V is weaker. Add acquire/release or fences, or use `Ztso` hardware.

**Q22. Do I need `fence.i` after loading code?** Yes (on each hart that will run it), unless a newer mechanism (`Zjid`) is available.

**Q23. How do I measure time?** `rdtime` (constant-rate timebase), `rdcycle` (core cycles); counters must be enabled by `mcounteren`/`scounteren`.

**Q24. What is the difference between `time` and `cycle`?** `time` ticks at the platform timebase (read-only shadow of `mtime`); `cycle` counts core clock cycles (may vary with frequency).

**Q25. How do harts start?** Firmware chooses a boot hart; others wait. The OS starts them with SBI `hart_start`.

**Q26. What is the difference between OpenSBI and U-Boot?** OpenSBI is resident M-mode runtime (SBI). U-Boot is a bootloader running in S/HS-mode (or M-mode on some platforms) that loads the kernel.

**Q27. Can I run RV32 binaries on RV64 hardware?** Only if the hardware supports RV32 compatibility at lower privilege (`UXL/SXL`); not guaranteed. RVA23 requires `Ssu64xl` (RV64 user) but no RV32 support.

**Q28. What is a custom extension and is it allowed?** Vendor-defined instructions in custom opcode space (`X*`). Allowed, but software depending on them is non-portable.

**Q29. What is RVA23?** The 2023-generation application-processor profile: mandates vector, hypervisor (in S64), many smaller extensions; the baseline for modern Linux-class systems.

**Q30. How do I learn the exact behavior of an instruction?** Read the ISA manual (docs.riscv.org); test with Spike/QEMU; check Sail model.

**Q31. Why is `x0` not renamed?** It's hardwired zero; reads give zero, writes are discarded.

**Q32. What does `la` expand to?** `auipc` + `addi` (non-PIC) or `auipc` + `ld` through GOT (PIC).

**Q33. Why do I get "relocation truncated to fit"?** Code model mismatch (`medlow` vs `medany`), branch out of range (use `call`/`jump` forms), or too-large `gp`-relative data.

**Q34. What is NaN-boxing for?** So single-precision values live safely in double-precision registers; invalid boxing reads as a canonical NaN.

**Q35. How do vectors differ from SIMD?** Length-agnostic, per-hart `vl`, mask registers, register grouping.

**Q36. How do I enable the vector unit in an OS?** Set `mstatus.VS` (or `sstatus.VS`) to Initial/Clean/Dirty; Linux enables lazily on first use.

**Q37. Can RISC-V do virtualization?** Yes, with the `H` extension (HS/VS/VU, two-stage translation); required in RVA23S64 via `Sha`.

**Q38. What is the "time" CSR trap?** If hardware lacks `time`, reading it traps, and firmware emulates it by reading `mtime`.

**Q39. How do I handle many interrupt sources?** Use AIA (APLIC + IMSIC) with MSIs; PLIC for small systems.

**Q40. What is the best first project?** Write an assembly program, run under QEMU/Spike, then a bare-metal UART program (Chapter 9), then boot Linux under QEMU (Chapter 10).

---

## 15.7 Learning resources

### Specifications and standards

| Resource | URL |
|----------|-----|
| Ratified specification library | https://docs.riscv.org/ |
| ISA manual source | https://github.com/riscv/riscv-isa-manual |
| Specs under development | https://riscv.org/specifications/development/ |
| psABI | https://github.com/riscv-non-isa/riscv-elf-psabi-doc |
| SBI | https://github.com/riscv-non-isa/riscv-sbi-doc |
| Assembly programmer's manual | https://github.com/riscv-non-isa/riscv-asm-manual |
| Vector intrinsics | https://github.com/riscv-non-isa/rvv-intrinsic-doc |
| Debug spec | https://github.com/riscv/riscv-debug-spec |
| Sail model | https://github.com/riscv/sail-riscv |

### Books and courses

- *Computer Organization and Design: RISC-V Edition* (Patterson and Hennessy).
- *The RISC-V Reader* (Patterson and Waterman).
- *Computer Architecture: A Quantitative Approach* (RISC-V content in recent editions).
- UC Berkeley **CS61C** (assembly and architecture with RISC-V).
- MIT **6.S081** (xv6-riscv operating systems).
- ETH Zurich and other university architecture courses using RISC-V.
- Linux Foundation / RISC-V International training courses.

### Code to read

| Project | Why |
|---------|-----|
| `riscv-tests`, `riscv-arch-test` | ISA tests, examples of every instruction |
| Spike (`riscv-isa-sim`) | Reference simulator source |
| xv6-riscv | Small teaching OS |
| OpenSBI | Reference firmware |
| Linux `arch/riscv` | Real OS port |
| Ibex, CVA6, Rocket, BOOM | Cores of increasing complexity |
| `riscv-dv`, `riscv-formal` | Verification |
| Chipyard | SoC generator |
| `riscv-unified-db` (UDB) **[verify name]** | Machine-readable ISA data |

### Tools

Spike, QEMU, Renode, gem5, Verilator, OpenOCD, GDB, Compiler Explorer (godbolt.org), `riscv-gnu-toolchain`, LLVM, `dtc`, Linux `perf`.

### Practice path

1. Write small assembly programs (loops, strings, recursion) and run with Spike or QEMU user-mode.
2. Hand-encode instructions and compare with `objdump`.
3. Write a bare-metal UART program (Chapter 9).
4. Implement a trap handler and a timer interrupt (Chapter 5).
5. Enable Sv39 paging in a toy kernel (Chapter 6).
6. Read xv6-riscv; boot Linux under QEMU with OpenSBI (Chapter 10).
7. Optimize a loop with the vector extension (Chapter 4).
8. Build or simulate a small core (Ibex/PicoRV32) and run `riscv-tests`.

---

## 15.8 Closing notes

- **Accuracy policy:** Statements marked **[verify]** are not confirmed from primary sources in this session. Statements about the ISA manual version (v20260120), the RVA23 mandatory/optional lists, and SBI 3.0 ratification were checked on 2026-10-22.
- **Where to extend:** Add your own notes as you learn: new extensions, errata, vendor-specific behavior, and board bring-up logs.
- **Suggested next steps:** Pick a target (embedded MCU, Linux SBC, server, accelerator), read the matching profile/platform spec and the vendor TRM, and keep this dictionary beside the ISA manual.

[Index](00_README.md)
