"""
Framework Laptop specific commands.
"""

from typing import Final, Literal
from enum import Enum
import struct
from datetime import timedelta
from ..baseclass import CrosEcClass
from ..constants.COMMON import *


EC_CMD_FLASH_NOTIFIED: Final = 0x3E01

EC_CMD_FACTORY_MODE: Final = 0x3E02

EC_CMD_CHARGE_LIMIT_CONTROL: Final = 0x3E03


class ChargeLimitControlModes(Enum):
    CHG_LIMIT_DISABLE = BIT(0)
    CHG_LIMIT_SET_LIMIT = BIT(1)
    CHG_LIMIT_GET_LIMIT = BIT(3)
    CHG_LIMIT_OVERRIDE = BIT(7)


def disable_charge_limit(ec: CrosEcClass) -> None:
    """
    Disables the charge limit.
    :param ec: The CrOS_EC object.
    """
    data = struct.pack("<Bxx", ChargeLimitControlModes.CHG_LIMIT_DISABLE.value)
    ec.command(0, EC_CMD_CHARGE_LIMIT_CONTROL, 3, 0, data)


def get_charge_limit(ec: CrosEcClass) -> tuple[UInt8, UInt8]:
    """
    Gets the charge limit.
    :param ec: The CrOS_EC object.
    :return: The charge limit as a tuple (max, min).
    """
    data = struct.pack("<Bxx", ChargeLimitControlModes.CHG_LIMIT_GET_LIMIT.value)
    resp = ec.command(0, EC_CMD_CHARGE_LIMIT_CONTROL, 3, 2, data)
    return struct.unpack("<BB", resp)


def set_charge_limit(ec: CrosEcClass, max: UInt8, min: UInt8) -> None:
    """
    Sets the charge limit.
    :param ec: The CrOS_EC object.
    :param limit: The charge limit.
    """
    data = struct.pack(
        "<BBB", ChargeLimitControlModes.CHG_LIMIT_SET_LIMIT.value, max, min
    )
    ec.command(0, EC_CMD_CHARGE_LIMIT_CONTROL, 3, 0, data)


def override_charge_limit(ec: CrosEcClass) -> None:
    """
    Overrides the charge limit to full for a single charge cycle.
    :param ec: The CrOS_EC object.
    :param limit: The charge limit.
    """
    data = struct.pack("<Bxx", ChargeLimitControlModes.CHG_LIMIT_OVERRIDE.value)
    ec.command(0, EC_CMD_CHARGE_LIMIT_CONTROL, 3, 0, data)


EC_CMD_PWM_GET_FAN_ACTUAL_RPM: Final = 0x3E04


def pwm_get_fan_rpm(ec: CrosEcClass, index: UInt8 = 0) -> UInt16:
    """
    Get fan RPM (Same value as `cros_ec_python.commands.memmap.get_fans`)
    :param ec: The CrOS_EC object.
    :param index: The fan index to get the RPM for.
    :return: The current fan RPM.
    """
    data = struct.pack("<B", index)
    resp = ec.command(0, EC_CMD_PWM_GET_FAN_ACTUAL_RPM, 1, 2, data)
    return struct.unpack("<H", resp)[0]


EC_CMD_SET_AP_REBOOT_DELAY: Final = 0x3E05

EC_CMD_ME_CONTROL: Final = 0x3E06

EC_CMD_NON_ACPI_NOTIFY: Final = 0x3E07

EC_CMD_DISABLE_PS2_EMULATION: Final = 0x3E08

EC_CMD_CHASSIS_INTRUSION: Final = 0x3E09


def get_chassis_intrusion(
    ec: CrosEcClass, clear_magic: UInt8 = 0, clear_chassis_status: UInt8 = 0
) -> dict[bool | UInt8]:
    """
    Get chassis intrusion status. It is recommended to leave the other parameters empty.
    :param ec: The CrOS_EC object.
    :param clear_magic: If `0xCE` then all chassis data is cleared.
    :param clear_chassis_status: If not `0`, then `chassis_ever_opened` is cleared.
    :return: The chassis intrusion status. `chassis_ever_opened` is True if the chassis has ever been opened, `coin_batt_ever_remove` is True if the coin battery has ever been removed, `total_open_count` is the total number of times the chassis has been opened, and `vtr_open_count` is the number of times the chassis has been opened with only RTC power.
    """
    data = struct.pack("<BB", clear_magic, clear_chassis_status)
    resp = ec.command(0, EC_CMD_CHASSIS_INTRUSION, 2, 4, data)
    unpacked = struct.unpack("<?BBB", resp)
    return {
        "chassis_ever_opened": unpacked[0],
        "coin_batt_ever_remove": unpacked[1],
        "total_open_count": unpacked[2],
        "vtr_open_count": unpacked[3],
    }


EC_CMD_BB_RETIMER_CONTROL: Final = 0x3E0A

EC_CMD_DIAGNOSIS: Final = 0x3E0B

EC_CMD_UPDATE_KEYBOARD_MATRIX: Final = 0x3E0C

EC_CMD_VPRO_CONTROL: Final = 0x3E0D

EC_CMD_FP_LED_LEVEL_CONTROL: Final = 0x3E0E


class FpLedBrightnessLevel(Enum):
    FP_LED_BRIGHTNESS_LEVEL_HIGH = 0
    FP_LED_BRIGHTNESS_LEVEL_MEDIUM = 1
    FP_LED_BRIGHTNESS_LEVEL_LOW = 2


def set_fp_led_level(ec: CrosEcClass, level: FpLedBrightnessLevel | int) -> None:
    """
    Set the fingerprint LED level.
    :param ec: The CrOS_EC object.
    :param level: The level to set the fingerprint LED to.
    """
    if isinstance(level, FpLedBrightnessLevel):
        level = level.value
    data = struct.pack("<Bx", level)
    ec.command(0, EC_CMD_FP_LED_LEVEL_CONTROL, 2, 0, data)


def get_fp_led_level_int(ec: CrosEcClass) -> UInt8:
    """
    Get the raw fingerprint LED level.
    :param ec: The CrOS_EC object.
    :return: The current fingerprint LED level.
    """
    data = struct.pack("<xB", 1)
    resp = ec.command(0, EC_CMD_FP_LED_LEVEL_CONTROL, 2, 1, data)
    return struct.unpack("<B", resp)[0]


def get_fp_led_level(ec: CrosEcClass) -> FpLedBrightnessLevel:
    """
    Get the fingerprint LED level.
    :param ec: The CrOS_EC object.
    :return: The current fingerprint LED level.
    """
    match level := get_fp_led_level_int(ec):
        case 55:
            return FpLedBrightnessLevel.FP_LED_BRIGHTNESS_LEVEL_HIGH
        case 40:
            return FpLedBrightnessLevel.FP_LED_BRIGHTNESS_LEVEL_MEDIUM
        case 15:
            return FpLedBrightnessLevel.FP_LED_BRIGHTNESS_LEVEL_LOW
        case _:
            raise ValueError(f"Invalid fingerprint LED level ({level})")


EC_CMD_CHASSIS_OPEN_CHECK: Final = 0x3E0F


def get_chassis_open_check(ec: CrosEcClass) -> bool:
    """
    Check if the chassis is currently open.
    :param ec: The CrOS_EC object.
    :return: True if the chassis is open, False if it is closed.
    """
    resp = ec.command(0, EC_CMD_CHASSIS_OPEN_CHECK, 0, 1)
    return struct.unpack("<?", resp)[0]


EC_CMD_ACPI_NOTIFY: Final = 0x3E10

EC_CMD_READ_PD_VERSION: Final = 0x3E11

EC_CMD_THERMAL_QEVENT: Final = 0x3E12

EC_CMD_STANDALONE_MODE: Final = 0x3E13

EC_CMD_PRIVACY_SWITCHES_CHECK_MODE: Final = 0x3E14


def get_privacy_switches(ec: CrosEcClass) -> dict[bool]:
    """
    Get the privacy switches status.
    :param ec: The CrOS_EC object.
    :return: The device status. True if enabled, False if disabled.
    """
    resp = ec.command(0, EC_CMD_PRIVACY_SWITCHES_CHECK_MODE, 0, 2)
    unpacked = struct.unpack("<??", resp)
    return {
        "microphone": unpacked[0],
        "camera": unpacked[1],
    }


EC_CMD_CHASSIS_COUNTER: Final = 0x3E15


def get_chassis_counter(ec: CrosEcClass) -> UInt8:
    """
    Get the amount of times the chassis has been opened while the EC has power.
    Clears on reboot and on read, use `get_chassis_intrusion` for persistent data.
    :param ec: The CrOS_EC object.
    :return: The chassis counter.
    """
    resp = ec.command(0, EC_CMD_CHASSIS_COUNTER, 0, 1)
    return struct.unpack("<B", resp)[0]


EC_CMD_CHECK_DECK_STATE: Final = 0x3E16

EC_CMD_GET_SIMPLE_VERSION: Final = 0x3E17


def get_simple_version(ec: CrosEcClass) -> str:
    """
    Get the simple ec version.
    :param ec: The CrOS_EC object.
    :return: The simple version as a string.
    """
    resp = ec.command(0, EC_CMD_GET_SIMPLE_VERSION, 0, 9)
    return resp.decode("utf-8").rstrip("\x00")


EC_CMD_GET_ACTIVE_CHARGE_PD_CHIP: Final = 0x3E18


def get_active_charge_pd_chip(ec: CrosEcClass) -> UInt8:
    """
    Get the active charge PD chip.
    :param ec: The CrOS_EC object.
    :return: The active charge PD chip.
    """
    resp = ec.command(0, EC_CMD_GET_ACTIVE_CHARGE_PD_CHIP, 0, 1)
    return struct.unpack("<B", resp)[0]


EC_CMD_UEFI_APP_MODE: Final = 0x3E19

EC_CMD_UEFI_APP_BTN_STATUS: Final = 0x3E1A

EC_CMD_EXPANSION_BAY_STATUS: Final = 0x3E1B

EC_CMD_GET_HW_DIAG: Final = 0x3E1C

EC_CMD_GET_GPU_SERIAL: Final = 0x3E1D


def get_gpu_serial(ec: CrosEcClass, idx: UInt8 = 0) -> dict[UInt8 | bool | str]:
    """
    Get the GPU serial. [Untested]
    :param ec: The CrOS_EC object.
    :return: The GPU serial as a string.
    """
    data = struct.pack("<B", idx)
    resp = ec.command(0, EC_CMD_GET_GPU_SERIAL, 1, 22, data)
    unpacked = struct.unpack("<B?20s", resp)
    return {
        "idx": unpacked[0],
        "valid": unpacked[1],
        "serial": unpacked[2].decode("utf-8").rstrip("\x00"),
    }


EC_CMD_GET_GPU_PCIE: Final = 0x3E1E


class GpuPcieConfig(Enum):
    PCIE_8X1 = 0
    PCIE_4X1 = 1
    PCIE_4X2 = 2


class GpuPcieVendor(Enum):
    GPU_AMD_R23 = 0
    GPU_PCIE_ACCESSORY = 0xFF


def get_gpu_pcie(ec: CrosEcClass) -> dict[GpuPcieConfig | GpuPcieVendor | UInt8]:
    """
    Get the PCIe configuration of the GPU module. [Untested]
    :param ec: The CrOS_EC object.
    :return: The GPU PCIe configuration and vendor.
    """
    resp = ec.command(0, EC_CMD_GET_GPU_PCIE, 0, 2)
    gpu_pcie_config = GpuPcieConfig(resp[0])
    gpu_vendor = (
        GpuPcieVendor(resp[1]) if resp[1] in GpuPcieVendor._value2member_map_ else None
    )

    return {"gpu_pcie_config": gpu_pcie_config, "gpu_vendor": gpu_vendor}


EC_CMD_PROGRAM_GPU_EEPROM: Final = 0x3E1F

EC_CMD_FP_CONTROL: Final = 0x3E20


def fp_control(ec: CrosEcClass, enable: bool) -> None:
    """
    Enable or disable the fingerprint sensor. [Untested]
    :param ec: The CrOS_EC object.
    :param enable: True to enable the fingerprint sensor, False to disable it.
    """
    data = struct.pack("<?", enable)
    ec.command(0, EC_CMD_FP_CONTROL, 1, 0, data)


# This doesn't seem to be implemented
EC_CMD_GET_CUTOFF_STATUS: Final = 0x3E21

EC_CMD_BATTERY_EXTENDER: Final = 0x3E24


def get_battery_extender(ec: CrosEcClass) -> dict[UInt8 | UInt16 | bool | timedelta]:
    """
    Get the battery extender status.
    :param ec: The CrOS_EC object.
    :return: The battery extender status. `current_stage` is the current stage of the battery extender (0-2), `trigger_days` is the number of days on charge before reducing the charge limit, `reset_minutes` is the number of minutes off charge before resetting the charge limit, `disable` is True if the battery extender is disabled, `trigger_timedelta` is the timedelta before reducing the charge limit, and `reset_timedelta` is the timedelta before resetting the charge limit.
    """
    # 1 for read
    data = struct.pack("<xxxxBx", 1)
    resp = ec.command(0, EC_CMD_BATTERY_EXTENDER, 6, 22, data)
    unpacked = struct.unpack("<BHH?QQ", resp)
    return {
        "current_stage": unpacked[0],
        "trigger_days": unpacked[1],
        "reset_minutes": unpacked[2],
        "disable": unpacked[3],
        "trigger_timedelta": timedelta(microseconds=unpacked[4]),
        "reset_timedelta": timedelta(microseconds=unpacked[5]),
    }


def set_battery_extender(
    ec: CrosEcClass, disable: bool, trigger_days: UInt8 = 0, reset_minutes: UInt16 = 0
) -> None:
    """
    Set the battery extender status.
    :param ec: The CrOS_EC object.
    :param disable: True to disable the battery extender, False to enable it.
    :param trigger_days: The number of days on charge before reducing the charge limit. Values less than 1 or greater than 99 will be ignored.
    :param reset_minutes: The number of minutes off charge before resetting the charge limit. Values less than 1 or greater than 9999 will be ignored.
    """
    # 0 for write
    data = struct.pack("<?BHBx", disable, trigger_days, reset_minutes, 0)
    ec.command(0, EC_CMD_BATTERY_EXTENDER, 6, 0, data)
