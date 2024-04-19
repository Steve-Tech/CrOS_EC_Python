from fcntl import ioctl
import struct

CROS_EC_IOC_MAGIC = 0xEC


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
    fd, version: int, command: int, outsize: int, insize: int, data: bytes = None
):
    """
    Send a command to the EC and return the response.
    fd: File descriptor for the EC device.
    version: Command version number (often 0).
    command: Command to send (EC_CMD_...).
    outsize: Outgoing length in bytes.
    insize: Max number of bytes to accept from the EC.
    data: Outgoing data to EC.
    """
    if data is None:
        data = bytes(outsize)

    cmd = struct.pack(f"<IIIII", version, command, outsize, insize, 0xFF)
    buf = bytearray(cmd + bytes(max(outsize, insize)))
    buf[len(cmd) : len(cmd) + outsize] = data

    CROS_EC_DEV_IOCXCMD = _IORW(CROS_EC_IOC_MAGIC, 0, len(cmd))
    result = ioctl(fd, CROS_EC_DEV_IOCXCMD, buf)

    if result < 0:
        raise IOError(f"ioctl failed with error {result}")

    if result != insize:
        raise IOError(f"expected {insize} bytes, got {result}")

    return bytes(buf[len(cmd) : len(cmd) + insize])

def ec_command(version: int, command: int, outsize: int, insize: int, data: bytes = None):
    """
    Send a command to the EC and return the response.
    version: Command version number (often 0).
    command: Command to send (EC_CMD_...).
    outsize: Outgoing length in bytes.
    insize: Max number of bytes to accept from the EC.
    data: Outgoing data to EC.
    """
    with open("/dev/cros_ec", "wb") as fd:
        return ec_command_fd(fd, version, command, outsize, insize, data)
    
def ec_many_commands(commands: list[tuple[int, int, int, int, bytes]]):
    """
    Send multiple commands to the EC.
    commands: List of commands to send. Each command is a tuple of arguments to ec_command.
    """
    results = []
    with open("/dev/cros_ec", "wb") as fd:
        for command in commands:
            results.append(ec_command_fd(fd, *command))

    return results
