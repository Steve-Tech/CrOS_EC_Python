# CrOS_EC_Python

A Python library for interacting with a Chrome OS EC.

Right now, this library is in a very early stage of development. It's not very easy to use, and wrong usage can brick your device. Use at your own risk.

View `fw_example.py` for example usage for Framework laptops.

The List of commands and their parameters can be found online, but knowledge of EC communication is basically required to use this library.
- [CrOS EC Commands](https://source.chromium.org/chromium/chromiumos/platform/ec/+/main:include/ec_commands.h)
- [Framework Laptop Specific Commands](https://github.com/FrameworkComputer/EmbeddedController/blob/hx20-hx30/board/hx30/host_command_customization.h) & [More Here](https://github.com/FrameworkComputer/EmbeddedController/blob/hx20-hx30/baseboard/fwk/baseboard_host_commands.h)