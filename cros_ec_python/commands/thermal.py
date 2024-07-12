"""
Thermal engine commands. Note that there are two implementations.
We'll reuse the command number, but the data and behavior is incompatible.

Version 0 is what originally shipped on Link.

Version 1 separates the CPU thermal limits from the fan control.
"""

from typing import Final
import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *

EC_CMD_THERMAL_SET_THRESHOLD: Final = 0x0050
EC_CMD_THERMAL_GET_THRESHOLD: Final = 0x0051

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
