# 3. A Public BSP Walkthrough and Component Development

## 3.1 Scope and baseline

The public [NXP walnascar README](https://github.com/nxp-imx-support/meta-nxp-openbmc/blob/walnascar/README.md) describes a BSP layer, machine setup, and `obmc-phosphor-image`. It is an illustrative, board-specific workflow, not a promise that a generic BMC accepts the result.

Before building, choose mutually compatible, documented revisions. The commands below explicitly check out the named branch in both source repositories; for a reproducible release, record and pin the resulting commit IDs.

```sh
git clone --branch walnascar https://github.com/openbmc/openbmc.git
cd openbmc
git clone --branch walnascar \
  https://github.com/nxp-imx-support/meta-nxp-openbmc.git meta-nxp
. setup evb-imx93
bitbake obmc-phosphor-image
```

A branch may move or cease to be available. If compatibility requirements change, follow the checked public BSP documentation rather than substituting unrelated branches.

## 3.2 What each command changes

`git clone` creates a working tree and Git metadata for the selected public repository. It does not compile anything. `cd` changes the shell's directory.

The second clone places the BSP in the expected source-tree location. Its layer metadata supplies machine choices and recipes/appends for that hardware.

`. setup evb-imx93` sources the setup script in the **current shell**. This lets it update environment variables and working directory, select configuration, and make BitBake tools available. Running an initialization script in a child shell cannot permanently change the parent shell's environment.

Inspect the resulting `conf/bblayers.conf`, `conf/local.conf`, and setup output. A preexisting build directory may retain earlier choices; setup is not proof that every old option was reset.

`bitbake obmc-phosphor-image` asks for a target graph. BitBake parses effective metadata, selects providers, schedules prerequisites, restores applicable cached work, and executes remaining tasks.

The public README identifies WIC output under `tmp/deploy/images/<board_name>`. Actual filenames and additional artifacts depend on recipes. Verify that directory after the build instead of assuming one fixed extension.

## 3.3 Templates and layers

Other OpenEmbedded workflows use `TEMPLATECONF` and `oe-init-build-env`. A template supplies initial configuration; it is not a runtime setting on the target.

Adding a layer registers metadata:

```text
bitbake-layers add-layer /absolute/path/to/your-public-layer
```

Use an actual layer directory with `conf/layer.conf`. Do not invent private layers to make a public BSP example appear complete.

Development image settings can weaken authentication or expose debugging facilities. Do not enable them by default in a publishable or production build. Select only the supported, authorized debug configuration your lab requires.

## 3.4 Working on one recipe with devtool

After choosing an actual recipe:

```text
devtool modify <recipe>
devtool build <recipe>
bitbake obmc-phosphor-image
```

`modify` prepares editable source and workspace metadata so the build uses it. `build` targets the component. Rebuilding the image integrates the package into new deployable artifacts.

Before ending the session, commit or otherwise preserve changes and use `devtool finish` to export the intended recipe/patch changes into an appropriate layer, following the release's workflow. Inspect the generated diff.

`devtool reset <recipe>` removes the workspace override; it is not an export or a substitute for preserving work. Check your release's behavior before cleanup.

## 3.5 A build is not a flash instruction

The BSP's selected machine can produce a bootable artifact for that board. It does not establish that the image is accepted by another board's updater or that a capsule/raw-image conversion is valid.

Verify target identity, layout, signing requirements, and recovery on supported equipment. This chapter stops before destructive deployment.

## Exercise

Open a fresh terminal and run `bitbake`, which is now missing.

**Answer:** environment initialization was local to the previous shell. Source the project's setup in the new shell and verify the intended build directory/configuration; do not copy arbitrary PATH fragments until you know which checkout they belong to.

Next: [Reproducibility and diagnosis](04_Reproducibility_and_Diagnosis.md).
