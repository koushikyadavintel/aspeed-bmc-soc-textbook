# 1. Messages, Identity, and Capability Discovery

## 1.1 Meaning above transport

PLDM defines management commands and data models. MCTP supplies a common transport, but reaching an endpoint does not establish that it supports PLDM or a particular command.

```text
physical route -> MCTP endpoint -> PLDM terminus
 -> supported type/version -> supported command -> operation
```

A terminus is a logical PLDM endpoint. It is not necessarily identical to a physical package or one OS process.

## 1.2 Header and response

A base PLDM message header contains a five-bit instance ID, request/datagram-related flags, header version/type information, and a command byte. Exact permitted bits and message forms come from the base specification.

Responses commonly begin their command-specific payload with a completion code. Do not read success-only fields when the completion indicates failure. An unsupported command response can be a valid transport/protocol exchange.

Instance ID is a bounded transaction-correlation value. It is neither a sensor ID nor an endpoint address. It can be reused only according to the request lifecycle and correlation context.

## 1.3 Type families

| Type | Common purpose |
| --- | --- |
| Base | Discovery and core identity/capabilities |
| SMBIOS transfer | System-description data exchange |
| Platform Monitoring and Control | PDRs, sensors, effecters, events |
| BIOS Control and Configuration | Attribute tables and configuration |
| FRU Data | Structured replaceable-unit information |
| Firmware Update | Negotiated component update workflow |

OEM extensions exist, but their semantics must come from the applicable vendor contract. Do not decode an unknown command by applying an unrelated standard payload layout.

## 1.4 Capability discovery

A typical requester determines terminus identity and uses commands such as `GetPLDMTypes`, `GetPLDMVersion`, and `GetPLDMCommands`. Command support can depend on the type version used in the query.

A cached table should include identity, transport path, supported versions/commands, and freshness. A device reset or replacement can invalidate it.

TID and MCTP EID can coincidentally have the same numeric value but still remain different namespaces. Maintain an explicit mapping rather than using one as the other.

## 1.5 Response correlation

Before accepting a response, validate:

1. Transport source/network and expected route.
2. Message type and message length.
3. Request/response form and supported header version.
4. PLDM instance ID, type, and command.
5. Completion code.
6. Command-specific length and values.

Timeouts must release pending state. Late responses must not be attached to a new request that reused an ID without a correct lifecycle policy.

Not every event or device-originated request is a reply to the most recent BMC command. Bidirectional request handling needs separate state.

## Worked example

A terminus supports PLDM Base but not Firmware Update. Reading types succeeds; sending an update command fails.

**Reasoning:** "PLDM-capable" is not equivalent to "supports every type." The correct application result is an explicit unsupported capability, not repeated transport retries.

## Exercise

What can a success completion code prove?

**Answer:** only the result defined for that command in the relevant state/version. It does not universally prove a physical effect completed or new firmware activated.

Next: [PDRs and platform data](02_PDRs_Sensors_Effecters_and_Events.md).
