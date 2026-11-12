# PCI Express: From Links to Drivers

| Chapter | Focus |
| --- | --- |
| [1. Links and bandwidth](01_Links_Topology_and_Bandwidth.md) | Lanes, hierarchy, generations, training, bottlenecks |
| [2. Enumeration and resources](02_Enumeration_Configuration_and_BARs.md) | BDF, configuration space, BARs, driver binding |
| [3. Transactions and DMA](03_Transactions_DMA_and_Interrupts.md) | TLPs, completions, credits, DMA, MSI/MSI-X |
| [4. Reliability and labs](04_Reliability_Virtualization_and_Labs.md) | AER, reset, SR-IOV, diagnostics, MCTP VDM |

**Prerequisites:** hexadecimal, memory/address concepts, basic Linux. Read [Arm memory](../ARMv8_A_Textbook/03_Memory_Translation_and_Ordering.md) for CPU-side distinctions.

Sources: [PCI-SIG specifications](https://pcisig.com/specifications), [Linux PCI documentation](https://docs.kernel.org/PCI/index.html), [driver guide](https://docs.kernel.org/PCI/pci.html), [DMA guide](https://docs.kernel.org/core-api/dma-api-howto.html).

The detailed walkthrough uses conventional pre-PCIe-6 transaction/link concepts. Later FLIT-mode behavior differs; do not generalize older packet/replay details to every generation.
