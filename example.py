#!/usr/bin/env python3
import struct
from cros_ec_python.cros_ec import ec_command, ec_readmem

"""
An example script to demonstrate how to use the cros_ec_python package to communicate with the EC.
"""

# --- Temperature Sensors ---

try:
    EC_TEMP_SENSOR_OFFSET = 200
    response = ec_readmem(0x0, 16)
    temps = struct.unpack("<16B", response)

    for i, temp in enumerate(temps):
        if temp >= 0xFC:
            # Something wrong with the sensor
            continue
        tempK = temp + EC_TEMP_SENSOR_OFFSET
        tempC = tempK - 273
        print(f"Temp Sensor {i}: {tempK}K ({tempC}°C)")

except IOError as e:
    print("Couldn't get temp sensors:", e)
