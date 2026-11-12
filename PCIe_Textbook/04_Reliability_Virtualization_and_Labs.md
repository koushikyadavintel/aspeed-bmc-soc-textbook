# 4. Reliability, Virtualization, and Management Traffic

## 4.1 Errors and recovery

Advanced Error Reporting can expose correctable and uncorrectable conditions with additional context. A correctable error can still be important if its rate changes; an uncorrectable report does not by itself identify the damaged component.

Correlate topology, requester/completer identity where available, timestamps, load, power transitions, and link state. The reporting port can be upstream of the actual cause.

Reset scopes differ: function-level, link/hot reset, and broader platform resets affect different resources. A function reset is not automatically safe while another function shares underlying hardware or while DMA is active.

Do not run reset, remove/rescan, or configuration-write experiments on a production system as a first diagnostic.

## 4.2 SR-IOV and isolation

Single Root I/O Virtualization separates a Physical Function from configurable Virtual Functions. The PF controls device-wide resources; VFs expose assignable function interfaces according to the device's design.

An IOMMU, interrupt remapping, platform routing/isolation, hypervisor configuration, and device behavior jointly determine safe assignment. Merely enabling VFs does not prove isolation.

ACS, ATS, PASID, and related capabilities address different routing/translation needs. Their availability is platform-specific and must be evaluated as a system, not a checklist of acronyms.

## 4.3 MCTP over PCIe VDM

PCIe Vendor Defined Messages can carry management traffic under a defined binding. In MCTP-over-PCIe, distinguish:

```text
PCIe routing identity -> MCTP endpoint/network -> PLDM operation
```

A working ordinary storage driver does not prove that a PCIe management VDM route and endpoint have been configured. Conversely, management availability does not prove the normal data path is healthy.

Read the [MCTP volume](../MCTP_Textbook/00_README.md) for EIDs and binding-specific discovery. Do not equate an EID with a PCIe BDF.

## 4.4 Read-only topology lab

1. Record the host and kernel identity.
2. Draw the hierarchy from `lspci -t`.
3. Pick one endpoint and its parent path.
4. Record maximum/current link speed and width at relevant hops.
5. Identify the driver and resource apertures.
6. Estimate a one-direction encoded bottleneck.
7. Explain why measured payload bandwidth may be lower.

**Pass condition:** the bottleneck estimate includes the shared upstream path and labels the difference between theoretical encoded capacity and measured application throughput.

Do not "validate" the estimate by forcing link speed or writing configuration registers unless a separate authorized test procedure requires it.

## 4.5 Review answers

- **Can a device DMA anywhere it wants?** It should be constrained by mapping and isolation policy; do not assume enforcement without the platform configuration.
- **Does a posted write guarantee device completion?** No; use device-defined completion/ordering mechanisms.
- **Can a Gen4 device run at Gen3?** Commonly yes when negotiated with supported link behavior; inspect the actual state.
- **Is a switch another endpoint?** Its forwarding/bridge role differs from an endpoint function's workload role.

## Glossary

| Term | Meaning |
| --- | --- |
| BDF | Bus/device/function identity |
| BAR | Base Address Register/resource aperture description |
| TLP | Transaction Layer Packet |
| DLLP | Data Link Layer Packet in applicable link modes |
| LTSSM | Link training/status state machine |
| DMA | Device-initiated memory access |
| AER | Advanced Error Reporting |
| PF/VF | Physical/Virtual Function in SR-IOV |
| VDM | Vendor Defined Message |

Return to [contents](00_README.md) or continue to [MCTP](../MCTP_Textbook/00_README.md).
