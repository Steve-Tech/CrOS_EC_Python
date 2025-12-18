"""
General / test commands
"""

from typing import Final, Literal
import struct
from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..exceptions import ECError

EC_CMD_PROTO_VERSION: Final = 0x0000


def proto_version(ec: CrosEcClass) -> UInt32:
    """
    Get protocol version, used to deal with non-backward compatible protocol changes.
    :param ec: The CrOS_EC object.
    :return: The protocol version as a uint32.
    """
    resp = ec.command(0, EC_CMD_PROTO_VERSION, 0, 4)
    return struct.unpack("<I", resp)[0]


EC_CMD_HELLO: Final = 0x0001


def hello(ec: CrosEcClass, in_data: UInt32) -> UInt32:
    """
    Hello.  This is a simple command to test the EC is responsive to commands.
    :param ec: The CrOS_EC object.
    :param in_data: Pass anything here. Max value is 0xFFFFFFFF (uint32).
    :return: Output will be in_data + 0x01020304.
    """
    data = struct.pack("<I", in_data)
    resp = ec.command(0, EC_CMD_HELLO, len(data), 4, data)
    return struct.unpack("<I", resp)[0]


EC_CMD_GET_VERSION: Final = 0x0002


def get_version(ec: CrosEcClass, version: Literal[0, 1] = 0) -> dict[str, str | int]:
    """
    Get version number
    :param ec: The CrOS_EC object.
    :param version: The command version to use. Default is 0.
    :return: The EC version as strings, and the RW status.
    """
    match version:
        case 0:
            resp = ec.command(version, EC_CMD_GET_VERSION, 0, 32 + 32 + 32 + 4)
            unpacked = struct.unpack("<32s32s32sI", resp)
            return {
                "version_string_ro": unpacked[0].decode("utf-8").rstrip("\x00"),
                "version_string_rw": unpacked[1].decode("utf-8").rstrip("\x00"),
                "reserved": unpacked[2].decode("utf-8").rstrip("\x00"),
                "current_image": unpacked[3]
            }
        case 1:
            resp = ec.command(version, EC_CMD_GET_VERSION, 0, 32 + 32 + 32 + 4 + 32)
            unpacked = struct.unpack("<32s32s32sI32s", resp)
            return {
                "version_string_ro": unpacked[0].decode("utf-8").rstrip("\x00"),
                "version_string_rw": unpacked[1].decode("utf-8").rstrip("\x00"),
                "cros_fwid_ro": unpacked[2].decode("utf-8").rstrip("\x00"),
                "current_image": unpacked[3],
                "crod_fwid_rw": unpacked[4].decode("utf-8").rstrip("\x00")
            }
        case _:
            raise NotImplementedError


# Read test - OBSOLETE
EC_CMD_READ_TEST: Final = 0x0003

EC_CMD_GET_BUILD_INFO: Final = 0x0004


def get_build_info(ec: CrosEcClass) -> str:
    """
    Get build information
    :param ec: The CrOS_EC object.
    :return: The build info as a string.
    """
    # 0xEC is the max command size on some platforms
    resp = ec.command(0, EC_CMD_GET_BUILD_INFO, 0, 0xEC, warn=False)
    return resp.decode("utf-8").rstrip("\x00")


EC_CMD_GET_CHIP_INFO: Final = 0x0005


def get_chip_info(ec: CrosEcClass) -> dict[str, str]:
    """
    Get chip info
    :param ec: The CrOS_EC object.
    :return: The chip vendor, name, and revision as strings.
    """
    resp = ec.command(0, EC_CMD_GET_CHIP_INFO, 0, 32 + 32 + 32)
    unpacked = struct.unpack("<32s32s32s", resp)
    return {
        "vendor": unpacked[0].decode("utf-8").rstrip("\x00"),
        "name": unpacked[1].decode("utf-8").rstrip("\x00"),
        "revision": unpacked[2].decode("utf-8").rstrip("\x00")
    }


EC_CMD_GET_BOARD_VERSION: Final = 0x0006


def get_board_version(ec: CrosEcClass) -> UInt16:
    """
    Get board HW version
    :param ec: The CrOS_EC object.
    :return: The board version as a uint16.
    """
    resp = ec.command(0, EC_CMD_GET_BOARD_VERSION, 0, 2)
    return struct.unpack("<H", resp)[0]


# use the CrOS_EC.memmap method instead
EC_CMD_READ_MEMMAP: Final = 0x0007

EC_CMD_GET_CMD_VERSIONS: Final = 0x0008


def get_cmd_versions(ec: CrosEcClass, cmd: UInt8 | UInt16, version: Literal[0, 1] | None = None) -> UInt32 | None:
    """
    Read versions supported for a command.
    :param ec: The CrOS_EC object.
    :param cmd: The command to get the supported versions of.
    :param version: The command version to use. Default is guess. 0 supports 8 bit commands, 1 supports 16 bit commands.
    :return: The supported versions as a bitmask. Bit 0 is version 0, bit 1 is version 1, etc. None if the command is not supported.
    """
    if version is None:
        version = int(cmd > 0xFF)
    try:
        match version:
            case 0:
                resp = ec.command(version, EC_CMD_GET_CMD_VERSIONS, 1, 4, struct.pack("<B", cmd))
                return struct.unpack("<I", resp)[0]
            case 1:
                resp = ec.command(version, EC_CMD_GET_CMD_VERSIONS, 2, 4, struct.pack("<H", cmd))
                return struct.unpack("<I", resp)[0]
            case _:
                raise NotImplementedError
    except ECError as e:
        # EC_CMD_GET_CMD_VERSIONS throws EC_RES_INVALID_PARAM if the command is not supported
        # Catch this and return None
        if e.status == EcStatus.EC_RES_INVALID_PARAM.value:
            return None
        # Otherwise, raise the exception
        raise e

def check_cmd_version(ec: CrosEcClass, cmd: UInt8 | UInt16, version: int) -> bool:
    """
    Check if a command supports a specific version.
    :param ec: The CrOS_EC object.
    :param cmd: The command to check.
    :param version: The version to check for.
    :return: True if the command supports the version, False otherwise.
    """
    supported_versions = get_cmd_versions(ec, cmd)
    if supported_versions is None:
        return False
    return (supported_versions & (1 << version)) != 0

EC_CMD_GET_COMMS_STATUS: Final = 0x0009

EC_CMD_TEST_PROTOCOL: Final = 0x000A


def test_protocol(ec: CrosEcClass, result: UInt32, ret_len: UInt32, buf: bytes, in_size: Int32 | None = None) -> bytes:
    """
    Fake a variety of responses, purely for testing purposes.
    :param ec: The CrOS_EC object.
    :param result: Result for the EC to return.
    :param ret_len: Length of return data.
    :param buf: Data to return. Max length is 32 bytes.
    :param in_size: Max number of bytes to accept from the EC. None to use ret_len.
    :return: The data returned.
    """
    data = struct.pack("<II", result, ret_len) + buf
    resp = ec.command(0, EC_CMD_TEST_PROTOCOL, len(data), in_size or ret_len, data)
    return resp


EC_CMD_GET_PROTOCOL_INFO: Final = 0x000B


def get_protocol_info(ec: CrosEcClass) -> dict[str, int]:
    """
    Get protocol info
    :param ec: The CrOS_EC object.
    :return: The protocol info as a dictionary.
    """
    resp = ec.command(0, EC_CMD_GET_PROTOCOL_INFO, 0, 12)
    unpacked = struct.unpack("<IHHI", resp)
    return {
        "protocol_versions": unpacked[0],
        "max_request_packet_size": unpacked[1],
        "max_response_packet_size": unpacked[2],
        "flags": unpacked[3]
    }
