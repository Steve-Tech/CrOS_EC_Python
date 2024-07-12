"""
List the features supported by the firmware
"""

from typing import Final
from enum import Enum
import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *

EC_CMD_GET_FEATURES: Final = 0x000D


class EcFeatureCode(Enum):
    """Supported Features"""

    EC_FEATURE_LIMITED = 0
    "This image contains a limited set of features. Another image in RW partition may support more features."

    EC_FEATURE_FLASH = 1
    "Commands for probing/reading/writing/erasing the flash in the EC are present."

    EC_FEATURE_PWM_FAN = 2
    "Can control the fan speed directly."

    EC_FEATURE_PWM_KEYB = 3
    "Can control the intensity of the keyboard backlight."

    EC_FEATURE_LIGHTBAR = 4
    "Support Google lightbar, introduced on Pixel."

    EC_FEATURE_LED = 5
    "Control of LEDs"

    EC_FEATURE_MOTION_SENSE = 6
    """
    Exposes an interface to control gyro and sensors.
    The host goes through the EC to access these sensors.
    In addition, the EC may provide composite sensors, like lid angle.
    """

    EC_FEATURE_KEYB = 7
    "The keyboard is controlled by the EC"

    EC_FEATURE_PSTORE = 8
    "The AP can use part of the EC flash as persistent storage."

    EC_FEATURE_PORT80 = 9
    "The EC monitors BIOS port 80h, and can return POST codes."

    EC_FEATURE_THERMAL = 10
    """
    Thermal management: include TMP specific commands.
    Higher level than direct fan control.
    """

    EC_FEATURE_BKLIGHT_SWITCH = 11
    "Can switch the screen backlight on/off"

    EC_FEATURE_WIFI_SWITCH = 12
    "Can switch the wifi module on/off"

    EC_FEATURE_HOST_EVENTS = 13
    "Monitor host events, through for example SMI or SCI"

    EC_FEATURE_GPIO = 14
    "The EC exposes GPIO commands to control/monitor connected devices."

    EC_FEATURE_I2C = 15
    "The EC can send i2c messages to downstream devices."

    EC_FEATURE_CHARGER = 16
    "Command to control charger are included"

    EC_FEATURE_BATTERY = 17
    "Simple battery support."

    EC_FEATURE_SMART_BATTERY = 18
    """
    Support Smart battery protocol
    (Common Smart Battery System Interface Specification)
    """

    EC_FEATURE_HANG_DETECT = 19
    "EC can detect when the host hangs."

    EC_FEATURE_PMU = 20
    "Report power information, for pit only"

    EC_FEATURE_SUB_MCU = 21
    "Another Cros EC device is present downstream of this one"

    EC_FEATURE_USB_PD = 22
    "Support USB Power delivery (PD) commands"

    EC_FEATURE_USB_MUX = 23
    "Control USB multiplexer, for audio through USB port for instance."

    EC_FEATURE_MOTION_SENSE_FIFO = 24
    "Motion Sensor code has an internal software FIFO"

    EC_FEATURE_VSTORE = 25
    "Support temporary secure vstore"

    EC_FEATURE_USBC_SS_MUX_VIRTUAL = 26
    "EC decides on USB-C SS mux state, muxes configured by host"

    EC_FEATURE_RTC = 27
    "EC has RTC feature that can be controlled by host commands"

    EC_FEATURE_FINGERPRINT = 28
    "The MCU exposes a Fingerprint sensor"

    EC_FEATURE_TOUCHPAD = 29
    "The MCU exposes a Touchpad"

    EC_FEATURE_RWSIG = 30
    "The MCU has RWSIG task enabled"

    EC_FEATURE_DEVICE_EVENT = 31
    "EC has device events support"

    EC_FEATURE_UNIFIED_WAKE_MASKS = 32
    "EC supports the unified wake masks for LPC/eSPI systems"

    EC_FEATURE_HOST_EVENT64 = 33
    "EC supports 64-bit host events"

    EC_FEATURE_EXEC_IN_RAM = 34
    "EC runs code in RAM (not in place, a.k.a. XIP)"

    EC_FEATURE_CEC = 35
    "EC supports CEC commands"

    EC_FEATURE_MOTION_SENSE_TIGHT_TIMESTAMPS = 36
    "EC supports tight sensor timestamping."
    #

    EC_FEATURE_REFINED_TABLET_MODE_HYSTERESIS = 37
    """
    EC supports tablet mode detection aligned to Chrome and allows
    setting of threshold by host command using
    MOTIONSENSE_CMD_TABLET_MODE_LID_ANGLE.
    """

    EC_FEATURE_SCP = 39
    "The MCU is a System Companion Processor (SCP)."

    EC_FEATURE_ISH = 40
    "The MCU is an Integrated Sensor Hub"

    EC_FEATURE_TYPEC_CMD = 41
    "New TCPMv2 TYPEC_ prefaced commands supported"

    EC_FEATURE_TYPEC_REQUIRE_AP_MODE_ENTRY = 42
    "The EC will wait for direction from the AP to enter Type-C alternate modes or USB4."

    EC_FEATURE_TYPEC_MUX_REQUIRE_AP_ACK = 43
    "The EC will wait for an acknowledge from the AP after setting the mux."

    EC_FEATURE_S4_RESIDENCY = 44
    "The EC supports entering and residing in S4."

    EC_FEATURE_TYPEC_AP_MUX_SET = 45
    "The EC supports the AP directing mux sets for the board."

    EC_FEATURE_TYPEC_AP_VDM_SEND = 46
    "The EC supports the AP composing VDMs for us to send."


def get_features(ec: CrosEcClass) -> UInt64:
    """
    List the features supported by the firmware
    :param ec: The CrOS_EC object.
    :return: The features as a bitmask. Use EcFeatureCode to decode.
    """
    resp = ec.command(0, EC_CMD_GET_FEATURES, 0, 8)
    return struct.unpack("<Q", resp)[0]


def decode_features(features: UInt32) -> list[EcFeatureCode]:
    """
    Decode the features bitmask into a list of EcFeatureCode enums
    :param features: The features bitmask.
    :return: The features as a list of EcFeatureCode enums.
    """
    return [feature for feature in EcFeatureCode if features & BIT(feature.value)]
