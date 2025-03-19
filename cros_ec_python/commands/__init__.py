"""
# Description

This submodule contains commands that have been abstracted into a python function for easier use.

Each command has been split into separate categories for easier maintainability.

The original command values are also present in these files.

## Format & Example

Each command is a function that takes a `cros_ec_python.baseclass.CrosEcClass` object as the first argument,
and any other arguments that are required.

**For example:**

```python
from cros_ec_python import get_cros_ec, general

ec = get_cros_ec()

in_data = 42

print("Input:", in_data)

# We will run the `hello` command here:
# The first argument is the object of the EC, and the second is the input data.
resp = general.hello(ec, in_data)

print("Raw Response:", resp)
# The Hello command adds 0x01020304 to the input and returns it
# We can subtract this to get the input back
print("Input Echoed:", resp - 0x01020304)
```
"""
