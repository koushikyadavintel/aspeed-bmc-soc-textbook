# The RISC-V Textbook and Reference

A teaching text and lookup dictionary for the RISC-V architecture, from first principles to advanced platform topics.

- **Compiled:** 2026-10-22
- **How to use it:** Read Parts I-III in order to learn. After that, use the index, the glossary (Chapter 15) and the FAQ (Chapter 15) to jump to answers.
- **Nature of this text:** Unofficial study notes, not a RISC-V International publication. RISC-V is a trademark of RISC-V International, and the specification text is copyright RISC-V International. The official specifications always take precedence; see the links in section 3.

---

## 1. Table of contents

| Ch | File | Topic | Level |
|----|------|-------|-------|
| 01 | [01_Foundations.md](01_Foundations.md) | What RISC-V is, history, governance, ecosystem, terminology | Beginner |
| 02 | [02_Base_ISA.md](02_Base_ISA.md) | Registers, encodings, every RV32I/RV64I instruction, pseudoinstructions | Beginner |
| 03 | [03_Standard_Extensions.md](03_Standard_Extensions.md) | M, A, F, D, Q, C, Zc*, B/Zb*, Zicond, Zicbo*, crypto, hints, and more | Intermediate |
| 04 | [04_Vector_Extension.md](04_Vector_Extension.md) | RVV 1.0: vtype, LMUL, masking, loads/stores, examples, crypto | Intermediate |
| 05 | [05_Privileged_Architecture.md](05_Privileged_Architecture.md) | Modes, CSRs, traps, interrupts, delegation, PMP, counters | Intermediate |
| 06 | [06_Virtual_Memory.md](06_Virtual_Memory.md) | Sv32/Sv39/Sv48/Sv57, PTEs, page walk, TLB, Svpbmt, Svnapot, A/D | Intermediate |
| 07 | [07_Hypervisor_AIA_IOMMU.md](07_Hypervisor_AIA_IOMMU.md) | H extension, two-stage translation, AIA (APLIC/IMSIC), IOMMU, PLIC/CLINT | Advanced |
| 08 | [08_Memory_Model_Atomics.md](08_Memory_Model_Atomics.md) | RVWMO, Ztso, fences, LR/SC, AMOs, C11 mapping, litmus tests | Advanced |
| 09 | [09_ABI_Toolchain_Assembly.md](09_ABI_Toolchain_Assembly.md) | Calling convention, ELF, relocations, GCC/LLVM, assembler, bare-metal example | Intermediate |
| 10 | [10_Boot_SBI_Firmware_Linux.md](10_Boot_SBI_Firmware_Linux.md) | Boot chain, SBI, OpenSBI, device tree, UEFI/ACPI, Linux | Intermediate |
| 11 | [11_Microarchitecture_Implementations.md](11_Microarchitecture_Implementations.md) | Pipelines, OoO, caches, open cores, commercial cores, boards | Advanced |
| 12 | [12_Security_CFI_TEE.md](12_Security_CFI_TEE.md) | PMP/ePMP, CFI, pointer masking, TEEs, secure boot, side channels | Advanced |
| 13 | [13_Debug_Trace_Perf_RAS.md](13_Debug_Trace_Perf_RAS.md) | Debug spec, triggers, trace, counters, RAS | Advanced |
| 14 | [14_Emerging_Topics.md](14_Emerging_Topics.md) | Newer and in-development work, with status labels | Advanced |
| 15 | [15_Glossary_Tables_FAQ.md](15_Glossary_Tables_FAQ.md) | Glossary, CSR table, opcode map, debugging checklists, FAQ, resources | Reference |

Suggested paths:

- **Software or compiler person:** 01, 02, 03, 09, 08, then 10.
- **OS or firmware person:** 01, 02, 05, 06, 10, then 07, 12.
- **Hardware or verification person:** 01, 02, 05, 06, 08, 11, 13.
- **Just want a dictionary:** go straight to 15.

---

## 2. Status legend (used throughout)

RISC-V International moves specifications through a lifecycle. Each topic in this text carries a label.

| Label | Meaning |
|-------|---------|
| **Ratified** | Approved by the RISC-V International Board. Ratified extensions are never revised; fixes come as follow-on extensions. |
| **Frozen** | Public review done or in progress; changes highly unlikely. |
| **Stable** | Mostly settled; only limited refinements expected. |
| **Draft** | Still evolving. Do not assume it will ship in this form. |
| **Impl-specific** | Behavior of a particular core, SoC, or vendor, not of RISC-V in general. |
| **[verify]** | A detail I could not confirm from a primary source while writing. Check the linked specification before relying on it. |

> The lifecycle wording (Draft/Development, Stable, Frozen, Ratified) comes from the RISC-V International specifications page.

---

## 3. Source snapshot (what was actually checked)

These were fetched from primary sources on 2026-10-22 and are the anchor for version-sensitive statements.

| Item | Version/status seen | Source |
|------|--------------------|--------|
| Unprivileged ISA manual | **v20260120** (January 2026) | https://docs.riscv.org/reference/isa/v20260120/unpriv/intro.html |
| Privileged ISA manual | **v20260120** (January 2026) | https://docs.riscv.org/reference/isa/priv/priv-index.html |
| Ratified spec library | HTML + PDF per spec | https://docs.riscv.org/reference/home/index.html |
| RVA23 profile (U64 and S64) | Mandatory/optional lists used in Ch. 3, 14 | riscv/riscv-profiles `rva23-profile.adoc` (repo shows **archived/read-only on 2026-07-24**; profile text now lives in the unified spec library, so check docs.riscv.org for the current home) |
| SBI | **3.0, Ratified** (released 2025-07-16) | https://github.com/riscv-non-isa/riscv-sbi-doc/releases |
| Extension naming rules | ISA manual chapter 36.1 | https://docs.riscv.org/reference/isa/v20260120/unpriv/naming.html |

Everything else (microarchitecture, ecosystem, boards, third-party software) is written from established knowledge of the field and marked **[verify]** where it is likely to have changed. RISC-V moves quickly; for any decision that matters, confirm against:

1. Spec library: https://docs.riscv.org/
2. Specs under development: https://riscv.org/specifications/development/
3. Ratified extensions list: https://riscv.atlassian.net/wiki/spaces/HOME/pages/16154732/Ratified+Extensions
4. ISA manual source: https://github.com/riscv/riscv-isa-manual
5. psABI: https://github.com/riscv-non-isa/riscv-elf-psabi-doc
6. SBI: https://github.com/riscv-non-isa/riscv-sbi-doc
7. Linux RISC-V docs: https://docs.kernel.org/arch/riscv/

---

## 4. Conventions in this text

- `monospace` is code, registers, CSRs, instruction mnemonics.
- Bit ranges use Verilog-like notation: `x[7:0]` means bits 7 down to 0.
- `XLEN` is the integer register width (32 or 64). `FLEN` is the FP register width. `VLEN` is the vector register width in bits.
- Numbers: `0x` prefix is hexadecimal, `0b` prefix is binary.
- "Hart" means hardware thread (see Ch. 1).
- Assembly examples use GNU assembler syntax. Comments start with `#`.
- Where a spec says **UNSPECIFIED**, the behavior is intentionally left open; platforms or implementations may define it.

---

## 5. Quick orientation: the five-minute RISC-V

1. RISC-V is an **open instruction set architecture** (ISA). Anyone may build chips or software for it without paying an ISA license.
2. It is a **modular family**: a tiny mandatory base (`I`, or `E`) plus optional extensions (`M`, `A`, `F`, `D`, `C`, `V`, ...).
3. The base ISAs are **RV32I, RV64I, RV32E, RV64E** (RV128I is reserved for the future).
4. `RV64GC` historically meant "64-bit general-purpose": `I M A F D` + `Zicsr` + `Zifencei` + `C`. Modern Linux-class systems target **profiles** such as **RVA23**, which also mandate Vector (`V`), the hypervisor (`H`), and many smaller extensions.
5. Instructions are 32 bits by default, 16 bits with `C`, and the encoding reserves room for longer ones.
6. There are three main privilege modes: **Machine (M)**, **Supervisor (S)**, **User (U)**. The **H extension** adds virtualization modes.
7. Software talks to firmware through the **SBI**. Hardware identity and features are discovered via **CSRs**, **device tree**, **ACPI**, or **OS interfaces** (not a CPUID instruction).

Next: [Chapter 1 - Foundations](01_Foundations.md)
