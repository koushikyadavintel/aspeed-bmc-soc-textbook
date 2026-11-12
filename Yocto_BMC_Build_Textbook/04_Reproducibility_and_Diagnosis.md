# 4. Reproducibility, Diagnosis, and Image Acceptance

## 4.1 Debug the first causal failure

BitBake can report many downstream failures after one missing dependency or failed task. Read the failing recipe/task and its `log.do_*` and `run.do_*` files in the work area. Paths vary by release and architecture.

Classify the failure:

1. Parse/provider problem: metadata and configuration.
2. Fetch problem: source URI, pinned revision, mirror, authorization.
3. Patch problem: baseline and patch compatibility.
4. Configure/compile problem: target options, dependencies, source.
5. Packaging/rootfs problem: file ownership, package selection, runtime requirements.
6. Image problem: layout, space, signing/tool configuration.
7. Runtime problem: the actual deployed artifacts and hardware.

Cleaning a recipe can force work, but it does not repair an incompatible patch. Clearing global caches can erase useful evidence and waste time.

## 4.2 What to record

A useful build identity includes:

- Repository commits for every active layer.
- Machine, distro, image target, release, and meaningful local configuration.
- Source revisions, patches, license metadata, and package/image manifests.
- Toolchain/build environment identity and applicable reproducibility settings.
- Output filenames and cryptographic digests.
- Signing-policy identifier, without private keys.

Reproducibility means more than "the branch had the same name." Floating source revisions, timestamps, download changes, or uncontrolled host input can affect results.

## 4.3 Trace a change into an image

For a changed sensor daemon:

```text
source commit -> selected recipe/provider -> actual task input
 -> compiled binary -> binary package -> image manifest
 -> rootfs file -> final artifact digest -> running identity
```

At each link, ask for evidence. A package manifest can establish inclusion, but not necessarily the exact runtime configuration. A correct flash operation can still boot the alternate slot.

When using stripped binaries, retain matching debug symbols in an approved artifact store. The symbols must match the compiled binary, not simply the repository branch.

## 4.4 Capstone

Build a supported public BSP on a suitable Linux host, or perform the metadata-only portion if hardware/build resources are unavailable.

1. Select compatible revisions and record them.
2. Explain each active layer's role.
3. Pick one real service recipe and locate source, dependencies, install rules, and packages.
4. Identify its image selection path.
5. Build or inspect the task graph and available logs.
6. Locate the final artifact and describe its consumer.
7. Write a private acceptance checklist before any deployment.

**Success criteria:** you can explain why the component is included, which architecture it targets, where its runtime files are installed, and why the chosen output is appropriate for the selected machine.

**Answer guide:** follow effective metadata rather than filenames alone; include appends and packagegroups; distinguish the service build from the image build. If no build was performed, label the result as metadata analysis, not a verified boot.

## 4.5 Common misconceptions

| Claim | Correction |
| --- | --- |
| "A package is a library." | A package can contain binaries, libraries, configuration, or data. |
| "Compiled means installed." | Installation and packaging are later tasks. |
| "Installed means enabled." | Unit enablement and runtime activation have separate policy. |
| "A new image means the BMC runs it." | Installation, boot selection, and activation must be verified. |
| "Every layer on disk is active." | Only configured and applicable metadata participates. |
| "A clean build proves reproducibility." | Repeatability requires controlled inputs and comparison. |

## Glossary

| Term | Meaning |
| --- | --- |
| BSP | Board-support metadata and software integration |
| Recipe | Metadata describing a software build/package |
| Sysroot | Dependency headers/libraries staged for a build context |
| Sstate | Reusable task output mechanism |
| Packagegroup | Metadata grouping runtime package selections |
| WIC | Tooling for partitioned image construction |
| Manifest | Record of image/package/source composition |
| Provider | Selected recipe satisfying a named capability |

Return to [contents](00_README.md) or continue to [Linux debugging](../Linux_Kernel_Debugging_Textbook/00_README.md).
