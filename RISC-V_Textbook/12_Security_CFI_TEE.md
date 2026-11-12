# Chapter 12 - Security: Protection, CFI, Pointer Masking, and Trusted Execution

[Index](00_README.md) | Prev: [Ch 11](11_Microarchitecture_Implementations.md) | Next: [Ch 13 - Debug, Trace, Performance, RAS](13_Debug_Trace_Perf_RAS.md)

**Goals:** Know the layers of security RISC-V offers: privilege and memory protection (PMP, Smepmp, paging, IOMMU), control-flow integrity (landing pads and shadow stacks), pointer masking, side-channel-aware features, entropy and crypto, and the architectures for trusted execution and secure boot.

> Status labels follow the RISC-V International lifecycle. Items marked **[verify]** may have moved between Draft and Ratified; check https://riscv.org/specifications/development/ and the ISA manual.

---

## 12.1 Threat model and security layers

| Layer | Mechanism | Chapter |
|-------|-----------|---------|
| Privilege separation | M / S / U (and HS / VS / VU) | 5, 7 |
| Physical memory isolation | PMP, Smepmp, Smmtt | 5, 12 |
| Virtual memory isolation | Paging, `U` bit, `SUM`, `MXR`, NX | 6 |
| DMA isolation | IOMMU, IOPMP | 7, 12 |
| Control-flow integrity | `Zicfilp`, `Zicfiss` | 12 |
| Memory-safety support | Pointer masking (software tagging), CHERI (draft) | 12, 14 |
| Side-channel resistance | `Zkt`, `Zvkt`, `Svukte` (draft **[verify]**), constant-time rules | 3, 12 |
| Secrets and randomness | `Zkr` (`seed`), scalar/vector crypto | 3, 4 |
| State isolation | `Smstateen`/`Ssstateen` | 5 |
| Trusted execution | PMP-based enclaves, CoVE/AP-TEE, WorldGuard | 12 |
| Platform root of trust | OpenTitan, Caliptra, secure boot, measured boot | 12 |
| Fault resilience | `Smrnmi`, RERI, double-trap handling | 5, 13 |

## 12.2 Memory protection recap and hardening

### Page-based protection (S-mode)

- `U` pages are not executable from S-mode ever; data access only if `sstatus.SUM=1`.
- Use W^X: never map a page both writable and executable (hardware allows it; policy should forbid).
- `MXR` makes executable pages readable; keep off by default.
- Guard pages: unmapped (`V=0`) pages around stacks.
- Randomize layouts (ASLR); Linux does this in user and kernel (KASLR) on RISC-V.

### PMP and Smepmp (M-mode isolation of physical memory)

- Locked PMP entries (`L=1`) bind M-mode too; freeze firmware regions (ROM, firmware RAM).
- **Smepmp**: `MML` prevents M-mode from executing U-mode-accessible pages and S/U from executing M-owned pages; `MMWP` default-denies M-mode when no entry matches; `RLB` is a temporary unlock bit that must be cleared and locked before running untrusted code.
- A typical secure setting: configure PMP early, set `mseccfg.MML=1, MMWP=1`, clear `RLB`.

### Smmtt (Supervisor Domain Access Protection, memory tracking tables) **[verify status]**

PMP's entry count limits scalability. `Smmtt` adds table-based per-domain physical-memory permissions (supervisor domains), enabling many isolated guests/enclaves; required by the **CoVE** confidential-computing work.

### WorldGuard (`Smwg`, `Sswg`) **[verify status]**

World IDs (WIDs) assigned to harts and bus masters; checkers at memory/peripherals enforce per-world permissions, similar in spirit to TrustZone worlds but with many worlds.

### IOPMP **[verify status]**

Physical-memory protection for **bus masters** (DMA engines, devices), complementing the IOMMU when no translation is needed.

## 12.3 Control-Flow Integrity (CFI)

**Ratified (2024).** Optional in RVA23 as **expansion** options (`Zicfilp`, `Zicfiss`). Two complementary mechanisms:

| Mechanism | Protects | Extension |
|-----------|----------|-----------|
| **Forward-edge**: indirect calls/jumps must land on a **landing pad** | JOP/COP-style attacks | `Zicfilp` |
| **Backward-edge**: returns must match a **shadow stack** | ROP attacks | `Zicfiss` |

Both reuse **may-be-operations** (`Zimop`, `Zcmop`), so CFI-instrumented binaries run on older hardware as no-ops.

### `Zicfilp`: landing pads

- New instruction: `lpad imm20`, encoded as `auipc x0, imm20` (harmless on hardware without the extension).
- A hidden state **ELP** (expected landing pad) is set when an **indirect call or jump** (`jalr`/`c.jalr`/`c.jr`) executes. Jumps whose source register is `x7` (`t2`) are "software-guarded" and do not set ELP (used for PLT stubs). While ELP is set, the *next* instruction must be `lpad`; anything else raises a **software-check exception** (cause 18, `xtval = 2` for landing-pad violation **[verify]**).
- **Labels:** `lpad` carries a 20-bit label; if non-zero it must equal `x7[31:12]` set by the caller (coarse-grained type check, e.g., a function-signature hash).
- The target of an `lpad` must be 4-byte aligned.
- Enable per mode: `menvcfg.LPE`, `senvcfg.LPE`, `henvcfg.LPE`; `mstatus.SPELP`/`MPELP` save ELP across traps.
- Compiler flag: `-fcf-protection=branch` (GCC) / `-fcf-protection=branch` (Clang) with `-march=..._zicfilp` **[verify flag spelling]**.

```asm
    lui   t2, 0x12345         # label in x7[31:12]
    jalr  ra, 0(t0)           # indirect call (t0 is not x7)
callee:
    lpad  0x12345             # first instruction at the target; label 0 would match any caller
    ...
```

### `Zicfiss`: shadow stack

- A separate **shadow stack** holds copies of return addresses; the `ssp` CSR (0x011) is its pointer.
- Instructions: `sspush x1/x5` (push link register), `sspopchk x1/x5` (pop and compare with the link register, raise a software-check exception on mismatch), `ssrdp rd` (read `ssp`), `ssamoswap.w/.d` (atomic swap on shadow stack memory), plus compressed `c.sspush`, `c.sspopchk`.
- **Shadow stack pages** are marked with the otherwise-reserved PTE encoding `R=0, W=1, X=0`. Ordinary loads/stores to them fault; only shadow-stack instructions can write; this prevents attackers from corrupting them with normal stores.
- Enable: `menvcfg.SSE`, `senvcfg.SSE`, `henvcfg.SSE`.
- Failure: **software-check exception** (cause 18, `xtval = 3` for shadow-stack violation **[verify]**).

Prologue/epilogue with both:

```asm
func:
    lpad   0
    sspush ra                 # push ra on shadow stack
    addi   sp, sp, -16
    sd     ra, 8(sp)
    ...
    ld     ra, 8(sp)
    addi   sp, sp, 16
    sspopchk ra               # fault if ra was tampered with
    ret
```

OS support: kernels allocate shadow stacks (`map_shadow_stack`-style syscalls) and context-switch `ssp`; Linux user-space shadow stack and landing-pad support for RISC-V were being merged around 6.x **[verify kernel status]**. SBI **FWFT** can enable/disable landing pads and shadow stacks for S-mode (`LANDING_PAD`, `SHADOW_STACK`).

## 12.4 Pointer masking

**Ratified (2024):** `Smnpm`, `Smmpm`, `Ssnpm`, `Sspm`, `Supm`.

- Allows software to use upper bits of a pointer for **tags** without masking by hand: hardware ignores the top `PMLEN` bits on **data** accesses (not instruction fetch).
- Field `PMM` in `mseccfg` (machine), `menvcfg` (S/U), `senvcfg` (U), `henvcfg` (guests) selects `PMLEN`: **0** (disabled), **7**, **16** (for Sv39/Sv48/Sv57 contexts).
- Use cases: software memory tagging (HWASan-style), garbage collectors and language runtimes storing metadata in pointers, sanitizers.
- **RVA23:** mandates `Supm` (U-mode) and `Ssnpm`, both at least `PMLEN=0` and `7`.

## 12.5 Side channels and constant-time programming

- **`Zkt` / `Zvkt`:** a list of scalar/vector instructions whose **latency is independent of operand values** (basic ALU ops, shifts, multiplies of the specified forms, bit-manip, crypto instructions). Divides and memory accesses are *not* covered. Mandatory in RVA22/RVA23 profiles.
- Software still needs constant-time algorithms (no secret-dependent branches or table indexes). `Zicond` helps write branch-free selects.
- **Speculative-execution attacks (Spectre/Meltdown classes):** RISC-V implementations vary; the ISA has no dedicated speculation barrier. Mitigations are implementation or platform-specific (predictor flush on privilege switch, hardened cores, fences as barriers). Vendors publish advisories **[verify per core]**. Proposals such as `Svukte` (make user-mode-accessible kernel-address accesses fault early) target Meltdown-like leaks **[verify status]**.
- **Cache-timing:** `Zicbom` flush instructions available in U-mode can be restricted via `*envcfg` bits.
- **Rowhammer/fault injection:** hardware/platform-level mitigations (ECC, refresh), RERI error reporting.
- **Debug and test interfaces:** disable or authenticate JTAG in production (Debug spec supports authentication).

## 12.6 Randomness and cryptography

- **`Zkr`**: CSR `seed` (0x015) returns entropy bits with status (BIST, ES16, WAIT, DEAD); intended to seed a DRBG; access gated by `mseccfg.USEED/SSEED`.
- **Scalar crypto (`Zk*`)** and **vector crypto (`Zvk*`)** (Chapters 3 and 4) provide AES, SHA-2, SM3/SM4, GCM, and carry-less multiply with timing guarantees.
- Linux uses `Zkr`/`seed` for the kernel RNG if present; libraries use hwprobe to select accelerated primitives.

## 12.7 Trusted execution environments (TEEs)

### PMP-based enclaves (M-mode monitor)

Examples: **Keystone** (Berkeley), **Penglai**, **MultiZone**, **Sanctum** (MIT, research variant), **CURE**.

- A small **security monitor** in M-mode configures PMP so enclave memory is inaccessible to the OS; handles enclave entry/exit, measures and attests code.
- Limits: PMP entry count limits the number of simultaneous enclaves; mitigated by `Smmtt` or by virtualization-based designs.

### Confidential computing: CoVE / AP-TEE **[Draft/verify]**

**CoVE** (Confidential VM Extension) builds on virtualization:

- Roles: **TSM** (TEE Security Manager) running in a trusted domain; **TVM** (TEE VM) guests; the untrusted host/hypervisor.
- ABI: SBI-based interfaces between host, TSM, and TVMs (`COVH` for host, `COVG` for guest, `COVI` for interrupts) **[verify names]**.
- Hardware building blocks: **Smmtt** (physical-memory isolation per domain), **IOMMU** (DMA isolation and secure interrupt delivery, with PCIe IDE/TDISP integration), **AIA** (interrupt isolation), `H` extension.
- Goal: VMs protected from the host hypervisor (similar goals to AMD SEV-SNP, Intel TDX, Arm CCA).
- Attestation and measurement use platform RoT and DICE-style chains.

### Other

- **Salus**: Rust-based TSM prototype.
- **Microcontroller TEEs:** PMP + `Smstateen` + separation kernels (seL4, Tock).
- **Platform Security Model (PSM)**: RISC-V International's guidance for platform security architecture **[verify]**.

## 12.8 Secure boot and roots of trust

```mermaid
flowchart LR
  ROM[Immutable ROM: RoT] --> V1[Verify FSBL signature]
  V1 --> V2[Verify OpenSBI + payload]
  V2 --> V3[Verify kernel/initrd]
  V3 --> M[Measure into TPM / DICE]
```

Elements:

- **Immutable ROM** holds public key hash/verification code; OTP fuses hold keys, lifecycle state, anti-rollback counters.
- **Chain of trust:** each stage verifies the next (signature + version) before executing it.
- **Measured boot:** hash of each stage extended into a TPM PCR (TPM 2.0 on SPI/I2C) or DICE layers.
- **Debug lock:** fuse-controlled debug enable; authenticated debug.
- **OpenTitan** (lowRISC): open-source silicon RoT built on the Ibex core (Earl Grey design), with secure boot, key manager, crypto accelerators, and lifecycle controller.
- **Caliptra** (CHIPS Alliance / OCP): open RoT block for data-center SoCs using a RISC-V core (VeeR EL2) **[verify versions]**.
- **Firmware update/recovery:** NIST SP 800-193 "PFR"-style resilience requires recovery images and authenticated updates.

### Firmware hardening checklist

| Item | Action |
|------|--------|
| PMP | Lock firmware regions; set `mseccfg.MML/MMWP`; clear `RLB` |
| Delegation | Delegate only what S needs; keep `ecall` from S for SBI |
| SBI | Validate all pointers and hart masks; reject unaligned or out-of-range addresses |
| Debug | Disable JTAG/abstract commands in production or require authentication |
| Secrets | Zeroize on boot-stage exit; use `Zkr`/hardware RNG |
| Update | Signed images; anti-rollback counters |
| Unused peripherals | Gate with PMP/IOPMP/WorldGuard |
| Stack | Use shadow stacks/canaries; compile with `-fstack-protector-strong` |
| Control-flow | Build firmware with landing pads if available |

## 12.9 Hypervisor and OS hardening on RISC-V

- Keep `SUM` clear except in sanctioned user-copy routines (Linux `__user` accessors).
- Use `Svpbmt`/PMAs correctly for device memory to avoid speculative side effects.
- Use G-stage + IOMMU to isolate guests and devices; enable `Svade`/dirty tracking carefully for live migration.
- Use `Smstateen` bits to deny guests/user mode access to optional state not context-switched.
- Defend against transient-execution leaks per vendor guidance; enable flushing on VM switches where required.

## 12.10 Chapter summary

- RISC-V provides layered isolation: privilege modes, PMP/Smepmp, paging, IOMMU; newer pieces add table-based domains (`Smmtt`) and confidential computing (CoVE).
- CFI: `Zicfilp` (landing pads, `lpad`) and `Zicfiss` (shadow stack, `sspush/sspopchk`, `ssp`) are ratified and backward-compatible via MOPs.
- Pointer masking supports software tagging; `Zkt/Zvkt` and crypto extensions support constant-time cryptography; `Zkr` provides entropy.
- Secure boot: immutable ROM, signed stages, measured boot, locked debug, hardware RoTs (OpenTitan, Caliptra).

### Check yourself

1. How does `Zicfiss` prevent attackers from overwriting the shadow stack with normal stores?
2. Why is `lpad` encoded as `auipc x0, imm`?
3. What does `mseccfg.MMWP` do?
4. Which instructions are covered by `Zkt`'s data-independent timing, and which are notably not?
5. Name the three actors in CoVE.

<details><summary>Answers</summary>

1. Shadow stack pages use the PTE encoding `R=0, W=1`, which is reserved for ordinary accesses; only shadow-stack instructions may write them.
2. It executes harmlessly as a no-op on hardware without `Zicfilp` (an `auipc` to `x0`).
3. Machine-mode whitelist policy: M-mode accesses that match no PMP entry are denied.
4. Covered: a defined list of ALU, shift, multiply, bit-manip, crypto ops. Not covered: divide and memory-access timing.
5. TSM (TEE Security Manager), TVM (confidential VM), and the untrusted host/hypervisor.
</details>

Next: [Chapter 13 - Debug, Trace, Performance, RAS](13_Debug_Trace_Perf_RAS.md)
