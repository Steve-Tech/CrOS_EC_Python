#!/usr/bin/env python3
import struct
from cros_ec_python import CrOS_EC, DeviceTypes

"""
An example script to demonstrate how to use the cros_ec_python package to communicate with the EC.
This example is for Framework laptops only.
"""

# Uses the Linux device by default
ec = CrOS_EC()
# Uncomment the line below to use the LPC device instead, `address=0xE00` is only needed for AMD Frameworks
#ec = CrOS_EC(DeviceTypes.LPC, address=0xE00)

try:
    EC_CMD_PWM_GET_FAN_ACTUAL_RPM = 0x3E0F
    # Send the command with no data, expect 2 bytes in response
    response = ec.command(0, EC_CMD_PWM_GET_FAN_ACTUAL_RPM, 0, 1, None)
    # Side note: This is supposed to be 4 bytes (32-bit),
    # but the EC only returns 2 bytes, and sometimes 0 bytes?

    # Unpack the 2 bytes into a 16-bit unsigned integer
    fan_speed = struct.unpack("<B", response)[0]
    print(f"Fan Speed: {fan_speed} RPM")

except IOError as e:
    print("Couldn't get fan speed:", e)

# --- Fan Speed ---
# An example with no input parameters

try:
    EC_CMD_PWM_GET_FAN_ACTUAL_RPM = 0x3E04
    # Send the command with no data, expect 2 bytes in response
    response = ec.command(0, EC_CMD_PWM_GET_FAN_ACTUAL_RPM, 0, 2, None)
    # Side note: This is supposed to be 4 bytes (32-bit),
    # but the EC only returns 2 bytes, and sometimes 0 bytes?

    # Unpack the 2 bytes into a 16-bit unsigned integer
    fan_speed = struct.unpack("<H", response)[0]
    print(f"Fan Speed: {fan_speed} RPM")

except IOError as e:
    print("Couldn't get fan speed:", e)

# --- Fingerprint LED Brightness ---
# An example with input parameters

# Input Parameters
set_level = 0
get_level = True
# Pack into a 2 byte struct
data = struct.pack("<BB", set_level, get_level)

try:
    EC_CMD_FP_LED_LEVEL_CONTROL = 0x3E0E
    # Send the command, expect 1 byte in response
    response = ec.command(0, EC_CMD_FP_LED_LEVEL_CONTROL, len(data), 1, data)

    # Output is an 8-bit unsigned integer, so we don't need to unpack it
    print(f"Fingerprint LED Brightness: {response[0]}")

except IOError as e:
    print("Couldn't get fingerprint LED brightness:", e)

match input("Set the current brightness level (high, medium, low): "):
    case "high":
        set_level = 0
    case "medium":
        set_level = 1
    case "low":
        set_level = 2
    case _:
        exit()

get_level = False
# Pack into a 2 byte struct
data = struct.pack("<BB", set_level, get_level)

try:
    # Send the command, expect 0 bytes in response
    response = ec.command(0, 0x3E0E, len(data), 0, data)
    print("Brightness level set successfully")

except IOError as e:
    print("Couldn't set fingerprint LED brightness:", e)

