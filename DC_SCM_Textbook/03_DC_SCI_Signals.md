# 3. DC-SCI Signals

The DC-SCI carries a lot of different interfaces over one connector. This chapter groups them by family and records the rules the specification attaches to each. The connector's pin regions are in [Chapter 2](02_Mechanical_and_Connector.md).

## 3.1 The big picture

| Family | Single node | Dual node | Voltage / speed |
| --- | --- | --- | --- |
| PCIe HPM to SCM | x1 + x1 + x4 | per-node x1 pairs | Gen2 typical, up to Gen5 |
| USB | 2.0 and 3.1 options | per-node USB | see 3.3 |
| eSPI | one bus (CS0 + optional CS1) | two buses | no LPC support |
| SPI / QSPI | QSPI_HPMCNTRL, SPI_HPMCNTRL_TPM, SPI_SCMCNTRL | two QSPI, two TPM SPI | |
| NC-SI RBT | up to 2 | up to 2, one per node possible | 50 MHz RMII-based |
| I2C / I3C | 18 ports (10 × 3.3 V, 8 × 1.8 V) | 6 × 3.3 V + 3 × 1.8 V | I3C Basic v1.1.1 |
| FSI | alternate on 1.0 V I2C/I3C pins | same | 1.2 V FSI |
| UART | 2, 3.3 V | 2 | no flow control |
| PECI | optional | per node | see 3.5 |
| JTAG | BMC-initiator | | IEEE 1149.1 |
| SGPIO | per DC-MHS M-PIC | | 3.3 V |
| LTPI | 4 LVDS links, 8 pins | same | [Chapter 5](05_LTPI.md) |

## 3.2 PCIe

**Lanes.** The DC-SCI supports several PCIe options between the HPM and the SCM.

- **x1, typically Gen2, up to Gen5** (pins A30-B31): usually a BMC PCIe **endpoint** for video, MCTP over PCIe VDM, memory-mapped devices and/or a USB controller.
- **x1, typically Gen2, up to Gen5** (A65-B66): usually a USB host controller, because some hosts no longer provide native USB host functions.
- **x4, up to Gen5** (OA2-OB12): lets the HPM talk to endpoints on or behind the SCM. The link can be split as 1×x4, 2×x2, 4×x1 or 2×x1 + x2; multi-node HPMs may split upstream ports per node.
- **SCM to HPM** (A33-B34): three mutually exclusive uses: BMC as a PCIe root complex, a host-domain x1 passed from a PCIe switch back into the HPM, or USB 3.1.

**Clocks.** Two HPM-provided reference clocks, `PCIE_HPM_SCM_CLK_100M_0` and `_1`. Typically the first feeds the x4 endpoint (for example a Gen5-capable one) and the second, through a clock buffer, feeds slower devices such as the BMC and a USB host controller. All host endpoints on the SCM are expected to share one clocking domain; otherwise separate reference-clock methods may be needed.

**Resets.** One PCIe reset per node from HPM to SCM for the host domain (`PERST`). Timing and per-endpoint resets are out of scope. Pin B51 can optionally carry a BMC root-complex PERST#; otherwise the BMC's PERST can be sent as a virtual wire over LTPI.

**Why this matters to a BMC.** The BMC's host-facing VGA and MCTP-over-PCIe-VDM both go through the first x1. A PCIe link that does not train looks, from the host, like a missing VGA device and missing management endpoints. See the [PCIe textbook](../PCIe_Textbook/00_README.md) for diagnosing link training.

## 3.3 USB

- **Host USB.** Because some chipsets lack native USB host controllers, the specification suggests a **PCIe x1 to USB host controller on the SCM**, reaching BMC, internal and external ports. Alternatively, `USBx_SCMHOST` buses can join the host domain; take care with cross-power-domain connections since the same pins can be used in the S5 AUX or S0 main domains.
- **Legacy.** Two optional HPM-to-SCM **USB 2.0** interfaces exist for hosts that keep USB 2.0 host controllers. **No USB 3.2 Gen1 HPM_SCM interfaces** are provided in DC-SCI 2.
- **Managed USB.** `USB2_SCM_HPM` for a BMC-managed high-speed management interface; `USB2_BMC_SCMOTG` where the BMC can be host or device (On-The-Go), typically a front "service port"; `USB3_SCMROOT_SCM_HPM` for future BMCs.
- **AC-coupling rule.** For USB 3.x TX lanes from SCM to HPM, the AC capacitors defined by the USB spec go on the DC-SCM. If the bus ends on the HPM (device or hub), the capacitors for the HPM-to-SCM direction go on the HPM; if it goes to an HPM USB connector, the attached device holds them.

## 3.4 SPI, QSPI and TPM

Single node has three SPI-family interfaces.

| Signal group | Initiator | Purpose |
| --- | --- | --- |
| `QSPI_HPMCNTRL` | HPM | host access to BIOS flash on the SCM. One QSPI in single node, two in dual node |
| `SPI_HPMCTRL_TPM` | HPM | dedicated TPM SPI for hosts that want one. Other hosts use a dedicated chip select on QSPI, leaving the other SPI pins for alternates such as `I2C_I3C_1V8` |
| `SPI_SCMCNTRL` | SCM | BMC access to expansion devices on the HPM such as the HPM FPGA (attestation, recovery, update) |

Only one discrete interrupt, `SPI_HPM_SCM_IRQ0_N`, exists (as in DC-SCM 1.0); any other interrupts go over LTPI. In **dual node** the 2.1 revision added two SPI interfaces as the *primary* way to attach TPMs on the SCM; the alternative is QSPI with a dedicated TPM chip select.

## 3.5 NC-SI

The DC-SCI carries up to two RMII-based Transport (RBT) NC-SI interfaces from the SCM to the HPM, for a high-speed sideband to NICs. Use the first (B43-B49) if you only need one. Two may serve redundancy, signal integrity or one per node. The RMII `RXERR` signal was removed in 2.0 because it is optional and its pin was more valuable for alternate functions.

**Timing assumptions.** The 50 MHz ±100 ppm clock source is assumed to be on the HPM. Traces are 50 Ω ±15% controlled-impedance nets. The budget:

| Parameter | Value |
| --- | --- |
| Total propagation delay BMC to target ASIC (`TPD,Budget`) | 3000 ps |
| BMC to DC-SCM connector (`TBMC_DATA`, on the SCM PCB) | 680 ps |
| Delay through the DC-SCI connector (`TDC-SCI`, typical) | 110 ps |
| Max reference-clock skew between devices (`TSKEW[max]`) | 1.5 ns |

The data rule is `TBMC_DATA + TDC-SCI + TSCM-NIC < TPD,Budget`. So everything *after* the connector (HPM trace plus the OCP NIC board) has to fit in what is left: 3000 − 680 − 110 = **2210 ps**. Reducing the actual skew improves the end-to-end budget.

## 3.6 eSPI

Single-node configurations provide **one** HPM-to-SCM eSPI bus, including `CS1/ALERT1`, although the typical case is to terminate `CS1/ALERT1` at the HPM FPGA. `CS0/ALERT0` are used for the BMC regardless. Multi-node provides a second full eSPI interface. **There is no LPC support** in either mode, and the host-to-BMC interface when eSPI is unavailable is out of scope. Known hosts vary in needing eSPI in S5, but tolerate S5 bias.

## 3.7 I2C and I3C

Single node offers 18 ports, split by voltage: **10 at 3.3 V** and **8 at 1.8 V**, for either I2C or I3C. Dual node offers 6 × 3.3 V and 3 × 1.8 V (bus numbers are not continuous). An additional 1.0 V group carries I2C/I3C or FSI.

**The rules:**

1. The HPM provides the I2C pull-up resistors.
2. The HPM does any cross-power-domain (AUX to Main) work and level translation.
3. More controllers are not precluded via bridges on PCIe, USB, LTPI, SPI or I3C-to-SMBus hubs.
4. There is no designated pure-initiator HPM to DC-SCM target bus.
5. No discrete I2C/SMBus alerts exist; treat them as virtual GPIOs via SPI_IRQ0, SGPIO or LTPI.
6. **The FRUID EEPROM sits directly on I2C0 at 8-bit address 0xA0**, never behind a mux or hub.
7. An authentication IC, if present, also sits on I2C0 on the same segment.
8. Avoid multi-initiator operation except for standard uses such as MCTP over SMBus or IPMB.

**Standards.** I2C follows the SMBus Specification Version 3.0; I3C does not exceed MIPI I3C Basic v1.1.1. HDR-BT (bulk transport) mode is **not** supported; HDR-DDR is not precluded but not guaranteed. On the SCM, total I3C bus capacitance (BMC pin plus trace plus DC-SCI pin) should be below **25 pF** to maximise clock rate.

**Minimum power state.** `I2C_3V3_0` (the FRU bus) must be powered in **Pre-STBY**. The others can wait until S5.

## 3.8 FSI, PECI, UART, battery, intrusion

- **FSI** (OpenPOWER Flexible Service Interface) is available as an alternate function on the 1.0 V pins, either I2C/I3C at 1.0 V or FSI at 1.2 V, not both.
- **PECI** is an optional bus plus power supply for CPU health monitoring; the BMC's PECI controller needs voltage from the HPM. If PECI is unused on both sides, `PECI_HPM_SCM` can serve as a low-voltage (0.85-1.21 V) GPIO biased only in S0, and `PECI_VREF_HPM_SCM` as a one-way HPM-to-SCM signal in that range.
- **UART:** two 3.3 V TTL UARTs without hardware flow control. UART0 is typically the host debug console when not eSPI-mapped; UART1 serves subsystem consoles (smart NICs, RAID cards). More UARTs can ride on USB, PCIe, LTPI or SPI.
- **Battery:** one pin carries 3.0 V from the HPM (`P3V0_HPM_SCM_BAT`).
- **Intrusion:** `HPM_SCM_INTRUSION_N`, optional, 3.3 V, active low: the switch is expected to be open when depressed (not intruded) and closed when released (cover removed).

## 3.9 JTAG

The DC-SCI offers a **BMC-initiator** JTAG for two uses: updating HPM programmable devices such as an FPGA, and at-scale ("closed-box") debug of ASICs or CPUs. The security issues around the second use are outside the specification.

**The 2.1 naming and direction change.** The DC-SCI **2.1** JTAG signal naming and direction follow IEEE 1149.1, defined **relative to the target device**. The specification states that the DC-SCI **1.0 and 2.0** releases did not follow the IEEE definition for TDI and TDO direction, and that this was fixed in 2.1. If you are connecting 2.0-era hardware to 2.1-era hardware, verify TDI and TDO explicitly (Chapter 6).

## 3.10 SGPIO

SGPIO follows the DC-MHS M-PIC Revision 1.0 specification and errata. Values below are from the 2.1 text.

| Parameter | Min | Max | Unit |
| --- | --- | --- | --- |
| SClock frequency | 5 | 25 | MHz |
| SClock duty cycle | 45 | 55 | % |
| Rise time / fall time | n/a | 6 | ns |
| Setup time | 0 | n/a | ns |
| Hold time | 2 | n/a | ns |
| Skew between SClock and SLoad/SDataOut/SDataIn on the SCM | n/a | 10 | ps |
| Interface voltage (3.3 V LVCMOS) | 3.135 | 3.465 | V |
| Input high (VIH) / low (VIL) | 1.7 / -0.3 | 3.465 / 0.8 | V |
| Output high (VOH) / low (VOL) | VCCIO-0.4 / n/a | n/a / 0.4 | V |
| I/O capacitance | n/a | 8 | pF |

The SCM should support the 25 MHz maximum, but the system may run slower because of cable and power-distribution-board loading.

## Worked exercises

**1. The NC-SI budget leaves how much for the HPM and NIC board?** 3000 − 680 − 110 = 2210 ps.

**2. An HPM puts its FRU EEPROM behind an I2C mux for convenience. What breaks?** The spec requires the FRU directly on I2C0 at address 0xA0 so the SCM can identify the HPM before anything else is configured. Behind a mux the SCM may not be able to find it, and a "Plug-N-Detect-Else-Halt" SCM would stop booting.

**3. How many 1.8 V buses does a single-node DC-SCI provide, and what can they carry?** Eight, usable as I2C or I3C.

**4. Which interface replaced LPC?** None: eSPI is the only host bus; LPC is not supported.

**5. In which DC-SCI revisions does the JTAG TDI/TDO direction differ from IEEE 1149.1?** Per the specification's own note, 1.0 and 2.0; the 2.1 update fixed it. Check the pinout of the exact revision you build to before wiring a JTAG header or an FPGA programming path.

## Review

- Which interface carries MCTP over PCIe VDM? **Answer:** the first PCIe x1 (A30-B31), where the BMC is an endpoint.
- What is the maximum SGPIO clock? **Answer:** 25 MHz.
- Which interfaces does LTPI replace in a dual-node design? **Answer:** it tunnels low-speed signals (GPIO, UART, I2C/SMBus and data), freeing pins for dedicated per-node interfaces.

Next: [Chapter 4: Power, boot and FRU](04_Power_Boot_and_FRU.md)
