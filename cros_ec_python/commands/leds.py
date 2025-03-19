"""
LED control commands
"""

from typing import Final
from enum import Enum, auto
import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *

EC_CMD_LED_CONTROL: Final = 0x0029


class EcLedId(Enum):
    # LED to indicate battery state of charge
    EC_LED_ID_BATTERY_LED = 0
    #
    # LED to indicate system power state (on or in suspend).
    # May be on power button or on C-panel.

    EC_LED_ID_POWER_LED = auto()
    # LED on power adapter or its plug
    EC_LED_ID_ADAPTER_LED = auto()
    # LED to indicate left side
    EC_LED_ID_LEFT_LED = auto()
    # LED to indicate right side
    EC_LED_ID_RIGHT_LED = auto()
    # LED to indicate recovery mode with HW_REINIT
    EC_LED_ID_RECOVERY_HW_REINIT_LED = auto()
    # LED to indicate sysrq debug mode.
    EC_LED_ID_SYSRQ_DEBUG_LED = auto()

    EC_LED_ID_COUNT = auto()


# LED control flags
EC_LED_FLAGS_QUERY = BIT(0)  # Query LED capability only
EC_LED_FLAGS_AUTO = BIT(1)  # Switch LED back to automatic control


class EcLedColors(Enum):
    EC_LED_COLOR_RED = 0
    EC_LED_COLOR_GREEN = auto()
    EC_LED_COLOR_BLUE = auto()
    EC_LED_COLOR_YELLOW = auto()
    EC_LED_COLOR_WHITE = auto()
    EC_LED_COLOR_AMBER = auto()

    EC_LED_COLOR_COUNT = auto()


def led_control(ec: CrosEcClass, led_id: EcLedId, flags: UInt8, brightnesses: list[UInt8]) -> list[UInt8]:
    """
    Control an LED
    :param ec: The CrOS_EC object.
    :param led_id: The LED to control.
    :param flags: Control flags. See EC_LED_FLAGS_*.
    :param brightnesses: Brightness values for each color. (6 colors, see EcLedColors)
    :return: The available brightness value range for each color.
    """
    data = struct.pack(f"<BB{EcLedColors.EC_LED_COLOR_COUNT.value}B", led_id.value, flags, *brightnesses)
    resp = ec.command(1, EC_CMD_LED_CONTROL, len(data), EcLedColors.EC_LED_COLOR_COUNT.value, data)
    return list(resp)


def led_control_set_color(ec: CrosEcClass, led_id: EcLedId, brightness: UInt8, color: EcLedColors) -> list[UInt8]:
    """
    Set the color of an LED
    :param ec: The CrOS_EC object.
    :param led_id: The LED to control.
    :param brightness: Brightness value.
    :param color: Color to set the LED to.
    :return: The available brightness value range for each color.
    """
    brightnesses = [0] * EcLedColors.EC_LED_COLOR_COUNT.value
    brightnesses[color.value] = brightness
    return led_control(ec, led_id, 0, brightnesses)


def led_control_get_max_values(ec: CrosEcClass, led_id: EcLedId) -> list[UInt8]:
    """
    Get the available brightness value range for each color of an LED
    :param ec: The CrOS_EC object.
    :param led_id: The LED to get the brightness values of.
    :return: The available brightness value range for each color.
    """
    return led_control(ec, led_id, EC_LED_FLAGS_QUERY, [0] * EcLedColors.EC_LED_COLOR_COUNT.value)


def led_control_set_auto(ec: CrosEcClass, led_id: EcLedId) -> list[UInt8]:
    """
    Set an LED back to automatic control
    :param ec: The CrOS_EC object.
    :param led_id: The LED to get the brightness values of.
    :return: The available brightness value range for each color.
    """
    return led_control(ec, led_id, EC_LED_FLAGS_AUTO, [0] * EcLedColors.EC_LED_COLOR_COUNT.value)
