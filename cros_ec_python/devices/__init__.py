r"""
# Description

The classes for each of the different interfaces supported by the library live in this submodule.

If you don't understand what this does, just use `cros_ec_python.cros_ec.get_cros_ec()` to pick an interface.

All device class implementations should inherit from `cros_ec_python.baseclass.CrosEcClass`,
and implement the methods described in that class. This allows everyone to use the standardised
`cros_ec_python.baseclass.CrosEcClass.command` method to send commands to the EC, and
`cros_ec_python.baseclass.CrosEcClass.memmap` to read memory from the EC.

Devices can have optional specific arguments in their `__init__` method, but other methods should be the same.

## Examples

**Initialisation**

```python
from cros_ec_python import get_cros_ec, CrosEcLpc, CrosEcDev

# Pick one of the following:

# Automatically pick the right class
ec = get_cros_ec()

# Manually pick LinuxDev
ec = CrosEcDev()

# Manually pick LPC
ec = CrosEcLpc()

# Manually pick LPC with a specific address
ec = CrosEcLpc(address=0xE00)
```

**Sending a command** (See `cros_ec_python.commands` for easier to use abstractions)

```python
from cros_ec_python import general
# Assuming `ec` is already initialised

data = b'\xa0\xb0\xc0\xd0'

resp = ec.command(0, general.EC_CMD_HELLO, len(data), 4, data)
print(resp)

# Output should equal b'\xa4\xb3\xc2\xd1'
assert resp == b'\xa4\xb3\xc2\xd1'
```

**Reading the memmap** (See `cros_ec_python.commands.memmap` for easier to use abstractions)

```python
from cros_ec_python.constants import MEMMAP
# Assuming `ec` is already initialised

resp = ec.memmap(MEMMAP.EC_MEMMAP_ID, 2)
print(resp)

# Output should equal b'EC'
assert resp == b'EC'
```
"""
