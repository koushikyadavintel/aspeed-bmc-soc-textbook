# Chapter 10 - Boot, SBI, Firmware, Device Discovery, and Linux

[Index](00_README.md) | Prev: [Ch 9](09_ABI_Toolchain_Assembly.md) | Next: [Ch 11 - Microarchitecture](11_Microarchitecture_Implementations.md)

**Goals:** Follow a RISC-V system from reset to a running OS, learn the Supervisor Binary Interface (SBI) in detail, know how software discovers hardware (device tree, ACPI, CSRs, `hwprobe`), and understand how Linux boots on RISC-V.

> Verified: **SBI v3.0 is Ratified** (released 2025-07-16, riscv-sbi-doc releases). Extension lists for 2.0/3.0 below are from the SBI changelog and memory; confirm exact function IDs in the spec **[verify]**.

---

## 10.1 The boot chain

```mermaid
flowchart LR
  R[Reset vector, M-mode] --> ZSBL[ROM / ZSBL]
  ZSBL --> FSBL[FSBL / SPL: DRAM init, clocks]
  FSBL --> SBI[OpenSBI runtime, M-mode]
  SBI --> BL[U-Boot proper or EDK2, S/HS-mode]
  BL --> K[Linux kernel]
  K --> U[init / user space]
```

| Stage | Typical software | Mode | Job |
|-------|-----------------|------|-----|
| Reset | Mask ROM (ZSBL: zero-stage boot loader) | M | Basic init, find next stage on SPI/SD/eMMC/UART; may do secure boot verification |
| First-stage | FSBL / U-Boot SPL / vendor loader | M (or S) | Initialize DRAM, clocks, PMIC, load firmware and next stage |
| Runtime firmware | **OpenSBI**, RustSBI, vendor SBI | M | Stays resident; provides SBI services; sets up PMP; delegates traps; boots S-mode payload |
| Second-stage | U-Boot proper, EDK2 (UEFI), coreboot payload, GRUB | S/HS | Device init, network/storage boot, load kernel + DTB |
| OS | Linux, FreeBSD, Zephyr, etc. | S/HS | Runs the system |

This ROM -> SPL -> runtime firmware -> bootloader -> kernel pattern mirrors other architectures (for example, a BMC boot chain: ROM, U-Boot, kernel).

### What each stage hands off

At the entry of the **S-mode payload** (bootloader or kernel) the boot contract is:

| Item | Value |
|------|-------|
| Privilege | S-mode (HS if `H` present) |
| `a0` | **hartid** of the current hart |
| `a1` | **Physical address of the device tree blob** (DTB), 8-byte aligned |
| `satp` | 0 (MMU off, `Bare`) |
| `sstatus.SIE` | 0 (interrupts disabled) |
| Other harts | Held by firmware (stopped or spinning); started later via the SBI HSM extension |
| Memory/PMP | Firmware reserved regions are protected by PMP |

M-mode firmware entry (what OpenSBI itself receives): `a0 = hartid`, `a1 = DTB` (or firmware-specific), and for `fw_dynamic`, `a2 =` pointer to a `struct fw_dynamic_info` that says where the next stage is and what mode to enter.

## 10.2 OpenSBI firmware types

| Type | Behavior |
|------|----------|
| `fw_jump` | Jumps to a **fixed address** for the next stage (configured at build time) |
| `fw_dynamic` | Reads next-stage address/mode/options from `fw_dynamic_info` passed by the previous stage (most flexible; recommended) |
| `fw_payload` | The next stage (e.g., U-Boot or kernel) is **embedded** into the firmware binary |

`fw_dynamic_info` (a2) fields: `magic` (0x4942534f, "OSBI"), `version`, `next_addr`, `next_mode` (1 = S, 0 = U), `options`, `boot_hart`.

OpenSBI platform code: `platform/generic` (device-tree driven, supports most boards) and platform-specific ports. It also implements **domains** (isolated sets of harts/memory with PMP), **PMU** support, **HSM**, and **SSE**.

### Single-hart "boot hart" selection

At reset, multiple harts start. Firmware chooses one (via a **lottery** using an atomic variable, or a fixed boot hart). Others wait (wfi or spin) until the boot hart finishes init, then enter **HSM stopped** state and wait for `sbi_hart_start`.

## 10.3 The Supervisor Binary Interface (SBI)

The SBI is the **standard interface between S-mode software and M-mode firmware** (and between VS-mode and the hypervisor). It lets one OS binary run on any compliant platform.

### Calling convention

```
Inputs : a7 = Extension ID (EID), a6 = Function ID (FID), a0..a5 = arguments
Action : ecall
Outputs: a0 = error code, a1 = return value
```

All other registers are preserved by the callee.

### Error codes

| Value | Name | Meaning |
|-------|------|---------|
| 0 | `SBI_SUCCESS` | OK |
| -1 | `SBI_ERR_FAILED` | Generic failure |
| -2 | `SBI_ERR_NOT_SUPPORTED` | Function/extension not implemented |
| -3 | `SBI_ERR_INVALID_PARAM` | Bad argument |
| -4 | `SBI_ERR_DENIED` | Not allowed |
| -5 | `SBI_ERR_INVALID_ADDRESS` | Address invalid or inaccessible |
| -6 | `SBI_ERR_ALREADY_AVAILABLE` | Already available |
| -7 | `SBI_ERR_ALREADY_STARTED` | Hart already started |
| -8 | `SBI_ERR_ALREADY_STOPPED` | Hart already stopped |
| -9 | `SBI_ERR_NO_SHMEM` | Shared memory not available |
| -10 | `SBI_ERR_INVALID_STATE` | Invalid state (2.0/3.0) **[verify]** |
| -11 | `SBI_ERR_BAD_RANGE` | Bad range **[verify]** |
| -12 | `SBI_ERR_TIMEOUT` | Timeout **[verify]** |
| -13 | `SBI_ERR_IO` | I/O error **[verify]** |

### Extension ID space

| Range | Use |
|-------|-----|
| `0x00` - `0x0F` | **Legacy** extensions (deprecated: console putchar/getchar, set_timer, IPI, remote fences, shutdown) |
| `0x10` | **Base** extension |
| `0x08000000` - `0x08FFFFFF` | Experimental |
| `0x09000000` - `0x09FFFFFF` | Vendor-specific |
| `0x0A000000` - `0x0AFFFFFF` | Firmware-specific |
| ASCII-name EIDs | Standard extensions (EID = ASCII bytes of the name) |

### Standard extensions

| Extension | EID (hex) | ASCII | Purpose |
|-----------|-----------|-------|---------|
| Base | `0x10` | - | Version, implementation ID, probe extension, `mvendorid/marchid/mimpid` |
| TIME | `0x54494D45` | "TIME" | `sbi_set_timer(stime_value)` |
| IPI | `0x735049` | "sPI" | `sbi_send_ipi(hart_mask, hart_mask_base)` |
| RFENCE | `0x52464E43` | "RFNC" | Remote `fence.i`, `sfence.vma`, `hfence.*` |
| HSM | `0x48534D` | "HSM" | Hart state management |
| SRST | `0x53525354` | "SRST" | System reset (shutdown/reboot) |
| PMU | `0x504D55` | "PMU" | Performance monitoring unit counters and events |
| DBCN | `0x4442434E` | "DBCN" | Debug console (write/read/write_byte) |
| SUSP | `0x53555350` | "SUSP" | System suspend |
| CPPC | `0x43505043` | "CPPC" | Collaborative processor performance control |
| NACL | `0x4E41434C` | "NACL" | Nested acceleration (hypervisors) |
| STA | `0x535441` | "STA" | Steal-time accounting |
| SSE | `0x535345` | "SSE" | Supervisor software events (v3.0) |
| FWFT | `0x46574654` | "FWFT" | Firmware features (v3.0): delegation/enables such as misaligned-exception delegation, landing pad/shadow stack control, hardware A/D updating |
| DBTR | `0x44425452` | "DBTR" | Debug triggers (v3.0) |
| MPXY | `0x4D505859` | "MPXY" | Message proxy (v3.0) |

(Extensions DBCN/SUSP/CPPC/NACL/STA arrived in 2.0; SSE/FWFT/DBTR/MPXY and further PMU improvements in 3.0 **[verify]**.)

### Base extension functions (EID `0x10`)

| FID | Function |
|-----|----------|
| 0 | `sbi_get_spec_version` |
| 1 | `sbi_get_impl_id` |
| 2 | `sbi_get_impl_version` |
| 3 | `sbi_probe_extension(eid)` -> nonzero if available |
| 4 | `sbi_get_mvendorid` |
| 5 | `sbi_get_marchid` |
| 6 | `sbi_get_mimpid` |

Implementation IDs: 0 BBL, 1 OpenSBI, 2 Xvisor, 3 KVM, 4 RustSBI, 5 Diosix, 6 Coffer, 7 Xen, 8 PolarFire HSS, 9 coreboot, 10 oreboot, 11 bhyve.

### Key functions

| Extension | Function (FID) | Notes |
|-----------|----------------|-------|
| TIME | `set_timer` (0) | Program next timer event; clears `STIP` |
| IPI | `send_ipi` (0) | Sets `SSIP` on harts selected by `hart_mask` (a0) and `hart_mask_base` (a1); `base = -1` selects all |
| RFENCE | `remote_fence_i` (0), `remote_sfence_vma` (1), `remote_sfence_vma_asid` (2), `remote_hfence_gvma_vmid` (3), `remote_hfence_gvma` (4), `remote_hfence_vvma_asid` (5), `remote_hfence_vvma` (6) | TLB/i-cache shootdowns |
| HSM | `hart_start` (0), `hart_stop` (1), `hart_get_status` (2), `hart_suspend` (3) | `hart_start(hartid, start_addr, opaque)`: target starts in S-mode at `start_addr` with `a0=hartid`, `a1=opaque`, `satp=0`, interrupts disabled |
| SRST | `system_reset` (0) | type: 0 shutdown, 1 cold reboot, 2 warm reboot; reason: 0 none, 1 system failure |
| DBCN | `console_write` (0), `console_read` (1), `console_write_byte` (2) | Early console without drivers |

HSM states: 0 `STARTED`, 1 `STOPPED`, 2 `START_PENDING`, 3 `STOP_PENDING`, 4 `SUSPENDED`, 5 `SUSPEND_PENDING`, 6 `RESUME_PENDING`.

### SBI examples

```asm
# Print one character using Debug Console (DBCN), console_write_byte
sbi_putc:                      # a0 = character
    li   a7, 0x4442434E        # EID "DBCN"
    li   a6, 2                 # FID: console_write_byte
    ecall                      # a0 = error, a1 = value
    ret

# Set a timer event for absolute time in a0
sbi_set_timer:
    li   a7, 0x54494D45        # "TIME"
    li   a6, 0
    ecall
    ret

# Shutdown the system
sbi_shutdown:
    li   a7, 0x53525354        # "SRST"
    li   a6, 0
    li   a0, 0                 # type: shutdown
    li   a1, 0                 # reason: none
    ecall
1:  wfi
    j    1b
```

```c
struct sbiret { long error; long value; };
static inline struct sbiret sbi_ecall(long eid, long fid, long a0, long a1, long a2) {
    register long r0 asm("a0") = a0, r1 asm("a1") = a1, r2 asm("a2") = a2;
    register long r6 asm("a6") = fid, r7 asm("a7") = eid;
    asm volatile ("ecall" : "+r"(r0), "+r"(r1) : "r"(r2), "r"(r6), "r"(r7) : "memory");
    return (struct sbiret){ r0, r1 };
}
```

### How the SBI works under the hood

`ecall` in S-mode traps to M-mode (code 9, "ecall from S"). OpenSBI's M-mode trap handler decodes `a7/a6`, runs the service, writes `a0/a1`, advances `mepc` by 4, and `mret`s. For VS-mode, the **hypervisor** (HS-mode, e.g., KVM) receives the `ecall` (code 10) and implements the SBI for the guest.

### Misaligned accesses and SBI

If the hardware traps on misaligned loads/stores, M-mode firmware often **emulates** them, or delegates the trap to S-mode (`FWFT` MISALIGNED_EXC_DELEG) so the OS emulates. Profile-conforming RVA23 hardware must support misaligned loads/stores (`Zicclsm`), possibly slowly.

## 10.4 Hardware discovery

RISC-V has **no CPUID instruction**. Software learns about the hardware from several sources, layered:

| Layer | What it provides |
|-------|------------------|
| CSRs | `mvendorid`, `marchid`, `mimpid`, `mhartid`, `misa` (M-mode only); S-mode gets them via SBI Base calls |
| **Device tree** (DTB) | CPU ISA strings, topology, memory map, interrupt controllers, timers, devices |
| **ACPI** tables | RHCT (hart capabilities), MADT (interrupt controllers), plus normal ACPI device descriptions; used with UEFI on server-class platforms |
| **SBI probe** | `sbi_probe_extension` |
| **OS interfaces** | Linux `riscv_hwprobe` syscall, `/proc/cpuinfo`, `AT_HWCAP` |
| Trial and error | Try an instruction, catch illegal-instruction; used by some libraries as a fallback |
| `mconfigptr` | Pointer to a standard configuration structure (rarely used so far) |

### Device tree for RISC-V (essentials)

```dts
/dts-v1/;
/ {
    #address-cells = <2>;
    #size-cells = <2>;
    compatible = "riscv-virtio";
    cpus {
        #address-cells = <1>;
        #size-cells = <0>;
        timebase-frequency = <10000000>;
        cpu0: cpu@0 {
            device_type = "cpu";
            reg = <0>;
            compatible = "riscv";
            riscv,isa-base = "rv64i";
            riscv,isa-extensions = "i", "m", "a", "f", "d", "c", "v",
                                    "zicsr", "zifencei", "zba", "zbb", "sstc", "svpbmt";
            riscv,cbom-block-size = <64>;
            mmu-type = "riscv,sv48";
            cpu0_intc: interrupt-controller {
                #interrupt-cells = <1>;
                compatible = "riscv,cpu-intc";
                interrupt-controller;
            };
        };
    };
    memory@80000000 { device_type = "memory"; reg = <0x0 0x80000000 0x0 0x8000000>; };
    soc {
        compatible = "simple-bus";
        #address-cells = <2>; #size-cells = <2>; ranges;
        plic: interrupt-controller@c000000 {
            compatible = "sifive,plic-1.0.0", "riscv,plic0";
            reg = <0x0 0xc000000 0x0 0x600000>;
            interrupt-controller; #interrupt-cells = <1>;
            interrupts-extended = <&cpu0_intc 11>, <&cpu0_intc 9>;
            riscv,ndev = <96>;
        };
        uart@10000000 { compatible = "ns16550a"; reg = <0x0 0x10000000 0x0 0x100>; interrupts = <10>; interrupt-parent = <&plic>; clock-frequency = <3686400>; };
    };
    chosen { bootargs = "console=ttyS0 earlycon"; stdout-path = "/soc/uart@10000000"; };
};
```

Key properties:

| Property | Meaning |
|----------|---------|
| `riscv,isa` | Legacy ISA string (e.g., `rv64imafdc`) |
| `riscv,isa-base` | `rv32i` / `rv64i` (newer) |
| `riscv,isa-extensions` | List of extension names (string list) |
| `mmu-type` | `riscv,sv39`, `riscv,sv48`, `riscv,sv57`, `riscv,none` |
| `timebase-frequency` | `time` CSR tick rate (Hz) |
| `riscv,cbom-block-size`, `riscv,cboz-block-size`, `riscv,cbop-block-size` | Cache-block sizes |
| `interrupts-extended` | List of (hart interrupt controller phandle, cause) pairs |
| `riscv,ndev` | Number of PLIC sources |

Compile/inspect: `dtc -I dts -O dtb in.dts -o out.dtb`, `dtc -I dtb -O dts out.dtb`. Dump QEMU's tree: `qemu-system-riscv64 -machine virt,dumpdtb=virt.dtb`.

### ACPI on RISC-V (server-class)

- Uses **UEFI** for boot services and ACPI for hardware description.
- **RHCT** (RISC-V Hart Capabilities Table): ISA string, MMU type, cache/ hart info. **MADT** has RISC-V-specific structures: `RINTC` (per-hart interrupt controller), `IMSIC`, `APLIC`, `PLIC`. Support appears in ACPI 6.5+ and Linux **[verify versions]**.

### Linux `riscv_hwprobe`

Syscall `riscv_hwprobe` (number 258) takes key/value pairs and a CPU set, returning keys such as `MVENDORID`, `MARCHID`, `MIMPID`, `BASE_BEHAVIOR`, `IMA_EXT_0` (bitmask of extensions: `V`, `Zba`, `Zbb`, `Zbs`, `Zicboz`, `Zfh`, `Zvfh`, ...), `CPUPERF_0` (e.g., misaligned-access speed), `ZICBOZ_BLOCK_SIZE`. It is exposed through the **vDSO** for speed. User-space libraries (glibc, runtime dispatch in codecs/crypto) use it to select code paths.

```c
#include <asm/hwprobe.h>
#include <sys/syscall.h>
struct riscv_hwprobe pair = { .key = RISCV_HWPROBE_KEY_IMA_EXT_0 };
syscall(__NR_riscv_hwprobe, &pair, 1, 0, NULL, 0);
if (pair.value & RISCV_HWPROBE_IMA_V) { /* vector available */ }
```

## 10.5 UEFI and standard boot

- RISC-V UEFI images are PE/COFF with machine type **`0x5064`** (RISC-V 64) or `0x5032` (RISC-V 32).
- `RISCV_EFI_BOOT_PROTOCOL` lets the OS loader fetch the **boot hartid** (needed since `a0` is not preserved across EFI calls).
- Linux has an **EFI stub** so the kernel `Image` can be booted directly by UEFI firmware (EDK2, U-Boot EFI) or via GRUB/systemd-boot.
- Server-class platforms follow the RISC-V **Server SoC** and **BRS** (Boot and Runtime Services) specifications, aiming at SBSA/SBBR-like standard behavior **[verify names/versions]**.

## 10.6 Linux on RISC-V

### Kernel image

The kernel `Image` has a 64-byte header, so any loader can find the entry point and size:

| Field | Meaning |
|-------|---------|
| `code0`, `code1` | Executable code (starts with `MZ` jump when EFI stub is enabled) |
| `text_offset` | Image load offset from 2 MiB-aligned base (RV64) |
| `image_size` | Effective size |
| `flags` | Bit 0: endianness (0 little) |
| `version` | Header version |
| `magic` | `"RISCV\0\0\0"` |
| `magic2` | `"RSC\x05"` |

Typical load address: DRAM base + `0x20_0000` (RV64) or `0x40_0000` (RV32), i.e., `0x8020_0000` on QEMU `virt` with OpenSBI occupying the first 2 MiB.

### Early kernel boot (high level)

1. `_start`: save `a0` (hartid) and `a1` (DTB), disable interrupts, set `gp`/`tp`.
2. Early page tables: build a minimal Sv39/Sv48/Sv57 mapping; the kernel probes the largest supported `satp` mode.
3. Enable the MMU; jump to the kernel's virtual address.
4. `start_kernel()`: parse the DTB (`/chosen`, `/memory`, `/cpus`), set up memory, SBI calls for console/timers, IRQ controller drivers (PLIC/AIA), per-CPU data.
5. Secondary harts started with SBI HSM `hart_start`, entering at a known address with `a0 = hartid`.
6. Mount rootfs, run `/sbin/init`.

### Kernel configuration highlights

| Config | Purpose |
|--------|---------|
| `CONFIG_RISCV` | Architecture |
| `CONFIG_64BIT` | RV64 vs RV32 |
| `CONFIG_RISCV_ISA_C`, `_ZBB`, `_ZICBOM`, `_V` ... | Optional ISA features, enabled by runtime patching (alternatives) |
| `CONFIG_RISCV_SBI` | SBI support |
| `CONFIG_SMP`, `CONFIG_NUMA` | Multicore, NUMA |
| `CONFIG_KVM` | Hypervisor support (needs `H`) |
| `CONFIG_RISCV_IMSIC`, `CONFIG_RISCV_APLIC` | AIA interrupt controllers |
| `CONFIG_EFI` | UEFI support |
| `CONFIG_MMU` | Virtual memory (NOMMU is also supported on small systems) |
| `CONFIG_FPU`, `CONFIG_RISCV_ISA_V` | FP and vector state handling |
| `CONFIG_RISCV_ISA_SVNAPOT`, `_SVPBMT`, `_ZICBOZ` | MMU and memory extensions |

### Runtime patching ("alternatives")

Linux uses **alternatives** to patch instruction sequences at boot based on detected extensions (e.g., use `cbo.zero` for `clear_page`, `Zbb` string routines, errata workarounds for specific CPUs).

### Booting under QEMU

```
# Boot Linux directly (OpenSBI is the default firmware)
qemu-system-riscv64 -machine virt -cpu rv64 -smp 4 -m 2G -nographic \
  -kernel Image -append "root=/dev/vda rw console=ttyS0" \
  -drive file=rootfs.ext4,format=raw,id=hd0 -device virtio-blk-device,drive=hd0 \
  -netdev user,id=n0 -device virtio-net-device,netdev=n0

# Enable the hypervisor and vector extensions on the CPU
-cpu rv64,h=true,v=true,vlen=256,zba=true,zbb=true
```

Options like `-cpu rv64,...` and CPU model names vary with QEMU version **[verify]**; recent QEMU also provides `-cpu max`, and `-machine virt,aia=aplic-imsic`.

### Distros and software support (as of knowledge cut, **[verify]**)

- **Debian:** riscv64 is an official architecture (since Debian 13 "trixie").
- **Fedora, openSUSE, Ubuntu (riscv64 server images), Arch/Alpine/Gentoo ports.**
- **Languages/runtimes:** GCC, LLVM/Clang, Rust, Go, OpenJDK, .NET (in progress), Node.js, Python.
- **Others:** FreeBSD, NetBSD, OpenBSD, Zephyr, FreeRTOS, RT-Thread, seL4.

## 10.7 Other firmware and loaders

| Project | Role |
|---------|------|
| **U-Boot** | SPL + proper bootloader, with RISC-V SBI and EFI support |
| **EDK2 (TianoCore)** | UEFI firmware for RISC-V (QEMU virt, platform ports) |
| **coreboot** | RISC-V payloads and platform ports |
| **RustSBI / OpenSBI** | SBI implementations |
| **Zephyr/Linux/Xen/KVM/Xvisor** | OS/hypervisor consumers |
| **Salus** | Experimental Rust hypervisor/TSM for confidential computing **[verify]** |
| **Tock / Hubris / seL4 / Redox** | Alternative OS kernels |

## 10.8 Bare-metal on real boards: practical hints

- Know your **reset vector**, boot ROM behaviors (boot-mode pins), and memory map; read the SoC's TRM.
- Many vendor SoCs use **custom ISA extensions or older CSR semantics** (for example, vendor-specific cache management instead of `Zicbom`; pre-1.0 vector). Check the vendor docs.
- `time` CSR may trap; the firmware may emulate it.
- PMP may be pre-configured by the boot ROM; check `pmpcfg*`.
- On first bring-up use **UART early console** (SBI DBCN or a direct 16550/vendor UART) and `earlycon` in Linux.
- Use **JTAG + OpenOCD + GDB** (Chapter 13) when UART output is unavailable.

## 10.9 Chapter summary

- Boot chain: ROM -> SPL -> OpenSBI (M) -> bootloader (S) -> Linux; handoff is `a0 = hartid`, `a1 = DTB`, MMU off.
- The **SBI** is the OS-to-firmware API: `ecall` with `a7 = EID`, `a6 = FID`; results in `a0` (error) and `a1` (value). v3.0 is ratified.
- Hardware is discovered through device tree / ACPI / SBI / `hwprobe`, not a CPUID instruction.
- Linux uses runtime patching to exploit extensions; EFI stub and ACPI support exist for server-style platforms.

### Check yourself

1. What are `a0` and `a1` when the kernel starts?
2. Which SBI extension starts secondary harts? What state do they start in?
3. How can user-space discover that the vector extension is present on Linux?
4. What is the difference between `fw_jump` and `fw_dynamic`?
5. Why can a guest's `ecall` not be handled by M-mode firmware directly?

<details><summary>Answers</summary>

1. `a0` = hartid, `a1` = physical address of the DTB.
2. HSM (`sbi_hart_start`); the hart starts in S-mode at the given address, `a0 = hartid`, `a1 = opaque`, `satp = 0`, interrupts off.
3. `riscv_hwprobe` (`IMA_EXT_0` bit for `V`), `/proc/cpuinfo`, or `AT_HWCAP` for single-letter extensions.
4. `fw_jump` uses a fixed compile-time next address; `fw_dynamic` reads it from a structure passed by the previous stage.
5. An `ecall` from VS-mode goes to the hypervisor (HS, cause 10), which implements the SBI for the guest.
</details>

Next: [Chapter 11 - Microarchitecture and Implementations](11_Microarchitecture_Implementations.md)
