"""
PWM commands
"""

from typing import Final
from enum import Enum, auto
import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *

EC_CMD_PWM_GET_FAN_TARGET_RPM: Final = 0x0020


def pwm_get_fan_rpm(ec: CrosEcClass) -> UInt32:
    """
    Get fan target RPM
    :param ec: The CrOS_EC object.
    :return: The current fan target RPM.
    """
    resp = ec.command(0, EC_CMD_PWM_GET_FAN_TARGET_RPM, 0, 4)
    return struct.unpack("<I", resp)[0]


EC_CMD_PWM_SET_FAN_TARGET_RPM: Final = 0x0021


def pwm_set_fan_rpm(ec: CrosEcClass, rpm: UInt32, idx: UInt8 | None = None) -> None:
    """
    Set target fan RPM
    :param ec: The CrOS_EC object.
    :param rpm: The RPM to set the fan to.
    :param idx: The index of the fan to set the RPM for (v1 command). If None, it will set all fans (v0 command).
    :return: The current fan target RPM.
    """
    if idx is None:
        data = struct.pack("<I", rpm)
        ec.command(0, EC_CMD_PWM_SET_FAN_TARGET_RPM, 4, 0, data)
    else:
        data = struct.pack("<IB", rpm, idx)
        ec.command(1, EC_CMD_PWM_SET_FAN_TARGET_RPM, 5, 0, data)


EC_CMD_PWM_GET_KEYBOARD_BACKLIGHT: Final = 0x0022


def pwm_get_keyboard_backlight(ec: CrosEcClass) -> dict[str, UInt8]:
    """
    Get keyboard backlight
    OBSOLETE - Use EC_CMD_PWM_SET_DUTY
    :param ec: The CrOS_EC object.
    :return: The current keyboard backlight percentage and state.
    """
    resp = ec.command(0, EC_CMD_PWM_GET_KEYBOARD_BACKLIGHT, 0, 2)
    unpacked = struct.unpack("<BB", resp)
    return {
        "percent": unpacked[0],
        "enabled": unpacked[1]
    }


EC_CMD_PWM_SET_KEYBOARD_BACKLIGHT: Final = 0x0023


def pwm_set_keyboard_backlight(ec: CrosEcClass, percent: UInt8) -> None:
    """
    Set keyboard backlight
    OBSOLETE - Use EC_CMD_PWM_SET_DUTY
    :param ec: The CrOS_EC object.
    :param percent: The percentage to set the keyboard backlight to.
    :return: None
    """
    data = struct.pack("<B", percent)
    ec.command(0, EC_CMD_PWM_SET_KEYBOARD_BACKLIGHT, 1, 0, data)


EC_CMD_PWM_SET_FAN_DUTY: Final = 0x0024


def pwm_set_fan_duty(ec: CrosEcClass, percent: UInt32, idx: UInt8 | None = None) -> None:
    """
    Set target fan PWM duty cycle
    :param ec: The CrOS_EC object.
    :param percent: The duty cycle to set the fan to. Out of 100.
    :param idx: The index of the fan to set the duty cycle for (v1 command). If None, it will set all fans (v0 command).
    :return: None
    """
    if idx is None:
        data = struct.pack("<I", percent)
        ec.command(0, EC_CMD_PWM_SET_FAN_DUTY, 1, 0, data)
    else:
        data = struct.pack("<IB", percent, idx)
        ec.command(1, EC_CMD_PWM_SET_FAN_DUTY, 2, 0, data)


EC_CMD_PWM_SET_DUTY: Final = 0x0025
# 16 bit duty cycle, 0xffff = 100%
EC_PWM_MAX_DUTY: Final = 0xffff


class EcPwmType(Enum):
    # All types, indexed by board-specific enum pwm_channel
    EC_PWM_TYPE_GENERIC = 0
    # Keyboard backlight
    EC_PWM_TYPE_KB_LIGHT = auto()
    # Display backlight
    EC_PWM_TYPE_DISPLAY_LIGHT = auto()
    EC_PWM_TYPE_COUNT = auto()


def pwm_set_duty(ec: CrosEcClass, duty: UInt16, pwm_type: EcPwmType, index: UInt8 = 0) -> None:
    """
    Set PWM duty cycle
    :param ec: The CrOS_EC object.
    :param duty: The duty cycle to set the PWM to. Out of EC_PWM_MAX_DUTY (0xffff).
    :param pwm_type: The type of PWM to set.
    :param index: The index of the PWM to set the duty cycle for.
    :return: None
    """
    data = struct.pack("<HBB", duty, pwm_type.value, index)
    ec.command(0, EC_CMD_PWM_SET_DUTY, 4, 0, data)


EC_CMD_PWM_GET_DUTY: Final = 0x0026


def pwm_get_duty(ec: CrosEcClass, pwm_type: EcPwmType, index: UInt8 = 0) -> UInt16:
    """
    Get PWM duty cycle
    :param ec: The CrOS_EC object.
    :param pwm_type: The type of PWM to get.
    :param index: The index of the PWM to get the duty cycle for.
    :return: The current PWM duty cycle. Out of EC_PWM_MAX_DUTY (0xffff).
    """
    data = struct.pack("<BB", pwm_type.value, index)
    resp = ec.command(0, EC_CMD_PWM_GET_DUTY, 2, 2, data)
    return struct.unpack("<H", resp)[0]
