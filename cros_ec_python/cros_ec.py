from .baseclass import CrosEcClass
from .devices import dev, lpc
from .constants.COMMON import *


class DeviceTypes(Enum):
    LinuxDev = 0
    LPC = 1


def pick_device() -> DeviceTypes:
    """
    Pick the device to use.
    """
    if dev.CrosEcDev.detect():
        return DeviceTypes.LinuxDev
    elif lpc.CrosEcLpc.detect():
        return DeviceTypes.LPC
    else:
        raise OSError("Could not auto detect device, check you have the required permissions, or specify manually.")


def get_cros_ec(dev_type: DeviceTypes | None = None, **kwargs) -> CrosEcClass:
    """
    Find and initialise the correct CrosEc class.
    @param dev_type: The device type to use. If None, it will be picked automatically.
    @param kwargs: Keyword arguments to pass to the CrosEc class.
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
