#!/usr/bin/env python3
from cros_ec_python import get_cros_ec
from cros_ec_python.commands.general import hello

ec = get_cros_ec()

in_data = 42

print("Input:", in_data)

resp = hello(ec, in_data)

print("Raw Response:", resp)
# The Hello command adds 0x01020304 to the input and returns it
# We can subtract this to get the input back
print("Input Echoed:", resp - 0x01020304)
