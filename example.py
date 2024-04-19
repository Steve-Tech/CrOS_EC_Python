#!/usr/bin/env python3
import struct
from cros_ec_python.cros_ec import ec_command, ec_readmem

"""
An example script to demonstrate how to use the cros_ec_python package to communicate with the EC.
"""

# --- Temperature Sensors ---
# An example that uses the ec memory map to read the temperature sensors

try:
    EC_MEMMAP_TEMP_SENSOR = 0x0
    EC_MEMMAP_TEMP_SENSOR_B = 0x18
    EC_TEMP_SENSOR_ENTRIES = 16
    EC_TEMP_SENSOR_B_ENTRIES = 8

    response = ec_readmem(EC_MEMMAP_TEMP_SENSOR, EC_TEMP_SENSOR_ENTRIES * 1)
    temps = struct.unpack("<16B", response)

    EC_TEMP_SENSOR_OFFSET = 200
    for i, temp in enumerate(temps):
        if temp >= 0xFC:
            # Something wrong with the sensor
            continue
        tempK = temp + EC_TEMP_SENSOR_OFFSET
        tempC = tempK - 273
        print(f"Temp Sensor {i}: {tempK}K ({tempC}°C)")

except IOError as e:
    print("Couldn't get temp sensors:", e)

# --- Get Fan Speed ---
# Another example that uses the ec memory map to read the fan speeds

try:
    EC_MEMMAP_FAN = 0x10
    EC_FAN_SPEED_ENTRIES = 4
    response = ec_readmem(EC_MEMMAP_FAN, EC_FAN_SPEED_ENTRIES * 2)
    fans = struct.unpack("<4H", response)

    for i, fan in enumerate(fans):
        if fan >= 0xFFFE:
            # Something wrong with the fan
            continue
        print(f"Fan {i}: {fan} RPM")

except IOError as e:
    print("Couldn't get fan speeds:", e)

# --- Get Fan Target ---
# A command example with no input parameters

try:
    EC_CMD_PWM_GET_FAN_TARGET_RPM = 0x0020
    # Send the command with no data, expect 4 bytes in response
    response = ec_command(0, EC_CMD_PWM_GET_FAN_TARGET_RPM, 0, 4, None)

    # Unpack the 4 bytes into a 32-bit unsigned integer
    fan_speed = struct.unpack("<I", response)[0]
    print(f"Fan Target: {fan_speed} RPM")

except IOError as e:
    print("Couldn't get fan target:", e)

# --- Set Fan Duty ---
# A command example with input parameters

if percent_in := input("Enter fan speed [0-100]: "):
    # Input Parameters
    percent = int(percent_in)
    fan_idx = 0

    # Pack into a 5 byte struct
    data = struct.pack("<IB", percent, fan_idx)

    try:
        EC_CMD_PWM_SET_FAN_DUTY = 0x0024
        # Send the command, expect 0 bytes in response
        response = ec_command(0, EC_CMD_PWM_SET_FAN_DUTY, len(data), 0, data)
        print("Fan duty set successfully")

    except IOError as e:
        print("Couldn't set fan duty:", e)

# --- Auto Fan Control ---
# So people can reset their fan control, but also it's a version 1 command
if input("Auto fan control [Y/n]: ").lower() == "y":
    # Input Parameters
    fan_idx = 0

    # Convert to bytes, an alternative to structs of 8bit integers
    data = bytes([fan_idx])

    try:
        EC_CMD_THERMAL_AUTO_FAN_CTRL = 0x0052
        # Send the command (v1) with no data, expect 0 bytes in response
        response = ec_command(1, EC_CMD_THERMAL_AUTO_FAN_CTRL, len(data), 0, data)
        print("Fan control set to auto")

    except IOError as e:
        print("Couldn't set fan control:", e)
