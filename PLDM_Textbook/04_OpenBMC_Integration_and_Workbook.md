# 4. OpenBMC Integration, Trace Diagnosis, and Review

## 4.1 Library versus daemon

`libpldm` supplies encoders/decoders and related protocol support. The OpenBMC PLDM application coordinates transport, discovery, request lifecycle, model integration, and enabled functions according to its build/configuration.

A decoder compiling successfully does not prove that a daemon routes messages, discovers the endpoint, or exposes a sensor to Redfish.

Use the checked-out project's build/test documentation. The public PLDM repository documents Meson setup/compile/test entry points, but dependencies and enabled options vary. Unit tests do not certify physical-device interoperability.

## 4.2 Integration responsibilities

An implementation needs:

1. Transport connectivity and endpoint lifecycle.
2. Instance-ID allocation, pending requests, deadlines.
3. Capability/version discovery.
4. PDR retrieval and model synchronization where applicable.
5. Command handlers and event processing.
6. D-Bus inventory/sensor/state mapping.
7. Explicit errors and recovery.

Application logs should include enough identity and command context to diagnose a failure without printing sensitive firmware buffers or credentials.

## 4.3 Trace checklist

For a failed reading:

| Question | Evidence |
| --- | --- |
| Correct endpoint? | MCTP network/EID and terminus mapping |
| Capability supported? | Types, version, command support |
| Valid request? | Header, instance, command, length, sensor ID |
| Transport response? | Tag direction, reassembly, source |
| Successful command? | Completion code |
| Valid quantity? | Data type, length, PDR units/conversion |
| Usable reading? | Operational and availability state |
| Exposed correctly? | D-Bus object/association and API mapping |

The first failed boundary determines the next useful test.

## 4.4 Capstone: sensor and firmware traces

Use synthetic traces or authorized captures.

**Part A:** map a sensor PDR to a successful reading and then an unavailable reading. Show that unavailable does not become numeric zero.

**Part B:** draw a firmware transfer with the FD requesting two data ranges. Label which side requests and responds, then add verification and activation outcomes.

**Pass criteria:** identities and correlation values are separated, range arithmetic is bounded, errors are not success-shaped, and activation is distinguished from transfer.

**Answer guide:** transport tags, PLDM instance IDs, sensor IDs, PDR record handles, and firmware offsets all serve different jobs. A single generic integer variable named `id` cannot explain the trace.

## 4.5 Common misconceptions

- PLDM is not the electrical bus.
- Every PLDM endpoint need not support firmware update.
- A response completion code is not an HTTP status.
- A sensor descriptor is not the current reading.
- An event is not necessarily a response.
- A transferred component is not necessarily active.
- Management-protocol support does not establish encryption or authorization.

## Glossary

| Term | Meaning |
| --- | --- |
| Terminus | Logical PLDM-capable endpoint |
| TID | Terminus ID |
| Instance ID | Five-bit transaction-correlation field |
| PDR | Platform Descriptor Record |
| Effecter | Controllable modeled value/state |
| UA | Update Agent |
| FD | Firmware Device |
| Completion code | Command-defined result category |
| Repository | Set of platform descriptor records |

Return to [contents](00_README.md) or continue to [Linux debugging](../Linux_Kernel_Debugging_Textbook/00_README.md).
