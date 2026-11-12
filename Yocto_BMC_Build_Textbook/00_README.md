# Yocto and BMC Image Construction

Understand the actual transformations between source code and a deployed BMC image.

| Chapter | Focus |
| --- | --- |
| [1. Metadata and task graphs](01_Metadata_and_Task_Graphs.md) | Layers, recipes, machine/distro/image policy, dependencies |
| [2. Source to image](02_From_Source_to_Image.md) | Cross-compilation, packaging, rootfs, filesystems, deploy artifacts |
| [3. Public BSP walkthrough](03_Public_BSP_Walkthrough.md) | NXP public commands, sourcing, BitBake, devtool |
| [4. Reproducibility and diagnosis](04_Reproducibility_and_Diagnosis.md) | Logs, signatures, manifests, validation, glossary |

**Prerequisites:** [C build stages](../C_Programming_Textbook/04_Interfaces_Builds_and_Review.md), basic Linux, [OpenBMC overview](../OpenBMC_Textbook/00_README.md).

Sources: [Yocto concepts](https://docs.yoctoproject.org/overview-manual/concepts.html), [development manual](https://docs.yoctoproject.org/dev-manual/), [NXP public BSP](https://github.com/nxp-imx-support/meta-nxp-openbmc/blob/walnascar/README.md).

Commands are for a supported Linux build host, not native Windows PowerShell. They explain a public workflow; no private platform recipe or release procedure is implied.
