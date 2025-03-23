"""
This submodule provides some helper functions to make it easier to use the library.

For example, you can use `get_cros_ec()` instead of manually picking between
`cros_ec_python.devices.lpc.CrosEcLpc` and `cros_ec_python.devices.dev.CrosEcDev`.
"""

import os

from .constants.COMMON import *
from .baseclass import CrosEcClass
from .devices import lpc
if os.name == "posix":
    from .devices import dev
else:
    dev = None


class DeviceTypes(Enum):
    """
    An Enum of different interfaces supported by the library.
    """
    LinuxDev = 0
    """
    This is the Linux device interface, which uses the `/dev/cros_ec` device file.
    *Recommended if you have the `cros_ec_dev` kernel module loaded.*
    """
    LPC = 1
    "This manually talks to the EC over the LPC interface, using the ioports."


def pick_device() -> DeviceTypes:
    """
    Pick the device to use. Used by `get_cros_ec`.
    Devices are picked in the following order:
    * `DeviceTypes.LinuxDev` (see `cros_ec_python.devices.dev.CrosEcDev.detect()`)
    * `DeviceTypes.LPC` (see `cros_ec_python.devices.lpc.CrosEcLpc.detect()`)
    """
    if os.name == "nt":
        # detect only works on Linux for now
        return DeviceTypes.LPC
    elif dev and dev.CrosEcDev.detect():
        return DeviceTypes.LinuxDev
    elif lpc and lpc.CrosEcLpc.detect():
        return DeviceTypes.LPC
    else:
        raise OSError("Could not auto detect device, check you have the required permissions, or specify manually.")


def get_cros_ec(dev_type: DeviceTypes | None = None, **kwargs) -> CrosEcClass:
    """
    Find and initialise the correct CrosEc class.
    This is the recommended way of obtaining a `cros_ec_python.baseclass.CrosEcClass` object.
    :param dev_type: The device type to use. If None, it will be picked automatically.
    :param kwargs: Keyword arguments to pass to the CrosEc class.
    """

    if dev_type is None:
        dev_type = pick_device()

    match dev_type:
        case DeviceTypes.LinuxDev:
            return dev.CrosEcDev(**kwargs)
        case DeviceTypes.LPC:
            return lpc.CrosEcLpc(**kwargs)
        case _:
            raise ValueError("Invalid device type.")
