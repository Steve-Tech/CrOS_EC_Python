from fcntl import ioctl
import struct
from typing import Final
from sys import stderr
from .constants.COMMON import *

CROS_EC_IOC_MAGIC: Final = 0xEC

readmem_ioctl = True


def _IOC(dir: int, type: int, nr: int, size: int):
    """
    Create an ioctl command number.
    Based on the Linux kernel's include/uapi/asm-generic/ioctl.h.
    """
    nr_bits, type_bits, size_bits, dir_bits = 8, 8, 14, 2
    nr_shift = 0
    type_shift = nr_shift + nr_bits
    size_shift = type_shift + type_bits
    dir_shift = size_shift + size_bits

    return dir << dir_shift | size << size_shift | type << type_shift | nr << nr_shift


def _IORW(type: int, nr: int, size: int):
    """
    Create an ioctl command number for read/write commands.
    Based on the Linux kernel's include/uapi/asm-generic/ioctl.h.
    """
    none = 0
    write = 1
    read = 2
    return _IOC((read | write), type, nr, size)


def ec_command_fd(
        fd, version: Int32, command: Int32, outsize: Int32, insize: Int32, data: bytes = None
) -> bytes:
    """Send a command to the EC and return the response.
    @param fd: File descriptor for the EC device.
    @param version: Command version number (often 0).
    @param command: Command to send (EC_CMD_...).
    @param outsize: Outgoing length in bytes.
    @param insize: Max number of bytes to accept from the EC.
    @param data: Outgoing data to EC.
    @return: Incoming data from EC.
    """
    if data is None:
        data = bytes(outsize)

    cmd = struct.pack(f"<IIIII", version, command, outsize, insize, 0xFF)
    buf = bytearray(cmd + bytes(max(outsize, insize)))
    buf[len(cmd): len(cmd) + outsize] = data

    CROS_EC_DEV_IOCXCMD = _IORW(CROS_EC_IOC_MAGIC, 0, len(cmd))
    result = ioctl(fd, CROS_EC_DEV_IOCXCMD, buf)

    if result < 0:
        raise IOError(f"ioctl failed with error {result}")

    if result != insize:
        print(f"WARNING: expected {insize} bytes, got {result}", file=stderr)

    return bytes(buf[len(cmd): len(cmd) + insize])


def ec_command(
        version: Int32, command: Int32, outsize: Int32, insize: Int32, data: bytes = None
) -> bytes:
    """
    Send a command to the EC and return the response.
    @param version: Command version number (often 0).
    @param command: Command to send (EC_CMD_...).
    @param outsize: Outgoing length in bytes.
    @param insize: Max number of bytes to accept from the EC. None for unlimited.
    @param data: Outgoing data to EC.
    @return: Incoming data from EC.
    """
    with open("/dev/cros_ec", "wb") as fd:
        return ec_command_fd(fd, version, command, outsize, insize, data)


def ec_readmem_fd(fd, offset: Int32, num_bytes: Int32) -> bytes:
    """
    Read memory from the EC.
    @param fd: File descriptor for the EC device.
    @param offset: Offset to read from.
    @param num_bytes: Number of bytes to read.
    @return: Bytes read from the EC.
    """
    global readmem_ioctl
    EC_MEMMAP_SIZE = 255
    if readmem_ioctl:
        data = struct.pack("<II", offset, num_bytes)
        buf = bytearray(data + bytes(num_bytes))
        CROS_EC_DEV_IOCRDMEM = _IORW(
            CROS_EC_IOC_MAGIC, 1, len(data) + EC_MEMMAP_SIZE + 1
        )
        try:
            result = ioctl(fd, CROS_EC_DEV_IOCRDMEM, buf)

            if result < 0:
                raise IOError(f"ioctl failed with error {result}")

            if result != num_bytes:
                print(f"WARNING: expected {num_bytes} bytes, got {result}", file=stderr)

            return buf[len(data): len(data) + num_bytes]
        except OSError as e:
            if e.errno == 25:
                print(e)
                readmem_ioctl = False
                return ec_readmem_fd(fd, offset, num_bytes)
            else:
                raise e
    else:
        # This is untested!
        data = struct.pack("<BB", offset, num_bytes)
        buf = ec_command(0, 0x07, len(data), num_bytes, data)
        return buf[len(data): len(data) + num_bytes]


def ec_readmem(offset: Int32, num_bytes: Int32) -> bytes:
    """
    Read memory from the EC.
    @param offset: Offset to read from.
    @param num_bytes: Number of bytes to read.
    @return: Bytes read from the EC.
    """
    with open("/dev/cros_ec", "wb") as fd:
        return ec_readmem_fd(fd, offset, num_bytes)
