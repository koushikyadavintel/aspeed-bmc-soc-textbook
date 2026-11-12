# 2. Packets, Message Tags, and Reassembly

## 2.1 A packet is not a message

A message contains the carried protocol data and begins with an MCTP message-type byte. It can span multiple packets. Each packet has a base transport header and binding framing.

The base header contains:

- Header version/reserved information.
- Destination and source EIDs.
- Start-of-message (SOM) and end-of-message (EOM).
- A two-bit packet sequence number.
- Tag owner and a three-bit message tag.

Use the specification for bit positions and permitted combinations. The message type starts the message body; it is not repeated as a fresh type byte in every continuation packet.

## 2.2 SOM, EOM, and sequence

A one-packet message has SOM=1 and EOM=1. A fragmented message starts with SOM, continues with neither boundary flag, and ends with EOM.

Sequence increments modulo four within a fragmented message. A mismatch can identify loss/reordering/incorrect context, but there is no universal automatic end-to-end retransmission guarantee.

The receiver tracks the message's endpoint/tag/ownership context, expected sequence, bounded accumulation, and timeout. A continuation without an established context is not an excuse to concatenate arbitrary data.

## 2.3 Tags and ownership

The owner of a message tag sets the tag-owner indication in the ownership/request direction. A response uses the corresponding tag with the opposite ownership direction.

Tags have limited space and must be managed across concurrent exchanges. The same numeric tag on another peer or ownership context is not automatically a conflict; the context matters.

MCTP control and PLDM have their own instance identifiers. Transport tags and application instance IDs correlate at different layers. Matching only the three-bit tag is not a complete PLDM response validation.

## 2.4 Correct fragmentation arithmetic

Assume a hypothetical usable packet-body capacity of 64 bytes **after the base transport header**, excluding binding overhead. Let the complete message body be 150 bytes including its one-byte type.

```text
packet 1: 64 bytes, SOM=1 EOM=0 seq=0
packet 2: 64 bytes, SOM=0 EOM=0 seq=1
packet 3: 22 bytes, SOM=0 EOM=1 seq=2
total:    150 bytes
```

Only the first body byte is the type byte. The receiver reassembles 150 bytes, of which 149 belong to the carried protocol.

This is an arithmetic example, not a claim about every binding's MTU definition or maximum message size. Verify whether a tool's displayed MTU includes/excludes each header.

For a 100-byte message and the same 64-byte capacity, the split is 64+36, not three fragments ending in a body larger than the stated capacity.

## 2.5 Reliability and limits

Physical/binding checks can detect corruption. Packet sequence supports reassembly validation. Application protocols supply their own response timing and error behavior.

Bound memory and pending exchanges. Handle timeout, endpoint reset, duplicate or stale response, oversize message, invalid sequence, and tag exhaustion explicitly.

Blind retries of state-changing operations can repeat an action. Retry semantics belong to the command/state machine, not just the fact that a response timed out.

## Exercise

A five-packet message begins at sequence 2. What are the sequence numbers?

**Answer:** 2, 3, 0, 1, 2. Only the first has SOM and only the last has EOM. The repeated 2 is not itself an error because the two-bit counter wraps.

Next: [Discovery, routing, and Linux](03_Discovery_Routing_and_Linux.md).
