"""
This file includes the base class for Port I/O backends.

It doesn't do anything on its own, but it is used as a base for all port I/O backends to inherit from.

See `cros_ec_python.ioports` for a few examples of a class that inherits from this class.
"""

import abc


class PortIOClass(metaclass=abc.ABCMeta):
    """
    Base class for port I/O backends to inherit from.
    """

    @abc.abstractmethod
    def outb(self, data: int, port: int) -> None:
        """
        Write a byte (8 bit) to the specified port.
        :param data: Byte to write.
        :param port: Port to write to.
        """
        pass

    @abc.abstractmethod
    def outw(self, data: int, port: int) -> None:
        """
        Write a word (16 bit) to the specified port.
        :param data: Word to write.
        :param port: Port to write to.
        """
        pass

    @abc.abstractmethod
    def outl(self, data: int, port: int) -> None:
        """
        Write a long (32 bit) to the specified port.
        :param data: Long to write.
        :param port: Port to write to.
        """
        pass

    @abc.abstractmethod
    def inb(self, port: int) -> int:
        """
        Read a byte (8 bit) from the specified port.
        :param port: Port to read from.
        :return: Byte read.
        """
        pass

    @abc.abstractmethod
    def inw(self, port: int) -> int:
        """
        Read a word (16 bit) from the specified port.
        :param port: Port to read from.
        :return: Word read.
        """
        pass

    @abc.abstractmethod
    def inl(self, port: int) -> int:
        """
        Read a long (32 bit) from the specified port.
        :param port: Port to read from.
        :return: Long read.
        """
        pass

    @abc.abstractmethod
    def ioperm(self, port: int, num: int, turn_on: bool) -> None:
        """
        Set I/O permissions for a range of ports.
        :param port: Start of port range.
        :param num: Number of ports to set permissions for.
        :param turn_on: Whether to turn on or off permissions.
        """
        pass

    @abc.abstractmethod
    def iopl(self, level: int) -> None:
        """
        Set I/O permissions level.
        :param level: Permissions level.
        """
        pass
