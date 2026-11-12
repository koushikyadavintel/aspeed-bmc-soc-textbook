# Chapter 14 - Emerging and Advanced Topics

[Index](00_README.md) | Prev: [Ch 13](13_Debug_Trace_Perf_RAS.md) | Next: [Ch 15 - Glossary, Tables, FAQ](15_Glossary_Tables_FAQ.md)

**Goals:** Orient yourself in the fast-moving edge of RISC-V: recently ratified extensions, work in progress, profiles beyond RVA23, ecosystem trends, and how to keep this knowledge current.

> **Read this first.** This chapter is the most perishable in the book. Everything here is labeled by confidence:
> - **Confirmed (2026-10-22):** seen in a primary source during writing.
> - **Reported:** widely reported or known from my background knowledge, not re-fetched.
> - **[verify]:** status uncertain; check the linked source.
>
> Rule: if a spec is not in the ratified library (https://docs.riscv.org/), treat it as **Draft**.

---

## 14.1 What is confirmed as current (snapshot)

| Item | Status | Basis |
|------|--------|-------|
| Unprivileged and Privileged ISA manuals **v20260120** (January 2026) | **Confirmed** | docs.riscv.org spec library |
| RVA23 (U64, S64) profile: mandatory/optional lists used in Chapter 3 | **Confirmed** | `rva23-profile.adoc` fetched; the `riscv-profiles` repository was seen **archived (read-only) on 2026-07-24**, meaning profile text moved elsewhere (look in the unified spec library) |
| RVA23 mandates `V`, `Zvfhmin`, `Zvbb`, `Zvkt`, `Zicond`, `Zimop`, `Zcmop`, `Zcb`, `Zfa`, `Zawrs`, `Zihintntl`, `Supm`; S64 adds `Sha` (hypervisor), `Svnapot`, `Sstc`, `Sscofpmf`, `Ssnpm`, `Ssu64xl`, `Ss1p13` | **Confirmed** | same source |
| RVA23 options include `Zabha`, `Zacas`, `Zvbc`, `Zama16b`, `Ziccamoc` (development); `Zicfilp`, `Zicfiss`, `Zfh`, `Zbc`, `Zvfh`, BF16 (expansion); `Sv48`, `Sv57`, `Svadu`, `Sdtrig`, `Ssstrict`, `Svvptc`, `Sspm`, `Zkr` (S-mode expansion) | **Confirmed** | same source |
| RVA23 text says a new instruction-cache coherence mechanism, tentatively **`Zjid`**, is under development; `Zifencei` stays mandatory meanwhile | **Confirmed** | same source |
| SBI **v3.0 ratified** (2025-07-16) | **Confirmed** | riscv-sbi-doc releases |
| Spec lifecycle: Draft/Development -> Stable -> Frozen -> Ratified; ratified specs are never revised | **Confirmed** | riscv.org specifications page |

## 14.2 Ratified extension families to know (by theme)

> Ratified dates are omitted deliberately; the ISA manual lists versions. Treat the column "Where it matters" as practical guidance.

| Theme | Extensions | Where it matters |
|-------|-----------|------------------|
| Bit manipulation | `Zba`, `Zbb`, `Zbs`, `Zbc`, `Zbkb`, `Zbkc`, `Zbkx` | Compilers, crypto, string routines |
| Cache management | `Zicbom`, `Zicbop`, `Zicboz` | DMA, `memset`/`clear_page` |
| Conditional | `Zicond` | Branchless code |
| Atomics | `Zaamo`, `Zalrsc`, `Zacas`, `Zabha`, `Zawrs` | Locks, lock-free structures |
| FP | `Zfh`, `Zfhmin`, `Zfbfmin`, `Zfa`, `Zfinx` family | AI/graphics, FP conformance |
| Vector | `V`, `Zve*`, `Zvl*`, `Zvfh`, `Zvfhmin`, `Zvfbfmin`, `Zvfbfwma`, `Zvbb`, `Zvbc`, `Zvk*` | HPC, AI, crypto, media |
| Compressed | `Zca`, `Zcb`, `Zcd`, `Zcf`, `Zcmp`, `Zcmt`, `Zcmop` | Code size |
| Hints/ops | `Zihintpause`, `Zihintntl`, `Zimop` | Spin loops, caches, CFI |
| Memory model | `Ztso` | x86 emulation/porting |
| Privileged: virtual memory | `Sv39/48/57`, `Svpbmt`, `Svnapot`, `Svinval`, `Svadu`, `Svade`, `Svvptc` | OS memory management |
| Privileged: timers/counters | `Sstc`, `Sscofpmf`, `Smcntrpmf` **[verify]** | Tickless OS, perf sampling |
| Privileged: state | `Smstateen`/`Ssstateen`, `Smcsrind`/`Sscsrind` | Virtualization, AIA |
| Virtualization | `H` (Hypervisor), `Sha` (profile), AIA, IOMMU | Cloud, servers |
| Security | `Smepmp`, `Zicfilp`, `Zicfiss`, pointer masking (`Sm/Ss/Supm`...), `Zkr`, `Zkt` | Hardened OS/firmware |
| Debug/trace | Debug 1.0, `Sdtrig`, E-Trace, N-Trace, `Smrnmi` | Bring-up, safety |
| Reliability | `Smdbltrp`/`Ssdbltrp` (double trap), RERI **[verify]** | Data center, automotive |
| QoS | `Ssqosid` and the CBQRI (capacity/bandwidth QoS register interface) **[verify]** | Cloud isolation |

## 14.3 Work likely still Draft or recently ratified **[verify each]**

| Topic | What it is | Why it matters |
|-------|-----------|----------------|
| **`P` (Packed SIMD)** | SIMD on integer registers (8/16/32-bit lanes) | DSP/embedded without vector hardware cost |
| **Matrix extensions** | Integrated and attached matrix multiply-accumulate (IME/AME style) and vector dot-product instructions (e.g., `Zvqdotq`) | AI inference/training |
| **FP8 (OFP8) and more BF16** | 8-bit float formats (conversions/dot products), vector BF16 arithmetic | LLM inference |
| **Vector additions** | Vector zip/unzip/permutes, absolute-difference ops, more bit-manip | Media, networking |
| **`Zjid`** | Instruction-cache coherence mechanism replacing global `fence.i` use | Efficient JIT, multi-hart code patching |
| **`Zalasr`** | Load-acquire / store-release instructions | Cheaper C11 atomics |
| **`Zibi`** | Branch-with-immediate compare **[verify name/status]** | Smaller/faster code |
| **`Zilsd`/`Zclsd`** | RV32 load/store of 64-bit data via register pairs | Embedded RV32 double loads |
| **`Smmtt`** | Table-based physical memory isolation | Confidential computing at scale |
| **CoVE / AP-TEE** | Confidential VMs (TSM/TVM model) | Cloud confidential computing |
| **WorldGuard, IOPMP** | Multi-world and DMA-master protection | SoC security |
| **`Svukte`** | Side-channel hardening for user vs kernel addresses | Meltdown-class mitigation |
| **CHERI for RISC-V** | Capability-based memory safety (`Zcheri*`); 128/64-bit capabilities | Spatial/temporal safety |
| **Nested virtualization improvements, NACL** | Efficient hypervisor-in-hypervisor | Cloud nesting |
| **Counter delegation, CTR (`Smctr/Ssctr`)** | Cheap profiling and branch records | Performance engineering |
| **Newer profile generations** (successor to RVA23, e.g., an "RVA30"-class) | Next common baseline | Software baselines; check profile pages |
| **Microcontroller profiles (RVM-series)** | Baselines for MCU-class `Zce`-style code | Embedded ecosystem |
| **RISC-V Server Platform / Server SoC, BRS** | Platform standardization (boot, RAS, ACPI, PCIe) | Data-center interoperability |
| **Formal specification (Sail), Unified Database** | Machine-readable ISA description (opcodes, CSRs, extension metadata) | Tooling, verification |

## 14.4 CHERI and memory safety

**CHERI** (Capability Hardware Enhanced RISC Instructions) replaces raw pointers with **capabilities**: bounded, permission-carrying, unforgeable pointers enforced by hardware.

- Prototypes: CHERI-RISC-V (Cambridge/SRI), CHERIoT (Microsoft, 32-bit embedded variant), Morello (Arm).
- RISC-V International has a CHERI working group developing standard extensions **[verify status]**.
- Benefits: eliminates classes of spatial memory errors; enables compartmentalization.
- Costs: ABI change (pure-capability mode), larger pointers, software porting effort.

Related, available now: pointer masking (software tagging), CFI (`Zicfilp/Zicfiss`), Linux hardening, Rust adoption.

## 14.5 AI and accelerator trends

- **Vector + matrix:** RVV 1.0 is the base; matrix extensions are specified to avoid proprietary tensor ISAs.
- **Custom accelerators:** companies pair many small RISC-V cores with tensor engines (examples: Tenstorrent, Esperanto-style designs) **[verify]**.
- **BF16/FP16/FP8 types** are first-class in vector extensions.
- **Software stack:** LLVM auto-vectorization (RVV), `riscv_vector.h` intrinsics, MLIR/IREE/TVM backends, OpenBLAS/BLIS kernels for RVV, XNNPACK/ONNX Runtime RVV paths **[verify]**.
- **Edge:** MCU-class RISC-V cores with `Zve*`/`P` for TinyML.

## 14.6 Data center, cloud, and HPC

- RVA23 + `Sha` + AIA + IOMMU + SBI 3.0 create a baseline comparable to server Arm/x86 platforms.
- Many-core chips (for example, 64-core Sophgo SG2042-class) and server designs (Ventana, Tenstorrent, others) **[verify]**.
- **HPC:** European initiatives (EPI, MareNostrum Experimental, Barcelona Supercomputing Center) and national programs target RISC-V **[verify]**.
- Cloud-native: Kubernetes/containers on riscv64 images; QEMU/KVM; CI on RISC-V runners.
- Needs maturity in: RAS, firmware (UEFI/ACPI), remote management (BMC integration), enterprise Linux certifications, performance tuning.

## 14.7 Embedded, automotive, and space

- **MCU/IoT:** vast majority of shipping RISC-V cores today (billions of units, mostly in embedded controllers inside SoCs, storage, and IoT).
- **Automotive:** ISO 26262 ASIL-qualified cores; the industry has formed collaborations to define common RISC-V automotive platforms (for example, a multi-company JV announced around 2023-2025) **[verify]**.
- **Space:** radiation-hardened RISC-V (NASA HPSC chiplets with SiFive X280-class cores, ESA/European programs, others) **[verify]**.
- Safety standards: use of `Smrnmi`, lockstep, RERI, `Smdbltrp`, and safety manuals.

## 14.8 Software ecosystem milestones (reported, **[verify]**)

- **Linux:** mainline since 4.15; steady additions (vector, hwprobe, KVM, AIA, IOMMU, CFI, ACPI).
- **Distributions:** Debian official `riscv64` port (13 "trixie"), Fedora, openSUSE, Ubuntu riscv64; discussions or decisions to adopt **RVA23** as the baseline for newer releases (Ubuntu reported).
- **Android:** Google announced RISC-V support (2023) and has been working toward making RISC-V a supported architecture; reports indicate RVA23 as the target baseline **[verify]**.
- **Toolchains:** GCC, LLVM/Clang, Rust, Go, OpenJDK, V8/SpiderMonkey/JavaScriptCore JITs, PyTorch/TensorFlow Lite ports.
- **Gaming/desktop:** RISC-V laptops/boards, Vulkan/Mesa support for some GPUs (PCIe) **[verify]**.
- **Windows:** not generally supported **[verify]**.

## 14.9 Governance and process trends

- Specs are being **unified into a single ISA manual** (unprivileged + privileged) with per-chapter extension status, and published through `docs.riscv.org`; the profile text is moving into the unified library (note the archived `riscv-profiles` repository).
- A **Unified Database (UDB)** and Sail model aim to be the machine-readable source of truth **[verify]**.
- **Compatibility and certification programs**: efforts exist for software/hardware compatibility testing aligned with profiles and platforms **[verify]**.
- **Release cadence:** yearly profile releases (RVA20 -> RVA22 -> RVA23, ...) and periodic manual snapshots (the v20260120 label is a date: 2026-01-20).

## 14.10 How to stay current (practical)

| Source | What for |
|--------|----------|
| https://docs.riscv.org/ | Ratified specifications (HTML/PDF) |
| https://riscv.org/specifications/development/ | What is under development |
| https://tech.riscv.org/ | Technical Hub, specification explorer |
| https://github.com/riscv/riscv-isa-manual | ISA manual source and issues; look at release tags |
| https://github.com/riscv-non-isa | psABI, SBI, toolchain conventions, platform and boot specs |
| https://github.com/riscv-software-src | Spike, riscv-tests, tools |
| LLVM `RISCVUsage` doc / GCC release notes / binutils NEWS | Which extensions your toolchain supports |
| Linux `Documentation/arch/riscv/` and `linux-riscv` mailing list | Kernel support |
| QEMU changelog | Emulated extension support |
| LWN.net, Phoronix, RISC-V International news | Ecosystem news |
| RISC-V Summit and workshop slides | Roadmaps |

### A method for checking any claim

1. Find the **extension name** and its **ratification** state in the spec library.
2. Check **toolchain support** (`-march` accepted? LLVM/GCC release notes).
3. Check **kernel support** (config option, hwprobe key).
4. Check **hardware**: does the core you target implement it? (core manual; device tree `riscv,isa-extensions`).
5. Check **profile membership** (is it mandatory/optional in your target profile).

## 14.11 Chapter summary

- The **confirmed** baseline in this text: ISA manual v20260120, RVA23 profile contents, SBI 3.0 ratified.
- Active areas: AI/matrix and low-precision FP, confidential computing (CoVE, Smmtt), CFI adoption, instruction-cache coherence (`Zjid`), CHERI, platform specs for servers, and profile generations after RVA23.
- Always verify extension status, toolchain/kernel support, and hardware before relying on a feature.

### Check yourself

1. Which RVA23 option is intended to become mandatory in a future profile (name two)?
2. What problem does `Zjid` aim to solve?
3. Where do you check whether an extension is ratified?
4. What is the difference between pointer masking and CHERI?
5. List the five checks for adopting a new extension.

<details><summary>Answers</summary>

1. Development options: `Zabha`, `Zacas`, `Ziccamoc`, `Zvbc`, `Zama16b`.
2. Efficient instruction-cache coherence for code modification without relying on `fence.i` semantics alone.
3. docs.riscv.org (ratified library) and the specs-under-development page.
4. Pointer masking ignores top address bits to allow software tags; CHERI enforces bounds and permissions in hardware with capabilities.
5. Spec status, toolchain support, kernel support, hardware support, profile membership.
</details>

Next: [Chapter 15 - Glossary, Tables, FAQ](15_Glossary_Tables_FAQ.md)
