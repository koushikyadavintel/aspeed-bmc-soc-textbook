# 3. Firmware Update as a Negotiated State Machine

## 3.1 Roles and identities

The Update Agent (UA) orchestrates an update. The Firmware Device (FD) is updated. A device may contain multiple firmware components, each with its own identity, version, compatibility, and activation requirements.

The UA first determines device identity/capabilities and installed component information using the applicable commands. Matching only a filename or product string is insufficient.

The package describes applicable device records and components according to the update specification. Vendor authentication and platform authorization remain separate requirements.

## 3.2 Preparation and component negotiation

A conceptual flow includes:

```text
discover device -> validate package applicability
 -> request update -> pass component information
 -> negotiate/update component -> transfer -> verify -> apply
 -> activate -> confirm running version
```

Command ordering and states are normative in DSP0267. Commands such as `RequestUpdate`, `PassComponentTable`, and `UpdateComponent` participate according to the chosen flow and supported revision.

The FD may reject a component because of compatibility, state, version policy, or resource constraints. A rejection is not necessarily a transport failure.

## 3.3 The device requests image data

A crucial distinction: during the standard firmware-data transfer, the FD issues `RequestFirmwareData` requests specifying offsets/lengths, and the UA returns the requested bytes in responses.

```text
FD -> UA: RequestFirmwareData(offset, length)
UA -> FD: response carrying the requested component data
```

Thus the UA manages the update but does not simply push arbitrary data packets whenever it wants. The implementation must support the bidirectional request/response roles correctly.

Bounds-check every requested range against the selected component. Repeated or delayed requests require defined handling. Transport fragmentation is below this layer and is not a replacement for component offset tracking.

## 3.4 Transfer, verify, apply, activate

The FD reports transfer completion, verification completion, and application completion through the protocol's state machine. The UA responds and proceeds according to the defined results.

These phases are distinct:

- **Transfer:** component bytes were exchanged.
- **Verification:** the device checked them according to its implementation/policy.
- **Apply:** the device processed the component.
- **Activation:** the selected firmware becomes active, possibly after reset.

Protocol success does not by itself prove a particular cryptographic policy. Establish the device's trust anchor, signed-image policy, rollback controls, and target authorization separately.

## 3.5 Failure and interruption

Keep per-device/per-component state, deadlines, expected requests, error results, and activation requirements. Handle cancellation, device reset, transport loss, and a UA restart according to specification and platform recovery policy.

Blindly resending a state-changing command can be wrong if the FD already advanced. Re-query or recover through the prescribed state rather than inventing an idempotence assumption.

Never test update recovery by interrupting production equipment. Use a vendor-supported lab procedure and a known recovery path.

## Exercise

An update transferred 100% of bytes, but the old version still runs. Was the transfer counter wrong?

**Answer:** not necessarily. Verification/apply could have failed, activation may require reset, selection may differ, or rollback may have occurred. Inspect the full state machine and actual running component identity.

Next: [OpenBMC integration and workbook](04_OpenBMC_Integration_and_Workbook.md).
