# 1. Links, Topology, and Bandwidth

## 1.1 A packet fabric inside the computer

PCIe is a point-to-point serial interconnect. A link joins two ports; switches compose links into a hierarchy. It is not the shared parallel electrical bus of conventional PCI.

The root complex connects the host memory/CPU system to the PCIe hierarchy. Endpoints implement functions such as NVMe storage or networking. A switch has an upstream connection and downstream ports.

```text
host/root complex
  +-- root port -- endpoint
  `-- root port -- switch -- endpoint A
                        `-- endpoint B
```

A switch can forward multiple flows, but its upstream link can limit aggregate host traffic. The width printed on one endpoint is not the capacity of every path to memory.

## 1.2 Lanes and link width

A lane has transmit and receive differential pairs, allowing full-duplex operation. Widths such as x1, x4, x8, and x16 describe the number of lanes in the link.

Connector size, wired lane count, maximum capability, and currently negotiated width are different properties. An x16-sized slot can be electrically narrower. Bifurcation requires platform support and appropriate routing; a passive adapter cannot create arbitrary independent root ports.

## 1.3 Bandwidth arithmetic

For generations 1-5, one-direction encoded capacity is approximately:

```text
capacity = transfer rate * encoding efficiency * lane count / 8
```

| Generation | Rate per lane | Encoding | GB/s per lane, one direction |
| --- | ---: | --- | ---: |
| 1 | 2.5 GT/s | 8b/10b | 0.250 |
| 2 | 5 GT/s | 8b/10b | 0.500 |
| 3 | 8 GT/s | 128b/130b | 0.985 |
| 4 | 16 GT/s | 128b/130b | 1.969 |
| 5 | 32 GT/s | 128b/130b | 3.938 |

Thus Gen4 x4 is about 7.88 GB/s per direction before transaction overhead. Decimal GB/s is not binary GiB/s. Full-duplex does not mean a one-way transfer can use both directions' sum.

Headers, link traffic, read latency, payload size, device queues, memory bandwidth, CPU placement, and software reduce application throughput.

PCIe 6 introduces PAM4 and FLIT-mode mechanisms including error-control changes. Do not extend the earlier encoding equation unchanged or confuse symbol rate with effective transfer rate.

## 1.4 Training and the LTSSM

The Link Training and Status State Machine coordinates electrical detection, training, negotiated width/speed, normal operation, recovery, and power-related transitions.

Useful distinctions:

- Link absent: no working physical connection.
- Link trains at lower speed/width: capability or signal/configuration limitation.
- Link reaches operation but errors under load: integrity, power, device, or traffic-dependent failure.
- Link retrains: may be recovery, power transition, or software-triggered behavior.

Do not reduce every reduced-width symptom to a driver bug. Check slot wiring, power, firmware policy, retimers, and physical design through authorized platform procedures.

## Worked bottleneck

Two Gen4 x4 endpoints share a Gen4 x4 switch uplink. Each can reach roughly 7.88 GB/s encoded one-way capacity on its own link, but simultaneous host-bound traffic shares the uplink. Summing endpoint specifications overstates aggregate host throughput.

## Review

Why is "Gen5 capable" insufficient to predict a benchmark?

**Answer:** inspect negotiated rate/width along the entire path, transaction sizes, host/device limitations, workload direction, and software.

Next: [Enumeration and BARs](02_Enumeration_Configuration_and_BARs.md).
