"""
Thermal engine commands.
"""

from typing import Final
from enum import Enum, auto
import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from .memmap import get_temps

EC_CMD_THERMAL_SET_THRESHOLD: Final = 0x0050
EC_CMD_THERMAL_GET_THRESHOLD: Final = 0x0051


class EcTempThresholds(Enum):
    EC_TEMP_THRESH_WARN = 0
    EC_TEMP_THRESH_HIGH = auto()
    EC_TEMP_THRESH_HALT = auto()

    EC_TEMP_THRESH_COUNT = auto()


def thermal_get_thresholds(
    ec: CrosEcClass, sensor_num: int, adjust: int | float = -273
) -> dict[str, list[int | float] | int | float]:
    """
    Get the temperature threshold configuration for a given sensor.
    :param ec: The CrOS_EC object.
    :param sensor_num: The sensor number.
    :param adjust: The adjustment to apply to the temperature. Default is -273 to convert from Kelvin to Celsius.
    :return: A dictionary containing the threshold configuration.
    """
    data = struct.pack("<I", sensor_num)
    thresh_count: Final = EcTempThresholds.EC_TEMP_THRESH_COUNT.value
    resp = ec.command(
        1,
        EC_CMD_THERMAL_GET_THRESHOLD,
        4,
        4 * thresh_count + 4 * thresh_count + 4 + 4,
        data,
    )
    config = struct.unpack(f"<{thresh_count}I{thresh_count}III", resp)
    return {
        "temp_host": [(i + adjust) for i in config[0:thresh_count]],
        "temp_host_release": [
            (i + adjust) for i in config[thresh_count : thresh_count * 2]
        ],
        "temp_fan_off": config[thresh_count * 2] + adjust,
        "temp_fan_max": config[thresh_count * 2 + 1] + adjust,
    }


def thermal_set_thresholds(
    ec: CrosEcClass,
    sensor_num: int,
    config: dict[str, list[int | float] | int | float],
    adjust: int | float = 273,
) -> None:
    """
    Set the temperature thresholds for a given sensor.
    :param ec: The CrOS_EC object.
    :param sensor_num: The sensor number.
    :param config: A dictionary containing the threshold configuration.
    :param adjust: The adjustment to apply to the temperature. Default is 273 to convert from Celsius to Kelvin.
    """
    thresh_count: Final = EcTempThresholds.EC_TEMP_THRESH_COUNT.value
    data = struct.pack(
        f"<I{thresh_count}I{thresh_count}III",
        sensor_num,
        *[int(i + adjust) for i in config["temp_host"]],
        *[int(i + adjust) for i in config["temp_host_release"]],
        int(config["temp_fan_off"] + adjust),
        int(config["temp_fan_max"] + adjust),
    )
    ec.command(1, EC_CMD_THERMAL_SET_THRESHOLD, len(data), 0, data)


EC_CMD_THERMAL_AUTO_FAN_CTRL: Final = 0x0052


def thermal_auto_fan_ctrl(ec: CrosEcClass, fan_idx: UInt8 | None = None) -> None:
    """
    Toggle automatic fan control.
    :param ec: The CrOS_EC object.
    :param fan_idx: The fan index to control (v1 command). If None, it will set all fans (v0 command).
    """
    if fan_idx is None:
        ec.command(0, EC_CMD_THERMAL_AUTO_FAN_CTRL, 0, 0)
    else:
        data = struct.pack("<B", fan_idx)
        ec.command(1, EC_CMD_THERMAL_AUTO_FAN_CTRL, 1, 0, data)


EC_CMD_TMP006_GET_CALIBRATION: Final = 0x0053
EC_CMD_TMP006_SET_CALIBRATION: Final = 0x0054
EC_CMD_TMP006_GET_RAW: Final = 0x0055

EC_CMD_TEMP_SENSOR_GET_INFO: Final = 0x0070

class EcTempSensorType(Enum):
    TEMP_SENSOR_TYPE_IGNORED = -1
    TEMP_SENSOR_TYPE_CPU = 0
    TEMP_SENSOR_TYPE_BOARD = auto()
    TEMP_SENSOR_TYPE_CASE = auto()
    TEMP_SENSOR_TYPE_BATTERY = auto()

    TEMP_SENSOR_TYPE_COUNT = auto()

def temp_sensor_get_info(ec: CrosEcClass, sensor_idx: UInt8) -> dict[str, EcTempSensorType]:
    """
    Get information about a temperature sensor.
    :param ec: The CrOS_EC object.
    :param sensor_idx: The sensor index.
    :return: The response data.
    """
    data = struct.pack("<B", sensor_idx)
    resp = ec.command(0, EC_CMD_TEMP_SENSOR_GET_INFO, 1, 33, data)
    unpacked = struct.unpack("<32sB", resp)
    return {
        "name": unpacked[0].decode("utf-8").rstrip("\x00"),
        "type": EcTempSensorType(unpacked[1])
    }

def get_temp_sensors(ec: CrosEcClass) -> dict[str, tuple[int, EcTempSensorType]]:
    """
    Get information about all temperature sensors.
    :param ec: The CrOS_EC object.
    :return: The response data.
    """
    temps = get_temps(ec)
    ret = {}
    for i, j in enumerate(temps):
        info = temp_sensor_get_info(ec, i)
        ret[info["name"]] = (j, info["type"])
    return ret
