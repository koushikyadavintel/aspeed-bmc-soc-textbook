# 2. Protocols, Services, and the OS Handoff

## 2.1 Handles and protocols

A handle identifies an entity in the firmware's object model. Protocols attached to it expose capabilities through GUID-identified interfaces. A storage-related handle might expose block or filesystem services; a loaded image has its own information and relationship to its source.

A protocol is not an Internet network protocol merely because it is called a protocol. It can be a table of callable interfaces shared within the firmware environment.

An application receives an image handle and a system-table pointer. The system table leads to console services, Boot Services, Runtime Services, and configuration tables.

## 2.2 Boot Services

Before OS takeover, Boot Services can allocate memory, discover/open protocols, create events, load/start images, and manage other firmware resources.

The caller must follow the relevant ownership and lifetime rules. Opening a protocol is not equivalent to copying an object; its provider can have relationships and restrictions. Firmware allocations have memory types that affect the later OS memory map.

Console output is useful during development but is not generally available through ordinary Boot Services after a successful exit.

## 2.3 ExitBootServices is a boundary

A loader obtains the memory map and a map key, then calls `ExitBootServices()` with the current key. Allocations or other intervening changes can invalidate the map.

```text
size/allocate map buffer -> obtain current map and key
 -> avoid inappropriate map-changing operations
 -> ExitBootServices(image, key)
 -> on defined retry conditions, reacquire map correctly
 -> OS owns Boot-Services resources
```

The exact failure/retry behavior and permissible operations must follow the specification and loader implementation. A print or allocation inserted for debugging can change the map, so handoff code must be designed carefully.

The OS does not simply "free all firmware memory." Runtime-designated regions and platform tables have their own lifetimes and mapping requirements.

## 2.4 Runtime Services

Runtime Services can include variable access, time services, reset, and applicable capsule/update interfaces. Their usability depends on platform implementation, OS support, runtime mappings, calling context, and the service's rules.

After `ExitBootServices()` succeeds, ordinary Boot Services and boot-only protocols are unavailable. Some firmware code remains resident, but the OS controls normal scheduling and hardware management.

When virtual addressing is established for firmware runtime use, pointer conversion and virtual-address transition rules matter. A stale physical pointer into runtime firmware can be as wrong as a stale application pointer.

## 2.5 Configuration tables and hardware description

UEFI can publish configuration-table entries referencing structures such as ACPI or device-tree information according to platform requirements. UEFI is not itself ACPI, and using UEFI does not mean every platform uses the same hardware-description mechanism.

The loader's final kernel handoff also follows the OS/architecture boot protocol. UEFI's interface does not erase those requirements.

## Worked failure

A loader prints its final message and fails when exiting Boot Services.

**Reasoning:** inspect map buffer handling, key freshness, allocations and events, error handling, and the firmware/loader contract. Do not assume the kernel faulted if control was never transferred.

## Review

1. Can a boot application call arbitrary firmware console functions after successful exit? **No.**
2. Is the memory-map key a permanent platform identifier? **No:** it identifies a map state.
3. Is a protocol GUID a device address? **No:** it identifies an interface contract.

Next: [PI and Secure Boot](03_PI_Phases_and_Secure_Boot.md).
