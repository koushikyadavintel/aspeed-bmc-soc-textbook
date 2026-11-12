# 2. Discovery, D-Bus, Sensors, and Redfish

## 2.1 D-Bus names are not filesystem paths

A service can own a well-known bus name and publish objects at object paths. Interfaces define typed methods, signals, and properties. A connection also has a unique bus name; a service restart can change that connection and recreate its objects.

For example, `/xyz/openbmc_project/sensors/temperature/Board_Temp` is an illustrative object path. It is not a directory to inspect with `cat`. A value interface commonly exposes a double-valued `Value`; other interfaces express availability, operational state, thresholds, and associations.

Object Mapper discovers providers by paths and interfaces. It is not a persistent sensor database. Standard D-Bus ObjectManager enumerates objects and interfaces exported below a managed path; it is related to discovery but not identical to OpenBMC Object Mapper.

## 2.2 From board identity to sensor

A common implementation uses:

```text
board identity / FRU / presence / configuration
    -> entity-manager match
    -> D-Bus configuration objects
    -> relevant sensor daemon
    -> value/status/threshold objects
```

Entity Manager configuration describes what to expose when a probe matches. A sensor daemon can consume that configuration and instantiate measurement objects. Other platforms have alternative services and legacy paths.

Inventory describes components and relationships. Sensors describe measurements or states. A replaceable module can be in inventory while its sensors are temporarily unavailable. Conversely, a measurement without the expected chassis association may not appear at the intended Redfish location.

## 2.3 Units and quality matter

Suppose a hwmon input reports `42500`, in the subsystem's defined millidegree units. A daemon may expose `42.5` degrees Celsius. Redfish may expose a schema-defined value and unit at a version-dependent sensor resource.

Compare physical quantity, not literal bytes:

```text
driver value + documented units
    -> conversion + calibration/configuration
    -> D-Bus numeric value + availability/status
    -> Redfish representation + schema/status
```

Do not apply scaling twice. Do not treat stale cached data as a fresh measurement. A valid number with `Available=false` is not a trustworthy live reading. A missing property is not necessarily zero.

## 2.4 Trace one observation

On an authorized lab image:

```sh
busctl --system list --no-pager
busctl --system tree --no-pager
```

Discover a provider, then use its actual name and object:

```text
busctl --system introspect <service> <object>
busctl --system get-property <service> <object> <interface> <property>
```

The angle-bracket entries are placeholders, not literal shell arguments. Record the provider's unit, image version, timestamp, interfaces, value, and quality state. Repeat after a controlled restart only if authorized; ownership and objects may change.

A userspace daemon reading sysfs enters the kernel through filesystem/syscall paths. A kernel driver may subsequently use `i2c_transfer()`. Identifying an import named `read` or a string mentioning `hwmon` does not prove a direct kernel-function call from userspace.

## 2.5 Redfish translates a model

`bmcweb` commonly implements HTTPS routing, authentication, privilege checks, and Redfish resource construction. It may gather properties from several services, query associations, map internal states to schema fields, and generate links.

```text
GET -> authentication/privileges -> route handler
    -> mapper/provider lookups -> D-Bus values and status
    -> schema mapping -> JSON or Redfish error
```

Start at `/redfish/v1/`, follow advertised links, and discover collection members. Do not hard-code a chassis ID or assume every release exposes the same thermal/sensor URI.

For a Linux client configured to trust the lab CA:

```sh
curl --fail-with-body --cacert lab-ca.pem --user operator \
  https://bmc.example.test/redfish/v1/
```

With only the username supplied, curl prompts for the password rather than placing it in shell history. Use an authorized account and the correct certificate. Do not normalize disabling certificate verification as a production workaround.

An HTTP 200 is not proof of complete platform discovery. Inspect the actual JSON, `Status`, units, errors, and resource membership.

## Exercise

The hwmon quantity is correct and D-Bus has the correct value, but Redfish omits it.

**Answer guide:** check availability and status, inventory/chassis associations, actual resource discovery, handler support, schema differences, and API-service logs. Rewriting the driver is not the first discriminating test.

Next: [Flash images and updates](03_Flash_Images_and_Updates.md).
