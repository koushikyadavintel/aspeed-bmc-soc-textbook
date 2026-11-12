# Yocto for BMC Engineers: Team Presentation (60 min)

**Audience:** BMC team, already familiar with Yocto/OpenBMC basics. **Angle:** fundamentals recapped quickly, then how they map to OpenBMC images and BMC bring-up.
**Format:** slide outline with on-slide bullets (what goes on the slide) and speaker notes (what you say). 30 slides.
**Flow and diagrams:** for a pipeline-ordered, in-depth version of this talk (master map, per-stage Mermaid diagrams, one running example), see [How Yocto works, end to end](Yocto_How_It_Works_Flow.md).

> Items tagged **[verify]** are details I could not confirm from a primary source. Check them against your own tree (`meta-phosphor`, your machine layer) before presenting. Commands are for a Linux build host.

## Timing plan

| Part | Slides | Min |
| --- | --- | --- |
| 0. Opening | 1-2 | 2 |
| A. Why Yocto for a BMC | 3-4 | 4 |
| B. Concepts that matter (fast recap) | 5-9 | 9 |
| C. Build flow and configuration | 10-14 | 9 |
| D. How OpenBMC maps onto Yocto | 15-20 | 12 |
| E. Boot chain: reference boards to BMC SoC | 21-22 | 5 |
| F. Releases and layer compatibility | 23-24 | 4 |
| G. Debugging and reproducibility | 25-27 | 6 |
| H. Demo | 28 | 5 |
| I. Takeaways and Q&A | 29-30 | 4 |
| **Total** | | **60** |

Cut list if you run long: slide 9, slide 22, slide 24. Demo is optional if time is tight; keep the screenshots on slide 28 as a fallback.

---

## Part 0: Opening (2 min)

### Slide 1: Title
**On slide:** "Yocto for BMC Engineers: from recipe to flash image." Your name, date.

**Notes:** One sentence on why you're presenting: you worked through Yocto from first principles (Poky, BitBake, layers, BSPs on BeagleBone and Raspberry Pi) and want to share what carries over to our OpenBMC work.

### Slide 2: Agenda and goal
**On slide:**
- Goal: after this talk, you can trace any file on the BMC back to a recipe, layer and task.
- Agenda: concepts, build flow, OpenBMC mapping, boot chain, releases, debugging, demo.

**Notes:** Set the frame: "When something is wrong on the BMC, the question is always *which layer/recipe put it there, and which variable controls it*." Everything today supports that.

---

## Part A: Why Yocto for a BMC (4 min)

### Slide 3: A BMC image is a custom distro
**On slide:**
- Four elements: toolchain, bootloader, kernel, rootfs (plus the application layer).
- BMC extra: it also has to be updateable, recoverable and secure.
- Yocto = tools and metadata to build *your own* distro, not a distro itself.

**Notes:** Explain the four elements briefly. A BMC is a tiny constrained system (SPI-NOR is often 32-128 MB), so a general-purpose distro does not fit and cannot be controlled tightly. Yocto builds exactly what we list.

### Slide 4: What Yocto buys us
**On slide:**
- Reproducible builds from pinned metadata.
- Layering: SoC vendor, platform, our product kept separate.
- One cross-compile environment for U-Boot, kernel, daemons, rootfs.
- Package-level license and CVE tracking (SBOM).

**Notes:** Tie each point to a BMC pain: "AST2600 vs AST2700 vs NXP: same OpenBMC core, different layers." Mention that the reuse is what lets us carry upstream OpenBMC improvements.

---

## Part B: Concepts that matter (9 min)

### Slide 5: The vocabulary (get this right once)
**On slide:**

| Term | Meaning |
| --- | --- |
| Yocto Project | The organization/umbrella |
| Poky | Reference distro (BitBake + oe-core + demo BSPs) |
| OpenEmbedded / oe-core | Shared core metadata (`meta/`) |
| BitBake | Task engine |
| Metadata | `.conf`, `.bb`, `.bbappend`, `.bbclass`, `.inc` |

**Notes:** Use the Ubuntu analogy: Yocto is like "Canonical", Poky is like "Ubuntu". **OpenBMC is not built from Poky as-is**: it is its own distro (`openbmc-phosphor`, from `meta-phosphor`) built on top of oe-core and BitBake. [verify the DISTRO name in your tree: `bitbake -e | grep ^DISTRO=`]

### Slide 6: BitBake in one slide
**On slide:**
- Parses metadata, builds a **task graph**, runs tasks in parallel.
- Task chain per recipe: `fetch -> unpack -> patch -> configure -> compile -> install -> package -> (rootfs/image)`.
- Shared state (sstate) skips tasks whose inputs did not change.

**Notes:** It is a graph, not a shell script. Two ideas to emphasise: (1) each task has a **signature** computed from its inputs, and (2) the sstate cache is how second builds are fast. See the [textbook chapter on task graphs](Yocto_BMC_Build_Textbook/01_Metadata_and_Task_Graphs.md).

### Slide 7: Recipes, classes, layers
**On slide:**
- Recipe `name_version.bb`: source, patches, build, install, license.
- `.bbappend`: modify a recipe **without** forking it.
- `.bbclass`: shared logic (`inherit cmake`, `systemd`, `meson`).
- Layer `meta-<name>`: a folder of related metadata with `conf/layer.conf`.

**Notes:** In OpenBMC nearly all customisation is a `.bbappend` in your platform layer. A recipe produces **many packages** (`foo`, `foo-dev`, `foo-dbg`), controlled by `PACKAGES`.

### Slide 8: Machine vs distro vs image
**On slide:**
- **Machine** (`MACHINE`): hardware (SoC, kernel, U-Boot, flash size, device tree).
- **Distro** (`DISTRO`): policy (init system, features, package format).
- **Image**: what goes in the rootfs (`obmc-phosphor-image`).

**Notes:** The three are independent knobs. A common mistake is putting machine-specific package lists in the image or distro. "Which of the three does this change belong to?" is the review question.

### Slide 9: The files you touch every day
**On slide:**
- `conf/bblayers.conf`: which layers (`bitbake-layers show-layers`).
- `conf/local.conf`: per-user scratch. **Not** source-controlled.
- Variables to know: `MACHINE`, `DL_DIR`, `SSTATE_DIR`, `TMPDIR`, `BB_NUMBER_THREADS`, `PARALLEL_MAKE`.
- Operators: `=`, `?=`, `??=`, `+=`, `:append`, `:prepend`.

**Notes:** Anything permanent belongs in a layer, not `local.conf`. Mention the precedence trap: `?=` (weak default) beats `??=` (weaker default), which is why uncommenting `MACHINE ?=` overrides the sample's `MACHINE ??=`. Inspect any final value with `bitbake -e <target> | grep ^VAR=`.

> **Syntax update from older training material:** use `IMAGE_INSTALL:append = " pkg"`. The old `_append` form was replaced by colon overrides in Yocto 3.4 (Honister). The leading space is required. In OpenBMC prefer `OBMC_IMAGE_EXTRA_INSTALL:append = " pkg"` for extra packages. [verify in your tree]

---

## Part C: Build flow and configuration (9 min)

### Slide 10: Host requirements, then and now
**On slide:**
- Disk **>= 140 GB**, RAM **>= 32 GB** recommended (older material says 50 GB).
- Git >= 2.22, tar >= 1.28, Python >= 3.9, gcc >= 10.1, make >= 4.0.
- Supported: Ubuntu 22.04/24.04/26.04, Debian 11-13, AlmaLinux/Rocky 8-10, Fedora, openSUSE Leap.
- Windows: WSL2 or container (not officially validated).

**Notes:** Old notes mention CentOS and Python 3.4: outdated. Give the team the current numbers. Point to the Yocto reference manual's *System Requirements* page. Build servers and CI containers should be sized against these.

### Slide 11: First build, step by step
**On slide:**
```sh
git clone https://github.com/openbmc/openbmc.git
cd openbmc
. setup <machine>              # sources env, creates build/, selects config
bitbake obmc-phosphor-image
```
- Generic Poky equivalent: `source oe-init-build-env`, then `bitbake core-image-minimal`.
- Current Yocto quick-start tool: `bitbake-setup` (newer, optional).

**Notes:** `. setup` is **sourced**, not executed. Otherwise it can't set your shell's environment. This is why a fresh terminal says `bitbake: command not found`. See [the walkthrough chapter](Yocto_BMC_Build_Textbook/03_Public_BSP_Walkthrough.md). `git://` URLs are old; use `https://`. Pick a branch supported today, not an end-of-life one.

### Slide 12: What a build produces
**On slide:**
- `tmp/deploy/images/<machine>/`
- Kernel image, rootfs/filesystem images, modules, bootloader pieces.
- Controlled by `KERNEL_IMAGETYPE`, `IMAGE_FSTYPES`.
- `tmp/work/...`: per-recipe work dirs and logs; `sstate-cache/`; `downloads/`.

**Notes:** Teach the team where to look first: deploy dir for artifacts, `tmp/work/<arch>/<recipe>/<ver>/temp/log.do_*` for failures.

### Slide 13: Disk and speed tips
**On slide:**
- `INHERIT += "rm_work"` saves disk; costs debuggability (`RM_WORK_EXCLUDE` for recipes you debug).
- Shared `DL_DIR` and sstate mirror for the team and CI.
- `BB_NUMBER_THREADS` (BitBake tasks) vs `PARALLEL_MAKE` (`make -j` inside a task).

**Notes:** Don't confuse the two threading variables. In CI, set up an sstate mirror (`SSTATE_MIRRORS`) and a hash-equivalence server so unchanged work isn't rebuilt. [verify what our CI already uses]

### Slide 14: Packaging formats and rootfs
**On slide:**
- ipk (small), deb, rpm: chosen by `PACKAGE_CLASSES`.
- Runtime package management is usually **off** on a BMC.
- Rootfs assembled from the package feed, then turned into an image.

**Notes:** Answer the question from the notes: ipk/deb/rpm are just package formats. On a BMC we usually ship a fixed image and update it as a whole, so we don't need a package manager on the target.

---

## Part D: How OpenBMC maps onto Yocto (12 min)

### Slide 15: OpenBMC is a layer stack
**On slide:**
```
meta-<company>/meta-<platform>   <- our machine and product changes
meta-<soc vendor> (aspeed, nuvoton, ...)   <- SoC support
meta-phosphor                    <- OpenBMC distro, services
meta-oe / meta-python / meta-networking    <- meta-openembedded
meta (oe-core) + BitBake
```
**Notes:** Name real examples from your tree (`bitbake-layers show-layers`). The idea: lower layers are upstream, top layers are ours. We want our delta to be small and to live only in the top layers. [verify exact layer names in the tree you present]

### Slide 16: A machine definition
**On slide:** `meta-<platform>/conf/machine/<machine>.conf` typically sets:
- SoC include (for example an AST2600 `.inc`).
- `KERNEL_DEVICETREE`, `UBOOT_MACHINE`, flash layout/size.
- `OBMC_MACHINE`, preferred providers for virtual packages.

**Notes:** This is where "what hardware is this" is encoded. A change of flash size or device tree starts here. Show a real file from your tree. [verify variable names]

### Slide 17: The image recipe
**On slide:**
- `obmc-phosphor-image`: top-level image, hardware-independent.
- Features and package sets added from machine/layer config.
- Debug/dev features exist; **do not** ship them in a production image.

**Notes:** Authentication-weakening development settings (empty root password, root login) are image features. In newer Yocto they were split into finer-grained features. Production vs debug images should be separate, deliberate choices.

### Slide 18: The OpenBMC services in recipe terms
**On slide:**
- Each daemon is a recipe: `bmcweb` (Redfish), `phosphor-state-manager`, `dbus-sensors`, `entity-manager`, `phosphor-hwmon`, `phosphor-ipmi-host`...
- Interfaces from `phosphor-dbus-interfaces`, bindings via `sdbusplus`.
- Packages end up as systemd services pulled into the image.

**Notes:** Connect to the [OpenBMC textbook](OpenBMC_Textbook/02_DBus_Sensors_and_Redfish.md). Key message: **a service on the BMC is there because a recipe installs it and an image/feature pulls it in.** To remove one, change what pulls it in, not the rootfs by hand.

### Slide 19: Customising without forking
**On slide:**
- `.bbappend` in your layer: patches, config, extra `SRC_URI`.
- Pin sources: `SRCREV` to a commit, not a moving branch.
- Work on one component: `devtool modify <recipe>` -> `devtool build` -> `devtool finish`.

**Notes:** `devtool reset` removes the workspace override but does not export your work; `devtool finish` does. Show the diff generated. Mention `bitbake-layers show-appends` to see who modifies a recipe. See [textbook section 3.4](Yocto_BMC_Build_Textbook/03_Public_BSP_Walkthrough.md).

### Slide 20: From build to flash image
**On slide:**
- Typical OpenBMC outputs (SPI-NOR static layout): full flash image, plus pieces such as u-boot, kernel (FIT), read-only rootfs, read-write overlay, and an update tarball. [verify names for your machine]
- A build is **not** a flash instruction: verify target identity, layout, signing, recovery first.
- A/B, signing and rollback are update policy, not something Yocto gives automatically.

**Notes:** Link to the [flash images chapter](OpenBMC_Textbook/03_Flash_Images_and_Updates.md). Repeat the point: "Same-size capsule and flash dump are **not** interchangeable." Never demo a write to real hardware.

---

## Part E: Boot chain, from reference boards to a BMC SoC (5 min)

### Slide 21: What the BeagleBone and Raspberry Pi labs taught
**On slide:**

| Board | Boot chain |
| --- | --- |
| BeagleBone Black (AM335x) | ROM -> SPL (`MLO`) -> U-Boot -> Linux |
| Raspberry Pi 3 | GPU ROM -> `bootcode.bin` -> `start.elf` -> kernel (Pi 4/5 use EEPROM) |
| BMC SoC (for example AST2600) | BootROM -> SPL -> U-Boot -> FIT kernel/DTB -> rootfs |

**Notes:** The BBB lab is the cleanest model for staged boot: tiny on-chip RAM forces an SPL stage that initialises DRAM. BMC SoCs follow the same pattern, differing in where the images live (SPI-NOR) and in the secure-boot hooks. Bring this together with the [ASPEED textbook](ASPEED_BMC_SoC_Textbook/04_Boot_Security_and_Software.md).

### Slide 22: Reference BSP vs vendor BSP
**On slide:**
- `meta-yocto-bsp`: minimal reference boards, mainline kernel and U-Boot.
- Vendor BSP (`meta-ti`, `meta-raspberrypi`, SoC-vendor BMC layers): full features, vendor kernel.
- Pick the vendor layer for real products; keep your delta in a separate layer.

**Notes:** Same decision applies to us: SoC-vendor layers carry drivers; our platform layer should only add board specifics. Warn: machine lists in these layers change between releases, so check `conf/machine/*.conf` on the branch you use.

---

## Part F: Releases and layer compatibility (4 min)

### Slide 23: Release model (verified Oct 2026)
**On slide:**
- Major release every 6 months (April and October); each has a codename.
- Stable: ~7 months. **LTS: 4 years** (older material says 2).
- Current: **6.1 "Blacksail"** (Oct 2026). LTS: **Scarthgap 5.0 (to Apr 2028)**, **Wrynose 6.0 (to Apr 2030)**.
- EOL examples: Zeus, Dunfell, Kirkstone.

**Notes:** Source: Yocto releases page; re-check the date before presenting since this changes every six months. Ask the room: "Which release does our OpenBMC tree sit on, and when does it lose support?" That is a useful discussion starter.

### Slide 24: Don't mix branches
**On slide:**
- Layers on different releases fail or misbehave (`.bbappend` tied to exact versions).
- Layers declare compatibility with `LAYERSERIES_COMPAT_<layer>`.
- Choose a branch every layer you need supports, and your host distro supports.

**Notes:** Upgrades are a project, not a task: plan them, and keep platform deltas small so they are cheap.

---

## Part G: Debugging and reproducibility (6 min)

### Slide 25: Debug the first failure
**On slide:**
- Read the first error in `log.do_<task>` under `tmp/work/.../temp/`, not the last line of BitBake output.
- `bitbake -c <task> <recipe>` to rerun one task. `-k` to keep going.
- `bitbake -c devshell <recipe>` for an interactive build environment.

**Notes:** Most "mystery" failures are an early task failing, then dependents cascading. Teach the team to find the first cause.

### Slide 26: Answer "why is this here / why did it change?"
**On slide:**
- `bitbake -e <target> | grep ^VAR=`: final value and where it came from.
- `bitbake-layers show-layers / show-recipes / show-appends`.
- `bitbake -g <target>`: dependency graph.
- `bitbake-diffsigs`: why a task re-ran.
- `oe-pkgdata-util`, image `.manifest`: which package provides which file.

**Notes:** Show one concrete example from our tree rather than a generic one. See [diagnosis chapter](Yocto_BMC_Build_Textbook/04_Reproducibility_and_Diagnosis.md).

### Slide 27: Release hygiene
**On slide:**
- Record: layer commit IDs, `MACHINE`, `DISTRO`, `local.conf` deltas, build host, image hashes.
- Keep manifests, license output, SPDX/SBOM and CVE-check results with the release.
- Pin with a manifest tool (`repo`, `kas`, `bitbake-setup`) so a build can be redone.

**Notes:** Reproducibility is a process: if you can't list the exact layer revisions, you can't rebuild or audit the image. Don't store secrets (keys, certificates) in layers or public repos.

---

## Part H: Demo (5 min)

### Slide 28: Live demo (pick one)
**Option 1: trace a package into the image (safest, no hardware).** On a pre-built tree:
```sh
bitbake -e obmc-phosphor-image | grep ^MACHINE=
bitbake-layers show-layers
bitbake-layers show-appends bmcweb
ls tmp/deploy/images/<machine>/
```
Say: "Here is the machine, here are the layers, here is who modifies `bmcweb`, here is what we produced."

**Option 2: run an OpenBMC image in QEMU.** Follow the QEMU instructions in the OpenBMC documentation for an existing QEMU machine (for example `romulus-bmc`). [verify the exact command against the current OpenBMC README]. Show login, a `redfishcli`/`curl` Redfish query, and `busctl tree`.

**Fallback:** keep screenshots of each step in the slide.

**Notes:** Pre-build everything beforehand; a full build takes hours. Do **not** run flash/erase commands live.

---

## Part I: Takeaways and Q&A (4 min)

### Slide 29: Five takeaways
1. A BMC image is a custom distro: **machine + distro + image + layers**.
2. Every file on the target traces to a recipe, a task and a layer.
3. Keep our delta in **`.bbappend`s in our own layer**; pin everything.
4. Use a **supported release**, and don't mix branches.
5. Debug the **first** failure, and use `bitbake -e` and `bitbake-layers` to answer "why".

### Slide 30: Q&A and follow-up
**On slide:** Links to the repo textbooks: [Yocto build textbook](Yocto_BMC_Build_Textbook/00_README.md), [OpenBMC textbook](OpenBMC_Textbook/00_README.md), [ASPEED SoC textbook](ASPEED_BMC_SoC_Textbook/00_README.md).

---

## Likely questions (prepare short answers)

| Question | Short answer |
| --- | --- |
| Poky vs Yocto? | Yocto is the project; Poky is the reference distro. OpenBMC uses its own distro. |
| Why not just edit `local.conf`? | It's untracked. Put changes in a layer so they are reviewable and reproducible. |
| Why did a rebuild take hours? | Signature changed (config, `SRCREV`, host tool) so sstate didn't match. Use `bitbake-diffsigs`. |
| How do I add a package to the image? | `OBMC_IMAGE_EXTRA_INSTALL:append = " pkg"` (or `IMAGE_INSTALL:append`) from a layer. [verify] |
| Which Yocto release are we on? | Check `LAYERSERIES_CORENAMES`/`LAYERSERIES_COMPAT` in the layers and the Yocto releases page. |
| Can I flash the image the build produced? | Only after confirming layout, signing, and recovery for that exact board. |
| Where is the old `rpi-sdimg`? | Gone: meta-raspberrypi now produces `.wic` images. |

## Corrections to older training material (for a one-slide appendix)

| Older notes say | Now |
| --- | --- |
| Branch `zeus` | EOL; use an LTS such as Scarthgap or Wrynose |
| `IMAGE_INSTALL_append` | `IMAGE_INSTALL:append` |
| `TMP_DIR` | The variable is `TMPDIR` |
| `git://` URLs | `https://` |
| 50 GB, Python 3.4 | 140 GB, 32 GB RAM, Python >= 3.9 |
| LTS = 2 years | LTS = 4 years |
| `.rpi-sdimg` | `.wic` / `.wic.bz2` |
| Quit QEMU with Ctrl-C | In `-nographic`, `Ctrl-A` then `X` |

## Cheat sheet handout (one page)

```sh
# Environment and build
. setup <machine>                       # OpenBMC; or: source oe-init-build-env
bitbake obmc-phosphor-image

# Inspect
bitbake -e <target> | grep ^MACHINE=
bitbake-layers show-layers
bitbake-layers show-appends <recipe>
bitbake -g <target>                     # dependency graph
bitbake -c listtasks <recipe>

# Debug
bitbake -c cleansstate <recipe>
bitbake -c devshell <recipe>
bitbake-diffsigs <sigfile1> <sigfile2>

# Component work
devtool modify <recipe>
devtool build <recipe>
devtool finish <recipe> <layer>
```

## Before you present

- [ ] Verify the **[verify]** items against your own tree.
- [ ] Re-check the release table (slide 23) against the Yocto releases page.
- [ ] Pre-build the image for the demo; capture fallback screenshots.
- [ ] Replace placeholder layer and machine names with ones from our real tree. Remove anything internal or confidential if the deck will be shared outside the team.
- [ ] Rehearse once with a timer; cut per the cut list if over 60 min.

## Sources

- Yocto Project releases: https://wiki.yoctoproject.org/wiki/Releases
- System requirements: https://docs.yoctoproject.org/ref-manual/system-requirements.html
- Quick build: https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html
- Overview and concepts: https://docs.yoctoproject.org/overview-manual/concepts.html
- OpenBMC: https://github.com/openbmc/openbmc
- Repo textbooks linked above.
