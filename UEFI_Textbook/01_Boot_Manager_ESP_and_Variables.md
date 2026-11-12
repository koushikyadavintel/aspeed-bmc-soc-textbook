# 1. Firmware, the Boot Manager, and the ESP

## 1.1 UEFI is an interface standard

Platform firmware initializes hardware and provides a pre-OS execution environment. UEFI standardizes interfaces used by firmware drivers, applications, loaders, and the eventual OS. An implementation is not the same thing as the specification.

Calling every setup screen "the BIOS" hides a distinction: legacy PC BIOS interfaces and UEFI interfaces are different. A graphical menu is not what makes firmware UEFI.

## 1.2 The boot path

```text
platform initialization -> firmware boot manager
 -> selected EFI image -> OS loader -> OS kernel
```

The selected image can be a loader, shell, diagnostic application, or another supported boot application. It is not necessarily the kernel.

UEFI applications and drivers use architecture-appropriate PE/COFF images. An `.efi` suffix does not prove that an arbitrary file is valid or trusted for the current CPU.

## 1.3 EFI System Partition

A disk-based boot commonly uses an EFI System Partition with a FAT filesystem. The ESP contains files such as a vendor's loader under an `EFI` directory. GPT is common, but "UEFI requires GPT in every possible situation" is too broad.

The ESP is storage. Firmware boot entries are configuration. A boot entry can reference an image through a device path. Recreating a file does not necessarily recreate its boot entry, and recreating a boot entry does not repair a missing file.

Fallback boot filenames are architecture-specific: for example, x86-64 commonly uses `EFI/BOOT/BOOTX64.EFI`, while AArch64 commonly uses `EFI/BOOT/BOOTAA64.EFI`. Use the applicable boot behavior and architecture; do not copy one filename onto every platform.

## 1.4 Variables and device paths

UEFI variables are identified by a name and vendor GUID, with attributes defining persistence and access conditions. They are not merely text environment variables.

Boot configuration commonly includes `BootOrder`, individual `Boot####` entries, and a one-shot `BootNext`. Platform policy determines how they are used and whether writes are permitted.

A device path describes a route or identity through firmware's device model. It can include hardware, messaging, media, and file-path components. A human-readable disk label alone does not capture the full path.

Nonvolatile variable storage is finite and security-sensitive. Do not bulk-delete variables to "clean up" a boot issue; they can contain keys and configuration essential for recovery.

## 1.5 Distinguish failure layers

| Symptom | Candidate area |
| --- | --- |
| Disk not discovered | Controller/driver/device initialization |
| Boot option missing | Variable/configuration/device-path policy |
| EFI image absent | ESP/filesystem/deployment |
| Image rejected | Architecture, format, signature, revocation |
| Loader runs, kernel fails | OS loader/kernel arguments, files, drivers |

A loader error after firmware has already started the loader should not automatically be called a firmware enumeration failure.

## Exercise

The setup menu lists an OS, but selecting it returns immediately. Is the boot entry enough evidence that the loader exists?

**Answer:** no. The entry can be stale or refer to an invalid path, missing image, incompatible architecture, or rejected signature. Inspect the path and file before changing unrelated firmware settings.

Next: [Protocols, services, and handoff](02_Protocols_Services_and_OS_Handoff.md).
