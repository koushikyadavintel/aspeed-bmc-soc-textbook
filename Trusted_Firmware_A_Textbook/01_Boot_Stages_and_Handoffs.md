# 1. Boot Stages and Their Contracts

## 1.1 What TF-A supplies

Trusted Firmware-A is reference secure firmware for Arm A-profile systems. It provides boot-stage infrastructure, EL3 runtime services, power-management integration, and platform hooks. It is neither an ordinary application nor the entire operating system.

The trusted label describes its intended role in the trusted computing base, not a proof that an arbitrary build is secure.

## 1.2 Common AArch64 flow

```text
reset -> BL1 -> BL2 -> BL31
                       |-> optional BL32 initialization
                       `-> BL33 -> normal OS
```

| Stage | Common role |
| --- | --- |
| BL1 | Earliest trusted TF-A stage, typically ROM-oriented |
| BL2 | Loads and optionally authenticates subsequent images |
| BL31 | Resident EL3 runtime firmware |
| BL32 | Optional secure payload, such as a trusted OS |
| BL33 | Non-secure next-stage firmware, such as U-Boot or UEFI |

These labels denote roles, not mandatory partitions. A SoC ROM may perform work otherwise associated with BL1; a platform may enter BL31 through alternative firmware. AArch32 has a different stage/runtime arrangement, so BL31 must not be described as universally present.

## 1.3 Handoff information

A jump target alone is insufficient. The next image needs its execution level, security state, entry address, arguments, permitted memory, and expected CPU/cache/MMU state.

TF-A carries image and entry-point information through defined data structures and platform conventions. Configuration blobs can describe firmware and hardware properties. The firmware-design documentation distinguishes `FW_CONFIG`, hardware configuration, and stage-specific configuration.

Incorrect handoff information can look like a broken next-stage binary: the same image can fail when loaded at the wrong address or entered at the wrong level.

## 1.4 Primary and secondary CPUs

Cold boot commonly selects a primary CPU and keeps secondary CPUs in a safe state until initialization is sufficient. Secondary CPU startup later follows platform power-control and warm-entry paths.

Not every reset runs the complete cold-boot chain. Suspend/resume, CPU hotplug, watchdog reset, and full power-on can take different paths and rely on different retained state.

A port that succeeds once on cold boot can still fail on warm reset because it assumes registers, memory, or clocks have their power-on values.

## 1.5 Who remains resident?

BL31 normally remains available after BL33 starts. Temporary loader code and data may be reusable according to platform rules; resident firmware and secure payload memory must remain protected from the normal OS and DMA.

BL32 is separate from BL31. A secure OS may provide trusted applications while BL31 provides EL3 mediation and runtime services. Combining their names obscures ownership and debugging.

## Worked diagnosis

BL2 reports that all images loaded; BL33 prints nothing.

Possible boundaries:

1. BL31 entry or initialization failed.
2. Secure-payload initialization did not return as expected.
3. BL33 entry information is wrong.
4. BL33 UART setup differs.
5. BL33 runs but faults before console initialization.

**Answer guide:** collect stage markers, image addresses/sizes, entry state, and relevant exception reports. "Loaded" proves bytes were placed somewhere, not that the next stage executed successfully.

## Exercise

Why is TF-A not simply another name for U-Boot?

**Answer:** they commonly occupy different roles and privilege/security contexts. TF-A can provide EL3 runtime services while U-Boot, as BL33, prepares and loads the normal-world OS.

Next: [Images and chain of trust](02_Images_and_Chain_of_Trust.md).
