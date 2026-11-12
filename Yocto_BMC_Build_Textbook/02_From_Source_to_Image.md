# 2. From Source Code to a Bootable Image

## 2.1 Separate the transformations

```text
C/C++ source -> object files -> executable/shared library
 -> binary package -> installed rootfs tree -> filesystem image
 + kernel + DTB + boot firmware + metadata -> deployment artifact(s)
```

This is a teaching model, not a universal file concatenation order. Some platforms deploy independent artifacts; some build a disk image, flash layout, or signed update package.

## 2.2 What common tasks do

| Task | What it establishes | Typical failure |
| --- | --- | --- |
| `do_fetch` | Required source is available | URI, revision, authentication, mirror |
| `do_unpack` | Source is extracted into a work area | Archive or source-layout issue |
| `do_patch` | Recipe patches apply | Wrong baseline, changed context |
| `do_configure` | Build system configured for target | Missing sysroot dependency, wrong option |
| `do_compile` | Target/native artifacts produced | Compiler, generated source, link error |
| `do_install` | Files staged in recipe destination | Wrong installation path or missing unit |
| `do_package` | Staged files split into packages | Unassigned file or packaging policy |
| `do_rootfs` | Selected packages installed into root tree | Dependency conflict, missing package |
| Image tasks | Filesystem/container outputs generated | Size, layout, tool, signing configuration |
| Deploy tasks | Relevant outputs published to deploy area | Naming/layout/provider mismatch |

Not every task belongs to every recipe, and exact task names are class/release-dependent.

## 2.3 Cross-compilation and sysroots

The build host might be x86-64 Linux; the BMC target may be 32-bit Arm or AArch64. The cross-compiler emits target instructions while running on the host. Headers and libraries must come from the target sysroot, not arbitrary workstation installations.

A host `pkg-config` accidentally locating host libraries can cause compile, link, or runtime failures. A correctly built target executable normally cannot run directly on the host without an appropriate emulator and runtime environment.

The toolchain also embodies ABI choices: instruction set, floating-point convention, libc, linker behavior, and processor tuning. "Both are Arm" does not prove binary compatibility.

## 2.4 Packages and the root filesystem

An executable is only part of a deployable service. It may need shared libraries, a service unit, configuration, policy files, users/groups, and data. Package dependencies and image selection must carry those requirements.

During rootfs creation, the package manager resolves selected packages and dependencies. Post-install processing, accounts, alternatives, and image policy influence the result. Filesystem creation then serializes that tree into a format such as SquashFS or ext4.

Installing a package into a rootfs is distinct from declaring a service enabled. A service can be installed but not wanted by the intended target.

## 2.5 Kernel, DTB, and deployment packaging

Kernel configuration chooses subsystems and built-in/module drivers. Device-tree selection describes the specific board. Bootloader packaging and SoC image tools can add headers, alignment, firmware components, and authentication material.

WIC uses a layout description to create a partitioned image. UBI-oriented outputs instead need volume and erase-block assumptions. A FIT groups boot components under a defined configuration. Each has distinct consumers.

A deployment directory containing ten files does not tell you which one your update interface accepts. Use the machine configuration, image classes, manifests, and platform procedure.

## 2.6 Shared state and incremental behavior

BitBake computes task signatures from relevant inputs and dependencies. Shared-state reuse can restore reusable outputs; unchanged tasks may not rerun. This is why a second build is not equivalent to the first build's work.

Blindly deleting all caches is a poor diagnosis. First establish whether the changed source or metadata participates, whether a task signature changed, and whether the expected package reached the image.

## Exercise

You modify a daemon, rebuild the daemon target, and flash yesterday's image. Should the behavior change?

**Answer:** not necessarily. Rebuild the image target, verify the selected package/revision in that image, check its digest, and verify the running image identity after deployment.

Next: [Public BSP walkthrough](03_Public_BSP_Walkthrough.md).
