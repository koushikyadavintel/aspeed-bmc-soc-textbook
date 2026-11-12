# 3. Virtual Memory, Attributes, and Ordering

## 3.1 Translation is a controlled lookup

Virtual addresses are translated through page tables selected by architectural control registers. The translation regime, supported address sizes, and granule determine table structure. Common granules are 4 KiB, 16 KiB, and 64 KiB, subject to implementation support.

With a typical 4 KiB granule, a table occupies 4 KiB and holds 512 eight-byte entries. Nine index bits select an entry. The number of active levels and address interpretation depend on configuration and architectural features.

`TTBR` registers identify table bases; `TCR` controls translation parameters; descriptors supply addresses, permissions, and attributes; `MAIR` maps memory attribute indices to attribute definitions.

Do not copy a raw descriptor constant from another system without verifying its translation level, output address width, feature assumptions, and reserved bits.

## 3.2 A permission fault is not a missing mapping

Translation can fail because a descriptor is invalid, because access permissions disallow the operation, because execution is prohibited, or because address-size/access-flag rules are violated. Distinguish those through the syndrome.

The TLB caches translations and related attributes. Updating a page-table entry is not always enough to change what a CPU uses. Correct update sequences can require ordering, cache maintenance in applicable configurations, TLB invalidation, synchronization, and break-before-make rules.

Exact sequences depend on the change and architecture. Treat them as an architectural protocol, not "write PTE; add any barrier."

## 3.3 Normal and Device memory

Normal memory supports ordinary cacheable RAM behavior, with attributes governing cacheability and shareability. Device memory models MMIO behavior and restricts transformations according to its selected subtype.

MMIO is not ordinary RAM with a special address. Reads may have side effects; combining writes or reordering accesses can be wrong. Use the operating system's accessors and mappings rather than ordinary pointer casts.

Shareability describes which observers participate in relevant coherency/order domains. "Cache coherent" does not eliminate the need for synchronization or make every DMA mapping valid.

## 3.4 Ordering versus completion

Arm permits weakly ordered behavior under its memory model. A source-level order is not automatically the observation order across CPUs and devices.

- `DMB` constrains ordering of selected accesses within its scope.
- `DSB` adds required completion/synchronization effects for selected operations.
- `ISB` synchronizes subsequent instruction execution with relevant context changes.

They are not interchangeable performance knobs. Correct scopes and access classes matter. User code should normally express synchronization through language atomics or OS primitives, letting the compiler/runtime provide the required machine sequence.

## 3.5 Atomics

Load-exclusive/store-exclusive sequences use a monitor to detect interference; store-exclusive can fail and require retry. Acquire/release operations provide useful synchronization semantics. LSE atomic instructions are an optional feature introduced after the original Armv8.0 baseline; target feature selection must match the CPU.

Lock-free does not mean wait-free, and neither means race-free without a correct algorithm. A compiler barrier alone does not create inter-CPU hardware ordering.

## Worked example: publish data

Thread A initializes a buffer, then publishes a ready flag with release semantics. Thread B waits using acquire semantics and, after observing the release, reads the initialized buffer.

The key is the matching synchronization relation. A plain or `volatile` flag does not provide the same C-language guarantee. A device doorbell introduces another boundary: DMA API and MMIO ordering requirements must also be met.

## Review

1. Does a TLB hold program data? **Answer:** translations/attributes, not the ordinary cache-line contents.
2. Does a cache flush replace a mutex? **Answer:** no.
3. Is a CPU physical address always a device DMA address? **Answer:** no; an IOMMU and DMA mappings can translate it.
4. Can a barrier fix a mapping to the wrong physical address? **Answer:** no; ordering cannot repair an incorrect target.

Next: [System integration and labs](04_Interrupts_Virtualization_and_Labs.md).
