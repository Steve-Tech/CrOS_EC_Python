import errno
from fcntl import ioctl
import struct
from typing import Final, IO
import warnings
import os

from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..constants.MEMMAP import EC_MEMMAP_SIZE
from ..commands.general import EC_CMD_READ_MEMMAP
from ..exceptions import ECError

__all__ = ["CrosEcDev"]

CROS_EC_IOC_MAGIC: Final = 0xEC


def IOC(dir: int, type: int, nr: int, size: int):
    """
    Create an ioctl command number.
    Based on the Linux kernels include/uapi/asm-generic/ioctl.h.
    """
    nr_bits, type_bits, size_bits, dir_bits = 8, 8, 14, 2
    nr_shift = 0
    type_shift = nr_shift + nr_bits
    size_shift = type_shift + type_bits
    dir_shift = size_shift + size_bits

    return dir << dir_shift | size << size_shift | type << type_shift | nr << nr_shift


def IORW(type: int, nr: int, size: int):
    """
    Create an ioctl command number for read/write commands.
    Based on the Linux kernels include/uapi/asm-generic/ioctl.h.
    """
    none = 0
    write = 1
    read = 2
    return IOC((read | write), type, nr, size)


class CrosEcDev(CrosEcClass):
    """
    Class to interact with the EC using the Linux cros_ec device.
    """

    def __init__(self, fd: IO | None = None, memmap_ioctl: bool = True):
        """
        Initialise the EC using the Linux cros_ec device.
        :param fd: Use a custom file description, opens /dev/cros_ec by default.
        :param memmap_ioctl: Use ioctl for memmap (default), if False the READ_MEMMAP command will be used instead.
        """
        if fd is None:
            fd = open("/dev/cros_ec", "wb", buffering=0)

        self.fd: IO = fd
        """The file descriptor for /dev/cros_ec."""

        self.memmap_ioctl: bool = memmap_ioctl
        """Use ioctl for memmap, if False the READ_MEMMAP command will be used instead."""

    def __del__(self):
        self.ec_exit()

    @staticmethod
    def detect() -> bool:
        """
        Checks for `/dev/cros_ec` and returns True if it exists.
        """
        return os.path.exists("/dev/cros_ec")

    def ec_init(self) -> None:
        pass

    def ec_exit(self) -> None:
        """
        Close the file on exit.
        """
        if hasattr(self, "fd"):
            self.fd.close()

    def command(
            self, version: Int32, command: Int32, outsize: Int32, insize: Int32, data: bytes = None, warn: bool = True
    ) -> bytes:
        """
        Send a command to the EC and return the response.
        :param version: Command version number (often 0).
        :param command: Command to send (EC_CMD_...).
        :param outsize: Outgoing length in bytes.
        :param insize: Max number of bytes to accept from the EC.
        :param data: Outgoing data to EC.
        :param warn: Whether to warn if the response size is not as expected. Default is True.
        :return: Incoming data from EC.
        """
        if data is None:
            data = bytes(outsize)

        cmd = struct.pack(f"<IIIII", version, command, outsize, insize, 0xFF)
        buf = bytearray(cmd + bytes(max(outsize, insize)))
        buf[len(cmd): len(cmd) + outsize] = data

        CROS_EC_DEV_IOCXCMD = IORW(CROS_EC_IOC_MAGIC, 0, len(cmd))
        result = ioctl(self.fd, CROS_EC_DEV_IOCXCMD, buf)

        if result < 0:
            raise IOError(f"ioctl failed with error {result}")

        ec_result = struct.unpack("<IIIII", buf[:len(cmd)])

        if ec_result[4] != 0:
            raise ECError(ec_result[4])

        if result != insize and warn:
            warnings.warn(f"Expected {insize} bytes, got {result} back from EC", RuntimeWarning)

        return bytes(buf[len(cmd): len(cmd) + insize])

    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        :param offset: Offset to read from.
        :param num_bytes: Number of bytes to read.
        :return: Bytes read from the EC.
        """
        if self.memmap_ioctl:
            data = struct.pack("<II", offset, num_bytes)
            buf = bytearray(data + bytes(num_bytes))
            CROS_EC_DEV_IOCRDMEM = IORW(
                CROS_EC_IOC_MAGIC, 1, len(data) + EC_MEMMAP_SIZE + 1
            )
            try:
                result = ioctl(self.fd, CROS_EC_DEV_IOCRDMEM, buf)

                if result < 0:
                    raise IOError(f"ioctl failed with error {result}")

                if result != num_bytes:
                    warnings.warn(f"Expected {num_bytes} bytes, got {result} back from EC", RuntimeWarning)

                return buf[len(data): len(data) + num_bytes]
            except OSError as e:
                if e.errno == errno.ENOTTY:
                    warnings.warn("ioctl failed, falling back to READ_MEMMAP command", RuntimeWarning)
                    self.memmap_ioctl = False
                    return self.memmap(offset, num_bytes)
                else:
                    raise e
        else:
            # This is untested!
            data = struct.pack("<BB", offset, num_bytes)
            buf = self.command(0, EC_CMD_READ_MEMMAP, len(data), num_bytes, data)
            return buf[len(data): len(data) + num_bytes]
