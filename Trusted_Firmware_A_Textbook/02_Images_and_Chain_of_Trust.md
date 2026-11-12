# 2. Image Packaging and Chain of Trust

## 2.1 A container is not authorization

A Firmware Image Package (FIP) packages images with identifiers and a table of contents. The loader can locate components by their defined identities.

Packaging alone does not authenticate the contents. A maliciously replaced FIP can still be structurally valid. Cryptographic authentication requires a configured chain rooted in a trusted key or equivalent hardware policy.

The same distinction appears in [BMC updates](../OpenBMC_Textbook/03_Flash_Images_and_Updates.md): a parser accepting a format is not proof that the firmware is authorized.

## 2.2 A chain needs a root

Conceptually:

```text
immutable trust anchor
 -> trusted verification code/key
 -> authenticated certificates/metadata
 -> authenticated executable components
 -> authenticated handoff
```

What is checked, which key is authoritative, and where the anchor resides are platform decisions governed by the boot architecture. Storing an unsigned replacement public key beside an image does not create a root of trust.

TF-A can integrate authentication infrastructure and Trusted Board Boot flows. The build configuration and port determine which features are actually enabled.

## 2.3 Corruption, authenticity, and rollback

- A checksum or unkeyed hash can detect accidental corruption relative to a trusted expected value.
- A signature can establish authorization under a trusted key and policy.
- Rollback protection prevents accepting an older but otherwise valid signed image when policy forbids it.
- Compatibility checks establish that the image belongs to the target and component set.

These are different properties. An old vulnerable image can carry a valid signature. A correctly signed image for another board can still be incompatible.

Rollback state must live in storage with suitable trust, atomicity, endurance, and recovery semantics. Incrementing a version field in an untrusted package does not establish a monotonic platform policy.

## 2.4 Measured boot

Measured boot records what was loaded into protected measurement state or logs suitable for later verification. Verified boot decides whether loading/execution is permitted.

A system can implement one, both, or neither. A measurement log is meaningful only in conjunction with its root of trust and a verifier's expectations; a text log on writable storage is not automatically trustworthy attestation evidence.

## 2.5 Loading and memory safety

Authentication must not obscure parser and loader safety. Check image size, destination ranges, overlap, arithmetic overflow, alignment, and metadata consistency. An authorized but malformed input still needs safe handling.

Trust also spans non-code configuration: memory maps, device assignments, secure/non-secure attribution, and boot arguments can affect the eventual security boundary.

Do not expose private signing keys in source trees, shell logs, build artifacts, or public repositories. Development/test keys must not be mistaken for production credentials.

## Lab: inspect without flashing

Using TF-A tools from a controlled checkout:

```sh
fiptool info fip.bin
sha256sum fip.bin
```

The tool must already be built and available. Compare component identities and sizes against the intended build configuration.

**Expected conclusion:** a structural inventory and digest, not a claim that signatures are valid. Use the platform's actual verification chain and policy to establish authorization.

## Review

Can an attacker replace both an image and its adjacent SHA-256 file?

**Answer:** yes, unless the expected digest or its signature is anchored in trusted state. Matching two attacker-controlled files is not secure boot.

Next: [Runtime services and PSCI](03_Runtime_Services_and_PSCI.md).
