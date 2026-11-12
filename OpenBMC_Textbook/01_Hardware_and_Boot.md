# 1. The BMC, Its Hardware, and Its Boot

## 1.1 Two computers in one server

The host executes workloads; the BMC manages the platform. They have different CPUs, software, reset domains, and often different power dependencies. A host crash need not stop the BMC. Loss of standby power can stop both.

BMC resources commonly include a SoC, DRAM, boot storage, network interfaces, UARTs, watchdogs, and hardware-management buses. The managed devices may include fan controllers, power supplies, EEPROMs, GPIO expanders, and components reached through MCTP.

The phrase "out-of-band" describes a management path independent of the host OS. It does not prove physical network separation, isolation from a shared NIC, or availability during every power state.

## 1.2 Boot as a chain of contracts

```text
reset -> SoC ROM -> optional early loader -> U-Boot/other firmware
      -> kernel + board description -> root filesystem -> PID 1
      -> platform services -> functional management interfaces
```

Each arrow has inputs, prerequisites, outputs, and evidence:

| Handoff | Required information | Evidence |
| --- | --- | --- |
| ROM to loader | Boot source, valid image, execution environment | ROM/loader UART or documented status |
| Loader to kernel | Entry point, DTB or other platform data, memory layout | Kernel banner and early console |
| Kernel to userspace | Root device, filesystem, init executable | Root mount and PID 1 messages |
| systemd to service | Unit configuration, permissions, dependencies | Unit state, journal, bus ownership |
| Service to usable feature | Discovery, hardware, valid data | Actual operation, not just process existence |

No Linux log can diagnose a stage before Linux started. The last UART line is useful evidence, but buffered output and asynchronous work mean it is not necessarily the failed instruction.

## 1.3 ROM and bootloader responsibilities

ROM samples boot configuration and loads or authenticates a next stage according to SoC rules. Early firmware may initialize SRAM, DRAM, clocks, pin multiplexing, and security controls. U-Boot commonly selects an image, loads the kernel/DTB, constructs boot arguments, and transfers execution.

These jobs vary. TF-A is relevant to some Arm A-profile platforms but is not a universal stage on every OpenBMC SoC. A FIT container can contain multiple components; a filename alone does not identify how the ROM expects to boot it.

Secure boot authenticates selected executable components according to a chain rooted in platform trust. A hash stored beside an unsigned image detects corruption only if the expected hash itself is trusted.

## 1.4 Kernel, device tree, and rootfs

The kernel controls memory, scheduling, drivers, storage, and networking. A DTB describes non-self-enumerating hardware and its connections. Correct source code with the wrong DTB can probe the wrong device, fail to bind, or configure the wrong pin.

The root filesystem supplies executables, libraries, configuration, and units. A successful kernel start followed by a root-mount failure suggests a different investigation from a service crash after login.

Kernel drivers may publish hwmon, IIO, GPIO, network, MTD, or other interfaces. Access is subsystem-specific: a sensor daemon reading hwmon is not directly calling a kernel-internal I2C function.

## 1.5 systemd: dependencies are not readiness

`After=` orders units if they are scheduled; it does not pull a unit into the transaction. `Wants=` and `Requires=` express dependency relationships with different failure semantics. A process starting successfully does not prove that its asynchronous device discovery completed.

Inspect actual units:

```sh
systemctl --failed --no-pager
systemctl list-units --type=service --no-pager
systemctl cat bmcweb.service
journalctl -b -u bmcweb.service --no-pager
```

The service name is common, not universal. If absent, discover the target image's unit names rather than fabricating an equivalent command.

Readiness has several milestones: console, kernel, network, authenticated API, inventory populated, sensor freshness, power-control policy satisfied. Define which one a test asserts.

## Exercise

You can log in, Redfish responds, but no temperature appears. Has boot succeeded?

**Answer:** several boot milestones succeeded, but platform-management readiness is incomplete. Check the value's provider and discovery before changing ROM or kernel boot arguments.

Next: [D-Bus, sensors, and Redfish](02_DBus_Sensors_and_Redfish.md).
