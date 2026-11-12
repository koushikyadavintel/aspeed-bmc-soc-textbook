# Public sources and verification notes

**Research date: 2026-10-22.** These resources were chosen for authority and relevance to the actual learning questions, not search-engine ranking. Prefer a normative specification for wire formats, project documentation for implementation behavior, and a lab measurement for a claim about your board.

## Checked public resources

The pages below were fetched during authoring. A fetched overview is not a claim that every linked manual, PDF, or code path was reviewed.

| Subject | Resource | Used for |
| --- | --- | --- |
| OpenBMC | [Project documentation](https://github.com/openbmc/docs) | Development, updates, console, host management, Redfish entry points |
| Yocto | [Concepts manual](https://docs.yoctoproject.org/overview-manual/concepts.html) | BitBake, metadata, tasks, recipes, layers, shared state |
| Public BSP | [NXP walnascar README](https://github.com/nxp-imx-support/meta-nxp-openbmc/blob/walnascar/README.md) | Public setup sequence, machine names, image target, WIC output |
| Linux MCTP | [Kernel MCTP documentation](https://docs.kernel.org/networking/mctp.html) | Network-scoped EIDs, datagram sockets, tags, message-type byte |
| Linux tracing | [ftrace](https://docs.kernel.org/trace/ftrace.html) | Tracefs, event/function tracing, configuration and overhead |
| Linux memory diagnostics | [KASAN](https://docs.kernel.org/dev-tools/kasan.html) | Detector modes, use-after-free/out-of-bounds coverage, support limits |
| Linux crash capture | [kdump](https://docs.kernel.org/admin-guide/kdump/kdump.html) | Capture kernel, reserved memory, vmcore, matching analysis tools |
| PMCI | [DMTF PMCI overview](https://www.dmtf.org/standards/pmci) | MCTP/PLDM purpose and specification identifiers |
| PLDM | [OpenBMC PLDM](https://github.com/openbmc/pldm) | Implemented type families, build/test entry points, integration |
| PCI | [Linux PCI driver guide](https://docs.kernel.org/PCI/pci.html) | Discovery, resources, driver lifecycle; use current APIs in actual code |
| TF-A | [Firmware design](https://trustedfirmware-a.readthedocs.io/en/latest/design/firmware-design.html) | Boot-stage roles, AArch32/AArch64 distinction, PSCI, configuration handoff |
| AArch64 ABI | [AAPCS64](https://github.com/ARM-software/abi-aa/blob/main/aapcs64/aapcs64.rst) | Authoritative calling-convention reference; linked, not reproduced |
| C build | [GCC overall options](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html) | Preprocess, compile, assemble, link; stopping stages |
| Enterprise RAG legacy | [OPEA repository](https://github.com/opea-project/Enterprise-RAG) | Migration notice; 2.3.0 identified as its final release |
| Enterprise RAG current | [Intel repository](https://github.com/intel/enterprise-rag) | Component of the solutions platform, composed pipelines, deployment context |
| Enterprise RAG architecture | [Architecture reference](https://github.com/intel/enterprise-rag/blob/main/docs/reference/architecture.md) | Platform/inference dependencies, component registry, pipeline composition |
| RISC-V | [Specifications entry point](https://docs.riscv.org/) | Confirmed the official library entry point; earlier volume has its own snapshot |
| ASPEED SoCs | [AST2600](https://www.aspeedtech.com/server_ast2600/), [AST2620](https://www.aspeedtech.com/server_ast2620/), [AST2700](https://www.aspeedtech.com/server_ast2700/), [AST2720](https://www.aspeedtech.com/server_ast2720/), [AST2750](https://www.aspeedtech.com/server_ast2750/), [AST1700](https://www.aspeedtech.com/server_ast1700/), [AST2500](https://www.aspeedtech.com/server_ast2500/) | CPU, memory, interface and security claims in the ASPEED volume (marketing summaries, fetched 2026-10-22) |
| AST2600 device tree | [aspeed-g6.dtsi](https://github.com/torvalds/linux/blob/master/arch/arm/boot/dts/aspeed/aspeed-g6.dtsi), [aspeed-ast2600-evb.dts](https://github.com/torvalds/linux/blob/master/arch/arm/boot/dts/aspeed/aspeed-ast2600-evb.dts) | Peripheral base addresses and counts; read at `torvalds/linux` commit `7be4bc52fd9e0e55dc9a2e0232b89427d2c4b614` |
| AST2700 device tree | [aspeed-g7-a35.dtsi, soc0, soc1, ast2700-evb.dts](https://github.com/torvalds/linux/tree/master/arch/arm64/boot/dts/aspeed) | CPU complex, GICv3, bus domains, peripherals, reserved memory, interrupt ranges; same commit |
| Linux ASPEED bindings | [interrupt (INTC0/INTC1)](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/interrupt-controller/aspeed,ast2700-interrupt.yaml), [SBC](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/arm/aspeed/aspeed,sbc.yaml), [PCIe](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/pci/aspeed,ast2600-pcie.yaml), [USB 3](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/usb/aspeed,dwc3.yaml), [HACE](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/crypto/aspeed,ast2500-hace.yaml), [ACRY](https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/crypto/aspeed,ast2600-acry.yaml) | Processor names (PSP/SSP/TSP/BMCU), INTC structure, block descriptions |
| AST2700 boot | [U-Boot ibex-ast2700 doc](https://github.com/u-boot/u-boot/blob/master/doc/board/aspeed/ibex-ast2700.rst) | RISC-V boot MCU running SPL; `u-boot` commit `ece349ade2973e220f524ce59e59711cc919263f` |
| AST2600 secure boot | [AspeedTech-BMC/socsec](https://github.com/AspeedTech-BMC/socsec) | SPL signing, size limit, algorithms, rollback revision, OTP tools |
| OCP DC-SCM | DC-SCM Specification **Revision 2.1, Version 1.1** (PDF linked from [Antmicro's DC-SCM carrier README](https://github.com/antmicro/dc-scm-osm-l-carrier-card)) | Architecture, form factors, connector, signals, power, FRU, revision history. OWFa 1.0 |
| OCP LTPI | DC-SCM 2 LTPI Specification **Revision 1.2, Version 1.0 RC3** (PDF linked from the [LTPI IP User Guide](https://github.com/opencomputeproject/HWMgmt-Module-DCSCM-LTPI/blob/main/docs/LTPI_User_Guide.pdf)) | Frames, training, errors, latency, revision history. A release candidate copy |
| LTPI reference IP | [HWMgmt-Module-DCSCM-LTPI](https://github.com/opencomputeproject/HWMgmt-Module-DCSCM-LTPI) | Reference SystemVerilog, parameters, revision history. MIT code, CC BY 4.0 documents |

The current Intel README describes a Xeon-focused layer installed through [enterprise-ai-solutions](https://github.com/intel/enterprise-ai-solutions), not a standalone deployment of the old repository. This is a documentation observation, not a benchmark or an endorsement of its security and performance claims.

The NXP README contains dependency/version wording that should be checked against the actual recipes. The book deliberately does not copy every component URI or promise that arbitrary branch heads are mutually compatible.

## Authoritative further reading

- [UEFI specifications](https://uefi.org/specifications), including UEFI and PI; [TianoCore EDK II](https://github.com/tianocore/edk2) for an implementation.
- [Arm architecture documentation](https://developer.arm.com/documentation/), including the Arm Architecture Reference Manual, [SMCCC](https://developer.arm.com/documentation/den0028/latest/), and [PSCI](https://developer.arm.com/documentation/den0022/latest/).
- [PCI-SIG specifications](https://pcisig.com/specifications). Exact capability layouts, electrical behavior, FLIT details, and compliance requirements must come from the applicable specification.
- [DMTF PMCI](https://www.dmtf.org/standards/pmci): DSP0236 MCTP Base; DSP0237 SMBus/I2C binding; DSP0238 PCIe VDM binding; DSP0239 MCTP message types; DSP0240 PLDM Base; DSP0241 PLDM over MCTP; DSP0248 monitoring/control; DSP0257 FRU; DSP0267 firmware update.
- [DMTF Redfish](https://www.dmtf.org/standards/redfish) and [schema publication](https://redfish.dmtf.org/schemas/v1/).
- [OpenBMC interface definitions](https://github.com/openbmc/phosphor-dbus-interfaces), [entity-manager](https://github.com/openbmc/entity-manager), [dbus-sensors](https://github.com/openbmc/dbus-sensors), [bmcweb](https://github.com/openbmc/bmcweb), [libpldm](https://github.com/openbmc/libpldm).
- [Linux debugging guide](https://docs.kernel.org/process/debugging/index.html), [ftrace](https://docs.kernel.org/trace/ftrace.html), [KASAN](https://docs.kernel.org/dev-tools/kasan.html), [lockdep](https://docs.kernel.org/locking/lockdep-design.html), [kdump](https://docs.kernel.org/admin-guide/kdump/kdump.html).
- [Linux DMA API](https://docs.kernel.org/core-api/dma-api-howto.html), [hwmon](https://docs.kernel.org/hwmon/sysfs-interface.html), [MTD/UBI](https://docs.kernel.org/driver-api/mtd/ubi.html).
- [U-Boot documentation](https://docs.u-boot.org/en/latest/), [FIT](https://docs.u-boot.org/en/latest/usage/fit/index.html).
- [WG14 document index](https://www.open-std.org/jtc1/sc22/wg14/www/docs/), including the public [N1570 C11 committee draft](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf). A committee draft is not the published ISO C17 standard.

## Access and version limits

UEFI pages returned HTTP 403 during research. The Arm introductory page returned a JavaScript application shell rather than readable chapter content. N1570 was reachable as a PDF but was not text-parsed here. They remain further-reading references, not purported newly verified specification snapshots.

The Linux developer-tools index returned insufficient substantive text; the concrete debugging references above are provided for follow-up, not described as fully reviewed. Live `main`, `latest`, and release-branch links move. Record a commit or release when reproducing a build or implementing a protocol.

No latest-version claim is made for UEFI, PCIe, Arm features, or DMTF documents. Newer features are separated from the baseline where they affect behavior. Public project availability, successful deployment, and standards compliance are three different claims.

**ASPEED and DC-SCM volumes.** ASPEED's datasheets and programming guides are not public, so they were not used; the ASPEED volume is built from product pages, Linux and U-Boot sources, and ASPEED's public tools. opencompute.org specification pages returned HTTP 404 for the URLs tried, so the DC-SCM 2.1 and LTPI 1.2 PDFs were taken from the links published in OCP-related repositories. The DC-SCM **2.0** document itself was not read; the 2.0-to-2.1 comparison comes from the revision history inside the 2.1 document. The LTPI copy is a release candidate. Google Drive links to those PDFs can move or change. Check opencompute.org for the current revision. The kernel and U-Boot commits are recorded so address and interrupt tables can be re-checked.
