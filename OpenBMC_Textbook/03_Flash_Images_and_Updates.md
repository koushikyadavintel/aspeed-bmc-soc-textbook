# 3. Flash Images, Persistence, Updates, and Analysis

## 3.1 Storage is not the same as a container

SPI-NOR, raw NAND, and eMMC have different access and failure models. NOR commonly has erase-before-write constraints; raw NAND needs ECC and bad-block handling; eMMC presents managed block storage but still has device-specific reliability and power-loss behavior.

Linux MTD describes raw flash devices. UBI manages volumes over suitable MTD storage; UBIFS is a filesystem built for UBI. SquashFS is a compressed read-only filesystem. An overlay can combine a read-only base with writable state. ext4 is a block-device filesystem. These are not interchangeable names for "the rootfs."

## 3.2 Four artifacts that people call an image

| Artifact | Meaning | Not safe to assume |
| --- | --- | --- |
| Raw flash dump | Bytes from a specified storage region | That it can be uploaded to an update API |
| Filesystem image | Contents in a specific filesystem format | That it includes a bootloader or partition table |
| Boot container | Structured components such as kernel/DTB/signatures | That it is the full storage layout |
| Update payload | Package/capsule accepted by an updater | That it belongs at offset zero |

The final deployment can use WIC partitions, UBI volumes, fixed flash partitions, a FIT, separate artifacts, or a platform-specific envelope. A universal address map cannot be inferred from "OpenBMC."

Persistent state may include network settings, certificates, logs, accounts, or calibration. Some inventory resides on separate FRU devices, not necessarily the firmware flash. Backup material can contain secrets and must remain private.

## 3.3 A/B is a policy, not magic

A robust update sequence might be:

```text
authenticate request -> validate package/platform/version
 -> stage inactive slot -> verify written contents
 -> select trial boot -> reboot
 -> validate health -> commit success
```

If trial boot fails, a defined recovery component selects a known-good image. Record what counts as health, how many retries occur, and what happens when both slots fail.

Not every platform has A/B; some redundancy schemes do not duplicate the bootloader. A/B alone does not provide rollback prevention, signature verification, or protection against power loss while updating shared metadata.

Distinguish transfer, validation, installation, boot selection, activation, and post-boot success. An HTTP upload success is not proof of activation.

## 3.4 Clarifying "POST"

HTTP `POST` is a request method an upload API may use. Power-on self-test is a startup diagnostic phase also abbreviated POST. A sentence about a "POST method" does not tell you which interface or target partition to use.

Discover the Redfish UpdateService and its supported mechanisms, or follow the exact platform update procedure. A filename ending in `.cap.bin` does not prove a standard UEFI capsule or a raw flash layout.

This textbook intentionally omits blind write commands. Obtain the expected format, signature policy, target identity, recovery instructions, and authorization first.

## 3.5 Read-only image investigation

On a Linux workstation, operate on an authorized copy, preferably isolated from production:

```sh
sha256sum firmware.bin
file firmware.bin
od -Ax -tx1 -N 128 firmware.bin
```

When a component's format has been established, specialized tools may inspect it:

```sh
dumpimage -l kernel.itb
readelf -h service.elf
readelf -d service.elf
```

Tools need to be installed and current; image parsers process untrusted input. Hashes identify the copy under analysis but do not prove authenticity without a trusted expected value.

Strings, imports, service units, D-Bus interface names, and filesystem paths provide hypotheses. A stripped ELF often retains dynamic symbols and strings but may omit local function names and debug information.

If a function references a temperature-error string and a hwmon path, "sensor-related userspace handling" is a reasonable hypothesis, not a certainty. Confirm reachable cross-references, callers, imports, process role, and runtime behavior on authorized systems. Shared logging helpers, dead code, and inlined code can mislead.

A heuristic confidence score is not a calibrated probability. Record the evidence and alternatives instead of presenting an arbitrary percentage as measured truth.

## Exercise

You receive a capsule and a flash dump with the same size. Can one replace the other?

**Answer:** no. Equal lengths do not establish format, offsets, authentication metadata, partition coverage, or compatibility. Verify each artifact's contract independently.

Next: [Bring-up workbook](04_Bringup_Workbook_and_Reference.md).
