"""
These functions are used to get the values of the memory-mapped data.

They aren't actually commands that are sent to the EC (usually), but rather data that is read from the EC.
This is why they aren't mixed in with the other commands.
"""


import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..constants.MEMMAP import *


def get_temps(ec: CrosEcClass, adjust: int | float = -273) -> list[int | float]:
    """
    Get the temperature of all temp sensors.
    :param ec: The CrOS_EC object.
    :param adjust: The adjustment to apply to the temperature. Default is -273 to convert from Kelvin to Celsius.
    :return: A list of temperatures.
    """
    version = int(ec.memmap(EC_MEMMAP_THERMAL_VERSION, 1)[0])
    if not version:
        # No temp sensors supported
        return []

    ret = []
    if version >= 1:
        resp = ec.memmap(EC_MEMMAP_TEMP_SENSOR, EC_TEMP_SENSOR_ENTRIES)
        temps = struct.unpack(f"<{EC_TEMP_SENSOR_ENTRIES}B", resp)
        ret += [temp + EC_TEMP_SENSOR_OFFSET + adjust for temp in temps if temp < 0xFC]

    if version >= 2:
        resp = ec.memmap(EC_MEMMAP_TEMP_SENSOR_B, EC_TEMP_SENSOR_B_ENTRIES)
        temps = struct.unpack(f"<{EC_TEMP_SENSOR_B_ENTRIES}B", resp)
        ret += [temp + EC_TEMP_SENSOR_OFFSET + adjust for temp in temps if temp < 0xFC]

    return ret


def get_fans(ec: CrosEcClass) -> list[int | None]:
    """
    Get the speed of all fans.
    :param ec: The CrOS_EC object.
    :return: A list of fan speeds. None if the fan has stalled.
    """
    version = int(ec.memmap(EC_MEMMAP_THERMAL_VERSION, 1)[0])
    if not version:
        # No fans supported
        return []

    resp = ec.memmap(EC_MEMMAP_FAN, EC_FAN_SPEED_ENTRIES * 2)  # 2 bytes per fan
    fans = struct.unpack(f"<{EC_FAN_SPEED_ENTRIES}H", resp)
    return [None if fan is EC_FAN_SPEED_STALLED else fan for fan in fans if fan < EC_FAN_SPEED_NOT_PRESENT]


def get_switches(ec: CrosEcClass) -> dict[str, bool]:
    """
    Get the state of the switches.
    :param ec: The CrOS_EC object.
    :return: The state of the switches.
    """
    version = int(ec.memmap(EC_MEMMAP_SWITCHES_VERSION, 1)[0])
    if not version:
        # No switches supported
        return {}

    resp = ec.memmap(EC_MEMMAP_SWITCHES, 1)[0]
    return {
        "lid_open": bool(resp & EC_SWITCH_LID_OPEN),
        "power_button_pressed": bool(resp & EC_SWITCH_POWER_BUTTON_PRESSED),
        "write_protect_disabled": bool(resp & EC_SWITCH_WRITE_PROTECT_DISABLED),
        "dedicated_recovery": bool(resp & EC_SWITCH_DEDICATED_RECOVERY)
    }


def get_battery_values(ec: CrosEcClass) -> dict[str, int | bool | str]:
    """
    Get the values of the battery.
    :param ec: The CrOS_EC object.
    :return: The state of the battery.
    """
    version = int(ec.memmap(EC_MEMMAP_BATTERY_VERSION, 1)[0])
    if not version:
        # No battery supported
        return {}

    resp = ec.memmap(EC_MEMMAP_BATT_VOLT, EC_MEMMAP_ALS - EC_MEMMAP_BATT_VOLT)
    data = struct.unpack("<IIIBBBxIIII8s8s8s8s", resp)
    return {
        "volt": data[0],
        "rate": data[1],
        "capacity": data[2],
        "ac_present": bool(data[3] & EC_BATT_FLAG_AC_PRESENT),
        "batt_present": bool(data[3] & EC_BATT_FLAG_BATT_PRESENT),
        "discharging": bool(data[3] & EC_BATT_FLAG_DISCHARGING),
        "charging": bool(data[3] & EC_BATT_FLAG_CHARGING),
        "level_critical": bool(data[3] & EC_BATT_FLAG_LEVEL_CRITICAL),
        "invalid_data": bool(data[3] & EC_BATT_FLAG_INVALID_DATA),
        "count": data[4],
        "index": data[5],
        "design_capacity": data[6],
        "design_voltage": data[7],
        "last_full_charge_capacity": data[8],
        "cycle_count": data[9],
        "manufacturer": data[10].decode("utf-8").rstrip("\x00"),
        "model": data[11].decode("utf-8").rstrip("\x00"),
        "serial": data[12].decode("utf-8").rstrip("\x00"),
        "type": data[13].decode("utf-8").rstrip("\x00")
    }


def get_als(ec: CrosEcClass) -> list[int]:
    """
    Get the current value from all Ambient Light Sensors.
    :param ec: The CrOS_EC object.
    :return: A list of ALS values. May be 0 if the sensor is not present.
    """
    resp = ec.memmap(EC_MEMMAP_ALS, EC_ALS_ENTRIES * 2)  # 2 bytes per sensor
    als = struct.unpack(f"<{EC_ALS_ENTRIES}H", resp)
    return [val for val in als]


def get_accel(ec: CrosEcClass) -> list[int]:
    """
    Get the current value from all accelerometers.
    :param ec: The CrOS_EC object.
    :return: A list of accelerometer values. May be 0 if the sensor is not present.
    """
    EC_ACC_ENTRIES: Final = 3
    resp = ec.memmap(EC_MEMMAP_ACC_DATA, EC_ACC_ENTRIES * 2)  # 2 bytes per sensor
    accel = struct.unpack(f"<{EC_ACC_ENTRIES}H", resp)
    return [val for val in accel]
