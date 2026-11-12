# 2. PDRs, Sensors, Effecters, and Events

## 2.1 Description before interpretation

A Platform Descriptor Record describes aspects of the managed platform: entities, relationships, sensors, effecters, or related data. A PDR repository is the set of such records.

An entity identifies a modeled component with type/instance/container relationships. A sensor ID identifies a measurement/state source within the appropriate terminus context. A record handle identifies a repository record. None is a substitute for the others.

The number 42 is not enough to identify a sensor across every terminus.

## 2.2 Retrieving a repository

Repository information and `GetPDR`-style operations allow records to be retrieved, potentially using multipart transfer.

Track separately:

- Current record handle.
- Next record handle.
- Transfer handle and transfer-operation state.
- Record length/type/version.
- Repository change information and applicable integrity checks.

Do not confuse "next part of this record" with "next record." Reject inconsistent lengths and unsupported record formats explicitly.

Repository changes can invalidate sensor configuration and cached associations. Preserve enough version/change context to detect stale interpretation.

## 2.3 Numeric versus state sensors

A numeric sensor carries a typed reading with metadata such as units, range, resolution/offset, and operational state as applicable. Scaling must follow the descriptor's defined fields and the command response's representation.

A state sensor reports one or more discrete states from specified state sets. A state byte is not a temperature merely because its value is 42.

For a hypothetical descriptor defining a simple linear conversion `physical = 0.25 * raw`, a raw reading of 160 corresponds to 40 units. This is only a conversion illustration, not the complete binary layout or universal PDR equation.

Unavailable, failed, disabled, or initialization states must be retained. An invalid reading must not become a plausible numeric zero.

## 2.4 Effecters control state

Effecters represent controllable numeric or discrete values. Before setting one, discover its allowed states/range, enablement, permissions/policy, and present state.

An accepted request may initiate a transition. Read back the appropriate present/pending state or observe the documented event to establish completion.

A fan-related effecter can interact with thermal-safety logic. Do not experiment with it on a production server or assume a low-level set overrides all policies safely.

## 2.5 Events complement polling

Events report changes asynchronously and can reduce polling load. Event receiver configuration, supported event classes, buffer/transfer modes, sequencing, and acknowledgments depend on capability and version.

An event needs correlation with current repository/terminus state. If a device rebooted and IDs changed, applying an old event to a new sensor mapping can corrupt the model.

Polling remains useful for reconciliation and freshness. An event-based design still needs recovery after missed events or connection loss.

## Worked end-to-end model

```text
endpoint PDR -> requester sensor model
 -> GetSensorReading/event -> decoded physical quantity + status
 -> D-Bus sensor/inventory relationship -> Redfish representation
```

Each conversion must preserve identity, units, status, and lifecycle. A correct PLDM decode with a wrong chassis association can still create a wrong API result.

## Exercises

1. Why can't you hard-code one sensor ID for every device? **Answer:** identity is terminus/model-specific.
2. Is a record handle a transfer offset? **Answer:** no.
3. Does a successful set prove the physical value changed? **Answer:** only the command's defined semantics apply; verify completion/state.

Next: [Firmware update](03_Firmware_Update_State_Machine.md).
