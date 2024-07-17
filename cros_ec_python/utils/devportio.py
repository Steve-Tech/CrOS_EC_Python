"""
This file provides a way to interact with the `/dev/port` device file
as an alternative to the [portio](https://pypi.org/project/portio/) library.

This is *a lot* slower than the portio library (especially since `/dev/port` is opened on every function call),
but it doesn't require an extra package.
"""

def out_bytes(data: bytes, port: int) -> None:
    """
    Write data to the specified port.
    :param data: Data to write.
    :param port: Port to write to.
    """
    with open("/dev/port", "wb") as f:
        f.seek(port)
        f.write(data)


def outb(data: int, port: int) -> None:
    """
    Write a byte to the specified port.
    :param data: Byte to write.
    :param port: Port to write to.
    """
    out_bytes(data.to_bytes(1, "little"), port)


outb_p = outb


def outw(data: int, port: int) -> None:
    """
    Write a word to the specified port.
    :param data: Word to write.
    :param port: Port to write to.
    """
    out_bytes(data.to_bytes(2, "little"), port)


outw_p = outw


def outl(data: int, port: int) -> None:
    """
    Write a long to the specified port.
    :param data: Long to write.
    :param port: Port to write to.
    """
    out_bytes(data.to_bytes(4, "little"), port)


outl_p = outl


def outsb(data: int, port: int, count: int) -> None:
    """
    Write a byte to the specified port, multiple times.
    :param data: Byte to write.
    :param port: Port to write to.
    :param count: Number of times to write.
    """
    for i in range(count):
        outb(data, port)


def outsw(data: int, port: int, count: int) -> None:
    """
    Write a word to the specified port, multiple times.
    :param data: Word to write.
    :param port: Port to write to.
    :param count: Number of times to write.
    """
    for i in range(count):
        outw(data, port)


def outsl(data: int, port: int, count: int) -> None:
    """
    Write a long to the specified port, multiple times.
    :param data: Long to write.
    :param port: Port to write to.
    :param count: Number of times to write.
    """
    for i in range(count):
        outl(data, port)


def in_bytes(port: int, num: int) -> bytes:
    """
    Read data from the specified port.
    :param port: Port to read from.
    :param num: Number of bytes to read.
    :return: Data read.
    """
    with open("/dev/port", "rb") as f:
        f.seek(port)
        return f.read(num)


def inb(port: int) -> int:
    """
    Read a byte from the specified port.
    :param port: Port to read from.
    :return: Byte read.
    """
    return int.from_bytes(in_bytes(port, 1), "little")


inb_p = inb


def inw(port: int) -> int:
    """
    Read a word from the specified port.
    :param port: Port to read from.
    :return: Word read.
    """
    return int.from_bytes(in_bytes(port, 2), "little")


inw_p = inw


def inl(port: int) -> int:
    """
    Read a long from the specified port.
    :param port: Port to read from.
    :return: Long read.
    """
    return int.from_bytes(in_bytes(port, 4), "little")


inl_p = inl


def insb(port: int, data: bytearray, count: int) -> None:
    """
    Read a byte from the specified port, multiple times.
    :param port: Port to read from.
    :param data: Buffer to read into.
    :param count: Number of times to read.
    """
    for i in range(count):
        if i >= len(data):
            data.append(inb(port))
        else:
            data[i] = inb(port)


def insw(port: int, data: bytearray, count: int) -> None:
    """
    Read a word from the specified port, multiple times.
    :param port: Port to read from.
    :param data: Buffer to read into.
    :param count: Number of times to read.
    """
    for i in range(count):
        if i >= len(data):
            data.append(inw(port))
        else:
            data[i] = inw(port)


def insl(port: int, data: bytearray, count: int) -> None:
    """
    Read a long from the specified port, multiple times.
    :param port: Port to read from.
    :param data: Buffer to read into.
    :param count: Number of times to read.
    """
    for i in range(count):
        if i >= len(data):
            data.append(inl(port))
        else:
            data[i] = inl(port)


def ioperm(port: int, num: int, turn_on: bool) -> None:
    """
    `ioperm` stub function. It's not required for `/dev/port`.
    """
    pass


def iopl(level: int) -> None:
    """
    `iopl` stub function. It's not required for `/dev/port`.
    """
    pass
