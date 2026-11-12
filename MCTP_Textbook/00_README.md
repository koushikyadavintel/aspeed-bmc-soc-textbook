# MCTP: Management Transport from First Principles

| Chapter | Focus |
| --- | --- |
| [1. Endpoints and bindings](01_Endpoints_Networks_and_Bindings.md) | EIDs, physical addresses, networks, bus owners, bridges |
| [2. Packets and messages](02_Packets_Tags_and_Reassembly.md) | Headers, tags, sequencing, fragmentation, reliability |
| [3. Discovery and Linux](03_Discovery_Routing_and_Linux.md) | Control commands, routes, AF_MCTP, lifecycle |
| [4. Trace workbook](04_Trace_Workbook_and_Reference.md) | Worked fragments, diagnosis, security boundaries, glossary |

**Prerequisites:** basic binary/hex, [OpenBMC](../OpenBMC_Textbook/00_README.md). PCIe binding readers should study [PCIe](../PCIe_Textbook/00_README.md).

Sources: [DMTF PMCI](https://www.dmtf.org/standards/pmci), DSP0236 base, DSP0237 SMBus/I2C, DSP0238 PCIe VDM, DSP0239 message types, and [Linux MCTP](https://docs.kernel.org/networking/mctp.html).

Exact wire encodings and discovery rules depend on the applicable base/binding revision. The book uses normal assigned EIDs and labels illustrative capacities explicitly.
