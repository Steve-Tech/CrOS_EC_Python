from typing import Final
from ..cros_ec import CrOS_EC
from ..constants.COMMON import *
import struct

EC_CMD_HELLO: Final = 0x0001


def hello(ec: CrOS_EC, in_data: UInt32) -> UInt32:
    """
    Hello.  This is a simple command to test the EC is responsive to commands.
    @param ec: The CrOS_EC object.
    @param in_data: Pass anything here. Max value is 0xFFFFFFFF (uint32).
    @return: Output will be in_data + 0x01020304.
    """
    data = struct.pack("<I", in_data)
    resp = ec.command(0, EC_CMD_HELLO, len(data), 4, data)
    return struct.unpack("<I", resp)[0]
