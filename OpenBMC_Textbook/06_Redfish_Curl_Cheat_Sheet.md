# 6. Redfish with curl: A Cheat Sheet

Redfish is not a command-line tool. It is a REST API served by the BMC (in OpenBMC, by `bmcweb`), so you use it with `curl`, a script, or a client library. [Chapter 2](02_DBus_Sensors_and_Redfish.md) explains how Redfish resources map to D-Bus objects. This page is the practical command set.

## 6.1 Verbs

| Method | Meaning |
| --- | --- |
| `GET` | read a resource |
| `POST` | create a resource or invoke an action |
| `PATCH` | update properties |
| `DELETE` | remove a resource |

## 6.2 Safe defaults

The examples set up a few shell variables. `--user "$U"` with no password makes curl prompt for it, so the password stays out of shell history. `--cacert` checks the BMC's certificate.

```sh
BMC=https://<bmc-host>
U=<username>
CA=lab-ca.pem
RF="curl --fail-with-body --cacert $CA --user $U"
```

`-k` (`--insecure`) skips certificate checks. It is common on lab BMCs with self-signed certificates, but it removes protection against impersonation. Do not make it a production habit. Never put real lab hostnames, IP addresses, or credentials in shared notes.

## 6.3 Discover before you assume

```sh
$RF $BMC/redfish/v1                       # service root
$RF $BMC/redfish/v1/Systems               # systems collection
$RF $BMC/redfish/v1/Managers              # the BMC(s)
$RF $BMC/redfish/v1/Chassis               # physical enclosures, sensors
```

A collection returns `Members` (a list of `@odata.id` links) and `Members@odata.count`. **Use the returned `@odata.id` values.** The member name may be `1`, `system`, `bmc`, or something vendor-specific; do not hard-code `Systems/1`.

```sh
$RF $BMC/redfish/v1/Systems/<id>
$RF $BMC/redfish/v1/Managers/<id>
$RF $BMC/redfish/v1/Systems/<id>/EthernetInterfaces
$RF $BMC/redfish/v1/Systems/<id>/LogServices
```

Pretty-print with `| jq`.

## 6.4 Power control

```sh
$RF -X POST $BMC/redfish/v1/Systems/<id>/Actions/ComputerSystem.Reset \
  -H "Content-Type: application/json" \
  -d '{"ResetType":"On"}'
```

| `ResetType` | Effect |
| --- | --- |
| `On` | power the host on |
| `ForceOff` | immediate power off (like holding the power button) |
| `GracefulShutdown` | ask the OS to shut down |
| `ForceRestart` | immediate reset |
| `GracefulRestart` | ask the OS to restart |

Supported values vary by implementation. Check `ResetType@Redfish.AllowableValues` on the action in the system resource before you send one. Power actions affect a real host, so use them only on systems you are authorised to control.

## 6.5 Headers

```sh
-H "Content-Type: application/json"     # for POST/PATCH bodies
-H "Accept: application/json"
```

## 6.6 How this connects to the boot walkthrough

A `ComputerSystem.Reset` with `On` is Stage 6 of [Chapter 5](05_Power_SPI_Flash_and_Boot_Walkthrough.md). `bmcweb` turns it into a D-Bus state request, the state manager or power-control service drives the power-button GPIO, and the host powers up.

## Review

1. A `GET` on `/redfish/v1/Systems/1` returns 404. What do you do? **Answer:** `GET` the `Systems` collection and use the `@odata.id` it returns.
2. Why prefer `--user name` over `-u name:password`? **Answer:** curl prompts for the password, so it does not appear in shell history or process listings.
3. Which `ResetType` asks the OS to shut down cleanly? **Answer:** `GracefulShutdown`.

Return to [contents](00_README.md)
