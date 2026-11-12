# 4. Trace Workbook, Security Boundaries, and Reference

## 4.1 Decode from outside inward

For each captured packet record:

```text
timestamp / interface / direction
binding source and destination
MCTP source EID, destination EID
SOM, EOM, sequence, owner, tag
message type on the first fragment
reassembly result
upper-protocol fields and response status
```

Do not decode a continuation fragment's first data byte as a new PLDM type. Reassemble before parsing a message that spans packets.

## 4.2 Worked request/response

Illustrative assigned endpoints:

```text
request:  EID 8 -> EID 12, owner=1, tag=3, type=PLDM
response: EID 12 -> EID 8, owner=0, tag=3, type=PLDM
```

Both can be single packets with SOM=EOM=1. The PLDM layer additionally matches its own instance, type, and command, then checks the completion code and payload.

An endpoint sending an unrelated event can originate a new exchange in the other direction. Do not classify every packet from the device as a response.

## 4.3 Missing-fragment exercise

Expected sequence is 0,1,2 for a three-fragment message. The capture contains 0,2.

Questions:

1. Is the carried PLDM payload safe to parse?
2. What evidence distinguishes a capture loss from an actual link/stack loss?
3. What happens to the pending application request?

**Answer guide:** do not parse incomplete reassembly as a valid message. Compare captures at appropriate boundaries and stack/error counters; consider that the capture tool itself dropped a packet. The requester should reach a defined timeout/error path rather than return partial success.

## 4.4 Failure matrix

| Layer | Possible failure | Useful evidence |
| --- | --- | --- |
| Electrical | Link/power/pull-up issue | Authorized board measurements/status |
| Binding | Wrong framing/address/check | Captured binding fields |
| MCTP network | Wrong network/EID/route | Route/address/neighbor state |
| Reassembly | Sequence/tag/context/size | Full packet sequence and timeout |
| Control | Assignment/discovery disagreement | Control command/response |
| Application | Unsupported command or invalid state | PLDM or other protocol completion |

Do not fix a Redfish symptom by reassigning EIDs until evidence points to the transport.

## 4.5 Security is not implied by transport

MCTP addressing is not authentication. A tag is not a secret. A checksum is not authorization. PLDM over MCTP is not automatically encrypted or mutually authenticated.

SPDM and secured-message designs can provide additional security under a defined platform policy. Their existence does not mean every device or route uses them. Validate trust establishment, key management, secured transport/binding support, and authorization at the relevant layers.

Trace files may contain inventory, firmware data, or other sensitive material. Keep real captures private and publish only sanitized synthetic examples.

## Glossary

| Term | Meaning |
| --- | --- |
| EID | Endpoint ID in an MCTP network |
| Binding | Mapping of MCTP onto a physical transport |
| SOM/EOM | Start/end of message |
| TO | Tag-owner indication |
| Message tag | Three-bit transport correlation value |
| Reassembly | Combining packets into one bounded message |
| Bus owner | Role coordinating applicable bus-management behavior |
| AF_MCTP | Linux socket address family for MCTP |

Return to [contents](00_README.md) or continue with [PLDM](../PLDM_Textbook/00_README.md).
