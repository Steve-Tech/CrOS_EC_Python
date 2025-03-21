"""
.. include:: ../README.md
"""

from .cros_ec import get_cros_ec, DeviceTypes
from .baseclass import CrosEcClass
from .commands import memmap, general, features, pwm, leds, thermal, framework_laptop
from .exceptions import ECError
from .devices.lpc import CrosEcLpc
if __import__("os").name == "posix":
    from .devices.dev import CrosEcDev
