"""
This module is used to import the correct portio module based on the OS.
"""

import os

if os.name == "posix":
    try:
        from .x86portio import IoPortIo as PortIO
    except ImportError:
        from .devportio import DevPortIO as PortIO
else:
    raise Exception("Unsupported OS")
