"""
# Description

This submodule contains the classes for the different IO port interfaces supported by the library.

If you don't understand what this does, just use `cros_ec_python.ioports.PortIO()` to import the correct class.

All IO port classes should inherit from `cros_ec_python.ioports.baseportio.PortIOClass`,
and implement the methods described in that class. This allows everything to use the standardised
methods to interact with the IO ports in a platform-independent way.

## Examples

**Initialisation**

```python
# Automatically pick the right class (Recommended)
from cros_ec_python.ioports import PortIO
portio = PortIO()

# Manually pick portio library (Linux, preferred)
from cros_ec_python.ioports.x86portio import IoPortIo
portio = IoPortIo()

# Manually pick `/dev/port` (Linux, fallback)
from cros_ec_python.ioports.devportio import DevPortIO
portio = DevPortIO()

# Manually pick WinRing0 (Windows)
from cros_ec_python.ioports.winportio import WinPortIO
portio = WinPortIO()

# Manually pick `/dev/io` (FreeBSD)
from cros_ec_python.ioports.freebsdportio import FreeBsdPortIO
portio = FreeBsdPortIO()
```

**Reading from a port**

```python
# Assuming `portio` is already initialised
data = portio.inb(0x80)
print(data)
```

**Writing to a port**

```python
# Assuming `portio` is already initialised
portio.outb(0x55, 0x80)
```

See `cros_ec_python.ioports.baseportio.PortIOClass` for the full list of common methods.

Some classes may have additional methods, such as `cros_ec_python.ioports.x86portio.IoPortIo`.
"""

import sys

if sys.platform == "linux":
    try:
        from .x86portio import IoPortIo as PortIO
    except ImportError:
        from .devportio import DevPortIO as PortIO
elif sys.platform == "win32":
    from .winportio import WinPortIO as PortIO
elif sys.platform.startswith("freebsd"):
    from .freebsdportio import FreeBsdPortIO as PortIO
else:
    raise Exception("Unsupported OS")

# This is for pdoc
from .baseportio import PortIOClass

PortIO: PortIOClass
"Automatically picked IO port class."
