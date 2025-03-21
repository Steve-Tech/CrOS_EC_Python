"""
This file provides a way to interact with the `/dev/port` device file
as an alternative to the [portio](https://pypi.org/project/portio/) library.

The speed is pretty much on par with the `portio` library, so there is no
real downside to using this method.
"""

from .baseportio import PortIOClass


class DevPortIO(PortIOClass):
    """
    A class to interact with the `/dev/port` device file.
    """

    _dev_port = None

    def __init__(self):
        """
        Initialize the `/dev/port` device file.
        """
        self._dev_port = open("/dev/port", "r+b", buffering=0)

    def __del__(self):
        """
        Close the `/dev/port` device file.
        """
        if self._dev_port:
            self._dev_port.close()

    def out_bytes(self, data: bytes, port: int) -> None:
        """
        Write data to the specified port.
        :param data: Data to write.
        :param port: Port to write to.
        """
        self._dev_port.seek(port)
        self._dev_port.write(data)

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
        :param num: Number of bytes to read.
        :return: Data read.
        """
        self._dev_port.seek(port)
        return self._dev_port.read(num)

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
        `ioperm` stub function. It's not required for `/dev/port`.
        """
        pass

    def iopl(self, level: int) -> None:
        """
        `iopl` stub function. It's not required for `/dev/port`.
        """
        pass
