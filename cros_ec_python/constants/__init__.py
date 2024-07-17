"""
# Description
These are constants to use throughout the project.

You are welcome to use these too for lower level commands (e.g. by using `cros_ec_python.baseclass.CrosEcClass.command`),
but they shouldn't be needed for the abstracted commands provided by this library.

## Example

Here is an example of using the constants in this submodule, to read the temperature sensors from the EC memmap:

```python
import struct
from cros_ec_python import get_cros_ec, CrosEcLpc

ec = CrosEcLpc(address=EC_LPC_ADDR_MEMMAP)
# ec = get_cros_ec()  # <- Or: this is the easiest way to get the EC object if you don't know which interface or address

response = ec.memmap(EC_MEMMAP_TEMP_SENSOR, EC_TEMP_SENSOR_ENTRIES * 1)
temps = struct.unpack("<16B", response)

for i, temp in enumerate(temps):
    if temp >= EC_TEMP_SENSOR_NOT_CALIBRATED:
        # Something wrong with the sensor
        continue
    tempK = temp + EC_TEMP_SENSOR_OFFSET
    tempC = tempK - 273
    print(f"Temp Sensor {i}: {tempK}K ({tempC}°C)")
```
"""
