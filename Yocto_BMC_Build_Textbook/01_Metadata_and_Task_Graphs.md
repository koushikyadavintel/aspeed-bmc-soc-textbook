# 1. Metadata, Policy, and Task Graphs

## 1.1 Yocto is not a binary distribution

The Yocto Project provides tools, metadata, and practices for creating custom Linux distributions. OpenEmbedded supplies build metadata; BitBake parses metadata and executes a task graph. OpenBMC adds platform-management components and policy.

A layer is an organized metadata collection, not necessarily one software component. A recipe usually describes how to obtain, configure, build, and package software. An image recipe selects and assembles runtime contents. Classes share common task behavior.

## 1.2 The files that decide a build

| File/concept | Responsibility |
| --- | --- |
| `.bb` | Recipe: source, dependencies, tasks, package rules |
| `.bbappend` | Extends a matching recipe from an active layer |
| `.bbclass` | Reusable task/configuration behavior |
| `conf/layer.conf` | Layer identity, collections, search configuration |
| `conf/machine/*.conf` | Target hardware choices and tuning |
| Distro configuration | Distribution policy and selected features/providers |
| Image recipe | Packages/features included in the rootfs |
| `bblayers.conf` | Layers participating in this build |
| `local.conf` | Local build choices and overrides |

Cloning a repository does not activate its layer. BitBake must find it through configured paths and applicable metadata.

An append can change patches or package contents without changing the original recipe file. Therefore, "I read the `.bb`" is not always enough to know the effective build.

## 1.3 Build-time versus runtime dependencies

`DEPENDS` describes build dependencies such as libraries required in a recipe's sysroot. Runtime dependencies such as `RDEPENDS` describe packages needed on the installed system. A `-native` tool runs on the build host; the corresponding target package runs on the BMC.

For example, a code generator may run on the host to create C++ source. A target library is then linked into a BMC service. Both participate in the graph, but they have different architectures and installation destinations.

The same software can produce multiple binary packages: runtime, development headers, debug symbols, documentation, or plugins. Recipe names and package names need not match one-to-one.

## 1.4 A graph, not one linear shell script

The conceptual sequence is:

```text
fetch -> unpack -> patch -> configure -> compile -> install -> package
                                                      |
selected packages -> rootfs -> filesystem/image tasks -> deploy
```

Tasks from different recipes run concurrently when dependencies allow it. Image generation also depends on kernel, DTB, bootloader, native tools, and platform-specific packaging tasks.

`do_install` usually stages a recipe's files under a destination directory; it does not install them directly onto your workstation's `/usr`. Packaging classifies these staged files. Rootfs construction installs selected binary packages into an image tree.

## 1.5 Effective configuration and overrides

Machine, distro, layer priority, overrides, providers, versions, and appends jointly determine results. Syntax has evolved; examples using modern colon overrides are not automatically valid on older releases.

Useful inspection commands in an initialized environment include:

```sh
bitbake-layers show-layers
bitbake-layers show-recipes
bitbake-layers show-appends
bitbake -e obmc-phosphor-image
```

The last command can expose paths or credentials from a real environment. Inspect locally and redact before sharing.

## Worked example

A service builds successfully but is absent from the image.

**Reasoning:** compilation only proves that a task produced artifacts. Check the produced package, its file rules, runtime dependencies, and image/packagegroup selection. Then verify the installed rootfs and final image. A successful `do_compile` is not an image-composition test.

## Review

Why can editing a recipe in an unlisted layer have no effect?

**Answer:** the layer is outside `BBLAYERS`, so its metadata does not participate. Also check that the intended provider/version is selected and that no stronger effective override replaces the change.

Next: [From source to image](02_From_Source_to_Image.md).
