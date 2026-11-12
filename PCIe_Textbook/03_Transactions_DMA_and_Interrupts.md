# 3. Transactions, DMA, and Interrupts

## 3.1 Requests and completions

Transaction Layer Packets encode operations such as memory reads, memory writes, configuration accesses, and messages.

A memory write is typically posted: it does not receive an ordinary completion proving that the target application has processed it. A memory read is non-posted and receives completion traffic, potentially split according to constraints.

Request tags correlate non-posted requests and completions. These are PCIe transaction tags, not MCTP message tags or PLDM instance IDs.

Completion timeout, unsupported request, poisoned data, and malformed traffic are different conditions. Error interpretation requires the transaction context.

## 3.2 Link reliability and credits

In conventional pre-FLIT operation, data-link mechanisms provide per-link sequence/error checking and replay. This is not the same as application-level retry.

Credit-based flow control prevents a sender from overrunning advertised receive buffering for relevant traffic categories. A link with insufficient available credits can stall despite having high signaling capacity.

End-to-end ordering rules, traffic classes, relaxed-ordering attributes, and requester behavior affect visibility. "PCIe is ordered" is too vague to justify a driver synchronization sequence.

## 3.3 MMIO versus DMA

With MMIO, the CPU accesses device apertures. With DMA, the device accesses host memory using addresses established through the OS DMA mapping API.

```text
CPU virtual address -> CPU translation -> system memory
device DMA address  -> IOMMU/host translation -> system memory
```

These paths may resolve to the same memory but use different address values and permission controls.

Coherent DMA mappings and streaming mappings have different synchronization rules. Cache coherency does not by itself order descriptor updates before a device doorbell; use the required DMA/MMIO barriers and accessors.

Never put a raw userspace pointer into a device register and assume it is a valid DMA address.

## 3.4 A queue-driven I/O example

1. Driver obtains DMA-safe queue/data mappings.
2. CPU fills a command descriptor.
3. Driver performs required synchronization/order operations.
4. Driver writes a device doorbell through MMIO.
5. Device fetches descriptors and transfers data using DMA.
6. Device records completion and signals an interrupt or is polled.
7. Driver checks completion status and synchronizes/reuses resources safely.

The order is a logical example, not a portable instruction sequence. A real device specification and Linux DMA API define the required details.

## 3.5 MSI and MSI-X

Message Signaled Interrupts use configured memory-write transactions to notify the host interrupt subsystem. MSI-X supports a device table and potentially many independently managed vectors.

A vector number in driver software is not necessarily the raw interrupt-controller number or a CPU index. OS allocation/remapping and affinity policy intervene.

An interrupt indicates an event to inspect; the driver still must read completion state and handle races, masking, coalescing, and shared device conditions.

## Worked performance analysis

A read-heavy workload uses tiny requests and reaches low throughput on a fast link. Candidate limits include round-trip latency, outstanding request count/tags, maximum read-request size, completion splitting, device processing, and software queue depth.

**Answer guide:** measure traffic direction and request distribution. Raising link generation cannot eliminate a transaction-latency bottleneck by itself.

Next: [Reliability, virtualization, and labs](04_Reliability_Virtualization_and_Labs.md).
