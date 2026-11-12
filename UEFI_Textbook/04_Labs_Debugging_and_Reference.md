# 4. UEFI Labs, Diagnosis, and Review

## 4.1 Read-only Linux inspection

On an authorized Linux system booted through UEFI:

```sh
test -d /sys/firmware/efi && printf 'UEFI environment detected\n'
efibootmgr -v
findmnt /boot/efi
```

These commands require appropriate utilities/permissions and distribution conventions. An absent `/boot/efi` mount does not prove there is no ESP: it may be mounted elsewhere or not mounted. An absent Linux EFI directory can indicate the current boot mode rather than the motherboard's entire capability.

Inspect boot entries without using write/delete options. Treat device identifiers and firmware variables as potentially sensitive platform information when sharing logs.

## 4.2 Trace one boot entry

1. Identify the active/current boot entry if reported.
2. Decode its device path and loader filename.
3. Locate the corresponding ESP through actual partition information.
4. Confirm the image architecture and expected file.
5. Explain which loader starts next and how it reaches the OS.

**Pass condition:** the path and image are connected by evidence, not just similar vendor names.

## 4.3 Application development lab

Use a documented EDK II virtual-machine platform such as the appropriate OVMF configuration for an x86 VM or ArmVirt configuration for an Arm VM. Obtain matching firmware and tools from a trusted source.

Build or use a minimal application that prints a message and returns. Understand its entry-point signature, image handle, system table, console interface, and return status before adding device access.

Keep writable variable storage separate from the code image as required by the VM platform. Make a disposable copy for each experiment. Never point a VM experiment at the host's actual firmware storage.

Expected progression:

```text
application builds -> firmware recognizes image
 -> image starts -> message appears -> application returns
```

Each step tests a different layer. A PE/COFF file existing on disk only establishes the first artifact, not execution.

## 4.4 Troubleshooting table

| Symptom | Investigate |
| --- | --- |
| Image not listed | Filesystem, boot path, architecture, boot policy |
| Security violation | Authorization/revocation state and image signature |
| Application starts then faults | Calling convention, protocol assumptions, pointer lifetime |
| ExitBootServices fails | Memory map/key, intervening changes, retry path |
| OS runtime variable access fails | OS policy, permissions, runtime mapping/service support |
| Update staged but version unchanged | Task/result, activation requirements, compatibility |

Do not make disabling Secure Boot the default answer to every loader failure. First establish whether rejection is actually the issue.

## 4.5 Review answers

- **UEFI firmware versus bootloader:** firmware provides an environment and launches an image; a bootloader is one image using that environment.
- **ESP versus variable storage:** the ESP is a disk filesystem; nonvolatile variables are firmware-managed configuration.
- **Boot Services versus Runtime Services:** the former end at successful OS takeover; the latter have defined post-boot availability and constraints.
- **PI versus UEFI:** internal initialization architecture versus external firmware/loader interfaces.

## Glossary

| Term | Meaning |
| --- | --- |
| ESP | EFI System Partition |
| Handle | Firmware-managed entity reference |
| Protocol | GUID-identified callable interface |
| PE/COFF | Executable/object format family |
| PI | Platform Initialization architecture |
| DXE | Driver Execution Environment |
| Capsule | Structured update-data container |
| EBS | Common abbreviation for ExitBootServices |

Return to [contents](00_README.md) or continue with [PCIe](../PCIe_Textbook/00_README.md).
