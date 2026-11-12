# 3. Discovery, Routing, and Linux Integration

## 3.1 Control traffic configures the transport

MCTP control messages use the control message type and commands for functions such as endpoint identity, assignment, supported message types, and routing information.

Discovery is not one universal broadcast script. The binding and topology determine which control exchanges are meaningful and how the physical target is reached before normal EID communication is ready.

A conceptual lifecycle is:

```text
physical link present -> binding available -> discover endpoint
 -> obtain/assign EID -> establish route/address mapping
 -> query supported message types -> start application discovery
```

Not all endpoints have dynamically assigned EIDs, and not all topologies need identical routing exchanges.

## 3.2 Reset changes the evidence

An endpoint reset can invalidate EID assignments, supported capability caches, routes, pending requests, and upper-layer state. Rediscovery must reconcile old and new identity rather than append duplicates indefinitely.

For hotplug, distinguish disappearance from a temporary timeout. Make removal and rediscovery behavior explicit. A durable UUID or inventory identity, when available and trustworthy, serves a different purpose from an EID.

## 3.3 Linux AF_MCTP

Linux provides `AF_MCTP`, `SOCK_DGRAM` sockets. Socket addresses include a network, EID, message type, and tag/ownership information.

The kernel documentation states that applications provide the message-type byte at the start of the send buffer and receive it in the message buffer. Do not omit it because a type also appears in the destination address.

An outgoing request with `MCTP_TAG_OWNER` can cause kernel-managed tag allocation. Responses are associated with the originating socket according to documented rules. An inbound-request socket binds with the appropriate owner semantics rather than assuming every response is delivered to any listener.

Tag exhaustion can produce `EAGAIN`. Treat it as backpressure or a lifecycle issue to handle, not proof of a broken physical bus.

## 3.4 Datagram programming obligations

A robust application must:

1. Check socket creation and bind/send/receive errors.
2. Initialize complete address structures.
3. Set correct network, destination, type, and ownership.
4. Bound receive buffers and detect truncation.
5. Validate source, lengths, and application correlation fields.
6. Apply deadlines/cancellation and release resources.

The kernel handles transport mechanics, not the validity of a PLDM completion code or PDR payload. Successful `sendto` means the syscall accepted a message according to its contract, not that the endpoint performed the requested action.

Capabilities, namespaces, socket permissions, kernel version, and binding-driver support affect availability.

## 3.5 Observing a Linux implementation

The [Code Construct mctp tools](https://github.com/CodeConstruct/mctp) and implementation-specific daemons can expose links, addresses, routes, and neighbor information. Tool versions and daemon interfaces differ.

Use the installed tool's `--help` and the platform's documented observation commands. Avoid presenting route-write commands as passive diagnosis. A bus-owner daemon may own configuration; manual changes can race it.

## Worked diagnosis

Control traffic reaches the endpoint, but a PLDM request times out.

**Answer guide:** verify advertised message support, exact destination network/EID, socket type-byte handling, tag ownership/lifecycle, PLDM instance correlation, and endpoint readiness. A successful control exchange narrows the problem but does not prove the upper protocol works.

Next: [Trace workbook](04_Trace_Workbook_and_Reference.md).
