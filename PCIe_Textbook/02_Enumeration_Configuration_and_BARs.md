# 2. Enumeration, Configuration Space, and BARs

## 2.1 Discovery assigns a software-visible identity

Firmware and/or the OS walk the PCI hierarchy, discover functions, assign bus numbers and resources, and configure operation. The division of work depends on platform and OS policy.

A conventional function identity is bus:device.function, often shown with a PCI domain/segment as `dddd:bb:dd.f`. That identity is not an IP address, MCTP EID, or necessarily a permanent physical slot identifier.

Topology can change with firmware configuration or hotplug. Use stable platform identities where persistence matters rather than assuming one BDF forever.

## 2.2 Configuration space

Configuration space exposes vendor/device identity, class information, command/status, BARs, and capability structures. PCIe functions can expose extended configuration space beyond the legacy region.

Capabilities advertise features such as PCI Express state, power management, MSI/MSI-X, AER, and virtualization. Presence does not mean the feature is enabled or correctly supported by every layer.

Read capabilities through supported OS tools/APIs. Writing arbitrary offsets can disable devices, change address decoding, or crash the host.

## 2.3 BARs request address resources

A Base Address Register describes a resource aperture, commonly MMIO. Enumeration allocates address space and programs its base.

A BAR is not automatically a RAM allocation, DMA buffer, or a pointer safe for applications. A 64-bit BAR consumes the required pair of BAR register slots. Its CPU mapping and access policy are established by the OS.

Devices often have multiple apertures for control registers, queue doorbells, or device memory. The device-specific programming specification defines their semantics.

BAR sizing involves configuration accesses that can temporarily change decoding state; do not reproduce probing writes manually on a live device.

## 2.4 Driver binding and lifecycle

Linux matches devices to drivers using supported IDs and policies. A typical driver:

1. Enables the device and claims resources.
2. Establishes DMA addressing limits.
3. Maps MMIO safely.
4. Allocates queues/buffers and configures interrupts.
5. Initializes the device and starts processing.

Teardown must stop DMA and interrupts before releasing the resources they can access. Unmapping a buffer while the device can still write it creates a memory-corruption risk.

Managed APIs can simplify release, but they do not automatically stop device engines in the correct hardware order.

## 2.5 Linux observation

On an authorized machine with pciutils:

```sh
lspci -Dnn
lspci -t
```

For a discovered BDF:

```text
lspci -s <domain:bus:device.function> -vv
```

Look for current versus maximum link state, driver binding, BAR resources, and reported errors. Some detailed configuration reads require privilege; use an appropriate lab system and a limited target rather than indiscriminate deep probing.

`lspci` describes what the kernel can inspect. A function absent from it may be physically unpowered, not enumerated, hidden by policy, or behind a failed link.

## Exercise

A BAR is assigned, but register reads return unusable values.

**Answer guide:** check power/reset state, driver ownership, whether the aperture is enabled, mapping/access width, device-specific requirements, and link/error state. Resource assignment alone does not establish functional device readiness.

Next: [Transactions, DMA, and interrupts](03_Transactions_DMA_and_Interrupts.md).
