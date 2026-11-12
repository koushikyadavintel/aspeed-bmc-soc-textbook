# 1. Endpoints, Networks, and Transport Bindings

## 1.1 What MCTP does

The Management Component Transport Protocol carries management messages among platform components. It provides a common addressing/message model over defined transport bindings.

MCTP does not define what a temperature command means. That belongs to a carried protocol such as PLDM. Nor does it create the electrical I2C or PCIe link.

```text
management application
 -> PLDM/SPDM/NVMe-MI or other message
 -> MCTP transport
 -> binding-specific framing
 -> physical transport
```

An error must be attributed to the appropriate layer. A valid MCTP response carrying a PLDM error is evidence that some transport exchange succeeded.

## 1.2 Four identifiers to keep separate

| Identifier | Meaning |
| --- | --- |
| SMBus/I2C address | Address on a particular physical bus |
| PCIe routing identity | Identity used by that transport/fabric |
| MCTP EID | Logical endpoint address in an MCTP network |
| PLDM TID | Terminus identity in the PLDM model |

Normal assigned MCTP endpoint addresses use the standard's assignable range, commonly 8 through 254 in the base model. Null, broadcast, and reserved values have specific meanings; they are not ordinary device addresses.

An EID can be assigned dynamically and can change after reset/discovery. Do not use it as a globally permanent hardware serial number.

## 1.3 Networks and interfaces

Linux models MCTP links as network interfaces, with each interface associated with an MCTP network. A network defines an EID address space and associated routes.

The same EID can exist in two distinct networks. Thus "send to EID 12" can be ambiguous without network context. A software network identifier is not necessarily a field carried in each base transport header.

A route chooses a path toward an EID. A binding-specific neighbor/address mapping establishes how to reach the next hop physically. The two are related, not identical.

## 1.4 Endpoints, bus owners, bridges

An endpoint originates or consumes messages. A bus owner coordinates management tasks such as addressing under the applicable binding. A bridge forwards between connected portions of the MCTP topology and may have routing responsibilities.

These are roles, not simply product labels. A BMC is often a bus owner/requester but its exact role depends on the topology. A device may have several logical management functions rather than one universal "chip address."

## 1.5 Binding differences

SMBus/I2C binding includes framing, addressing, and integrity rules suitable for that bus. MCTP peer communication can require controller support beyond an ordinary host-only I2C transaction pattern.

PCIe VDM binding carries messages through PCIe-defined message mechanisms. Physical link readiness, PCIe routing, and management discovery all matter.

Other bindings exist, but support in a particular kernel/image is not guaranteed. A base-protocol feature cannot compensate for a missing physical binding driver.

## Worked example

A lab BMC has two isolated MCTP networks, each containing EID 10. One endpoint is on SMBus; the other is behind a PCIe management path.

**Reasoning:** `(network, EID)` selects the logical target; binding/routing resolves the physical path. PLDM discovery then establishes management capabilities. Reusing the EID across networks is not necessarily a conflict.

## Exercise

Why is "I can reach I2C address 0x30" not proof that PLDM works?

**Answer:** the physical device must support the intended binding, have correct MCTP addressing/routing, advertise or support PLDM, and accept the particular command in its current state.

Next: [Packets and reassembly](02_Packets_Tags_and_Reassembly.md).
