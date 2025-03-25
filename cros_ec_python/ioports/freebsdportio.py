"""
This file provides a way to interact with the `/dev/io` device file on
FreeBSD.
"""

from typing import Final, IO
from fcntl import ioctl
import struct

from .baseportio import PortIOClass

IODEV_PIO_READ: Final = 0
IODEV_PIO_WRITE: Final = 1


def _IOC(inout: int, group: str, num: int, length: int):
    """
    Create an ioctl command number.
    Based on the FreeBSD kernels sys/sys/ioccom.h.
    """
    IOCPARM_SHIFT: Final = 13  # number of bits for ioctl size
    IOCPARM_MASK: Final = ((1 << IOCPARM_SHIFT) - 1)  # parameter length mask

    return (((inout) | (((length) & IOCPARM_MASK) << 16) | (ord(group) << 8) | (num)))


def _IOWR(group: str, num: int, length: int):
    """
    Create an ioctl command number for read/write commands.
    Based on the FreeBSD kernels sys/sys/ioccom.h.
    """
    IOC_VOID: Final = 0x20000000  # no parameters
    IOC_OUT: Final = 0x40000000  # copy out parameters
    IOC_IN: Final = 0x80000000  # copy in parameters
    IOC_INOUT: Final = (IOC_IN|IOC_OUT)  # copy parameters in and out
    IOC_DIRMASK: Final = (IOC_VOID|IOC_OUT|IOC_IN)  # mask for IN/OUT/VOID
    return _IOC(IOC_INOUT, group, num, length)


def IODEV_PIO():
    """
    Create an ioctl command number for the `/dev/io` device file.
    """

    # struct iodev_pio_req {
    # 	u_int access;
    # 	u_int port;
    # 	u_int width;
    # 	u_int val;
    # };

    length = struct.calcsize("IIII")
    return _IOWR("I", 0, length)


class FreeBsdPortIO(PortIOClass):
    """
    A class to interact with the `/dev/io` device file on FreeBSD.
    """

    _dev_io: IO | None = None

    def __init__(self):
        """
        Initialize the `/dev/port` device file.
        """
        self._dev_io = open("/dev/io", "wb", buffering=0)

    def __del__(self):
        """
        Close the `/dev/port` device file.
        """
        if self._dev_io:
            self._dev_io.close()

    def out_bytes(self, data: bytes, port: int) -> None:
        """
        Write data to the specified port.
        :param data: Data to write.
        :param port: Port to write to.
        """
        iodev_pio_req = struct.pack(
            "IIII", IODEV_PIO_WRITE, port, len(data), int.from_bytes(data, "little")
        )
        ioctl(self._dev_io, IODEV_PIO(), iodev_pio_req)

    def outb(self, data: int, port: int) -> None:
        """
        Write a byte (8 bit) to the specified port.
        :param data: Byte to write.
        :param port: Port to write to.
        """
        self.out_bytes(data.to_bytes(1, "little"), port)

    def outw(self, data: int, port: int) -> None:
        """
        Write a word (16 bit) to the specified port.
        :param data: Word to write.
        :param port: Port to write to.
        """
        self.out_bytes(data.to_bytes(2, "little"), port)

    def outl(self, data: int, port: int) -> None:
        """
        Write a long (32 bit) to the specified port.
        :param data: Long to write.
        :param port: Port to write to.
        """
        self.out_bytes(data.to_bytes(4, "little"), port)

    def in_bytes(self, port: int, num: int) -> bytes:
        """
        Read data from the specified port.
        :param port: Port to read from.
        :param num: Number of bytes to read (1 - 4).
        :return: Data read.
        """
        iodev_pio_req = struct.pack("IIII", IODEV_PIO_READ, port, num, 0)
        return ioctl(self._dev_io, IODEV_PIO(), iodev_pio_req)[struct.calcsize("III") :]

    def inb(self, port: int) -> int:
        """
        Read a byte (8 bit) from the specified port.
        :param port: Port to read from.
        :return: Byte read.
        """
        return int.from_bytes(self.in_bytes(port, 1), "little")

    def inw(self, port: int) -> int:
        """
        Read a word (16 bit) from the specified port.
        :param port: Port to read from.
        :return: Word read.
        """
        return int.from_bytes(self.in_bytes(port, 2), "little")

    def inl(self, port: int) -> int:
        """
        Read a long (32 bit) from the specified port.
        :param port: Port to read from.
        :return: Long read.
        """
        return int.from_bytes(self.in_bytes(port, 4), "little")

    def ioperm(self, port: int, num: int, turn_on: bool) -> None:
        """
        `ioperm` stub function. The iopl will already be raised from opening `/dev/io` and is not required.
        """
        pass

    def iopl(self, level: int) -> None:
        """
        `iopl` stub function. The iopl will already be raised from opening `/dev/io` and is not required.
        """
        pass
