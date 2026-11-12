# 4. Bring-up Workbook and Reference

## 4.1 Start with a falsifiable statement

"Sensors are broken" is not a useful test result. A useful statement names the board, firmware identity, host power state, sensor identity, expected behavior, observed behavior, and observation time.

Example: "In the lab image, the board-temperature sensor exists on D-Bus with availability true, but the discovered Redfish chassis collection has no associated sensor resource after discovery has settled."

That narrows the boundary and suggests the next experiment. Preserve evidence before restarting services.

## 4.2 Fault-localization table

| Symptom | First useful evidence | Next discriminating check |
| --- | --- | --- |
| No UART output | Power/reset/console setup | Documented ROM behavior and boot source |
| Bootloader runs, no kernel | Selected image and load/handoff logs | Image validity, entry, DTB, early console |
| Kernel cannot mount root | Kernel command line and storage probe | Root device, filesystem support, image layout |
| Unit fails | Status, journal, actual unit | Exec path, shared libraries, permissions, configuration |
| Sensor object absent | Provider/discovery logs | Matching board config and kernel interface |
| Value wrong | Raw quantity and conversion | Channel mapping, units, calibration |
| API value missing | D-Bus value/status/associations | bmcweb mapping and supported schema |
| Update uploaded but old version runs | Update task and boot-selection state | Installation, activation, rollback decision |

## 4.3 Observation-only lab

Use a lab BMC with authorization. Do not force fan speeds or toggle power as part of this exercise.

1. Record firmware identity and the managed host's power state.
2. Record `uname -a`, `/proc/cmdline`, and a bounded boot journal.
3. Discover one sensor in the documented kernel or protocol path.
4. Discover the D-Bus owner, interfaces, numeric value, status, and association.
5. Discover its Redfish representation by following links.
6. Normalize units and compare observations from a close time window.
7. Explain any absence, conversion, delay, or status discrepancy.

Expected artifact: a private trace table, not an unfiltered log upload.

| Layer | Identity | Value/units | Quality | Timestamp |
| --- | --- | --- | --- | --- |
| Source | Actual driver/protocol sensor | Measured quantity | Device state | Observation |
| D-Bus | Provider/object/interface | Published quantity | Availability/function | Observation |
| API | Discovered URI | Schema representation | Redfish status | Observation |

**Pass condition:** all three observations refer to the same physical or logical sensor; quantities agree within documented conversion and sampling tolerances; quality and freshness are accounted for. "Three commands returned output" is not enough.

## 4.4 Bring-up acceptance

Define acceptance by function:

- Required boot milestones occur within a project-defined budget.
- Expected inventory is present in applicable power states.
- Sensor readings match independent references within stated tolerances.
- Thermal control has a documented safe response to unavailable readings.
- Authenticated management APIs expose correct status and privileges.
- Firmware installation and interrupted-update recovery meet the product's policy.
- Persistence behavior is tested across restart/update/recovery boundaries.

The exact tolerances, timings, and supported power states come from platform requirements, not this generic textbook.

## 4.5 Review and answers

1. Is D-Bus an on-disk database? **No:** object state belongs to services and can disappear.
2. Does `systemctl is-active` prove sensor readiness? **No:** inspect actual data and quality.
3. Is a reading of zero a safe missing-data default? **No:** preserve unavailability.
4. Does a host-off test prove total power-loss survivability? **No:** standby-powered behavior is different.
5. Can a string identify a function conclusively? **No:** cross-reference and runtime evidence are needed.

## Glossary

| Term | Meaning |
| --- | --- |
| BMC | Independent platform-management controller |
| FRU | Replaceable-unit inventory concept/data |
| DTB | Compiled device-tree description |
| Object Mapper | OpenBMC service/provider discovery mechanism |
| Association | Relationship between modeled objects |
| hwmon | Linux hardware-monitoring subsystem |
| FIT | U-Boot-oriented structured image format |
| UBI | Volume management over raw flash |
| Activation | Making an installed firmware version active |
| Readiness | Evidence that the required function can operate |

Return to [contents](00_README.md), continue to [Yocto](../Yocto_BMC_Build_Textbook/00_README.md), or study [MCTP](../MCTP_Textbook/00_README.md).
