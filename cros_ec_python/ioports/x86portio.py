"""
This module provides a class for port I/O using the portio module.

This method might be slightly faster than the `/dev/port` method,
since it uses the x86 I/O instructions directly,
but it requires the `portio` module to be installed.
"""

from .baseportio import PortIOClass
import portio


class IoPortIo(PortIOClass):
    """
    A class to interact with the portio module for x86 port I/O.
    """

    portio = portio

    def outb(self, data: int, port: int) -> None:
        portio.outb(data, port)

    def outb_p(self, data: int, port: int) -> None:
        portio.outb_p(data, port)

    def outw(self, data: int, port: int) -> None:
        portio.outw(data, port)

    def outw_p(self, data: int, port: int) -> None:
        portio.outw_p(data, port)

    def outl(self, data: int, port: int) -> None:
        portio.outl(data, port)

    def outl_p(self, data: int, port: int) -> None:
        portio.outl_p(data, port)

    def outsb(self, data: bytes, port: int) -> None:
        portio.outsb(data, port)

    def outsw(self, data: bytes, port: int) -> None:
        portio.outsw(data, port)

    def outsl(self, data: bytes, port: int) -> None:
        portio.outsl(data, port)

    def inb(self, port: int) -> int:
        return portio.inb(port)

    def inb_p(self, port: int) -> int:
        return portio.inb_p(port)

    def inw(self, port: int) -> int:
        return portio.inw(port)

    def inw_p(self, port: int) -> int:
        return portio.inw_p(port)

    def inl(self, port: int) -> int:
        return portio.inl(port)

    def inl_p(self, port: int) -> int:
        return portio.inl_p(port)

    def insb(self, port: int, num: int) -> bytes:
        return portio.insb(port, num)

    def insw(self, port: int, num: int) -> bytes:
        return portio.insw(port, num)

    def insl(self, port: int, num: int) -> bytes:
        return portio.insl(port, num)

    def ioperm(self, port, num, turn_on) -> None:
        return portio.ioperm(port, num, turn_on)

    def iopl(self, level) -> None:
        return portio.iopl(level)
