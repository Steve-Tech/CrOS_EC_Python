import struct
import portio
import warnings
from .constants.COMMON import *
from .constants.LPC import *
from .constants.MEMMAP import *
from .exceptions import ECError


def ec_init(address: Int32 = EC_LPC_ADDR_MEMMAP) -> None:
    """
    Initialise the EC. Checks for the EC, and configures the library to speak the same version.
    @param address: Address of the EC memory map.
    """
    # Request I/O permissions
    if portio.ioperm(address, EC_MEMMAP_SIZE, True) or \
            portio.ioperm(EC_LPC_ADDR_HOST_DATA, EC_MEMMAP_SIZE, True) or \
            portio.ioperm(EC_LPC_ADDR_HOST_CMD, EC_MEMMAP_SIZE, True) or \
            portio.ioperm(EC_LPC_ADDR_HOST_PACKET, EC_LPC_HOST_PACKET_SIZE, True):
        raise PermissionError("Permission denied. Try running as root.")

    status = 0xFF

    # Read status bits, at least one should be 0
    status &= portio.inb(EC_LPC_ADDR_HOST_CMD)
    status &= portio.inb(EC_LPC_ADDR_HOST_DATA)

    if status == 0xFF:
        raise OSError("No EC detected.")

    # Check for 'EC' in memory map
    if portio.inb(address + EC_MEMMAP_ID) != ord("E") and portio.inb(
            address + EC_MEMMAP_ID + 1
    ) != ord("C"):
        raise OSError("Invalid EC signature.")

    ec_get_cmd_version(address)


def wait_for_ec(status_addr: Int32 = EC_LPC_ADDR_HOST_CMD) -> None:
    """
    Wait for the EC to be ready after sending a command.
    @param status_addr: The status register to read.
    """
    while portio.inb(status_addr) & EC_LPC_STATUS_BUSY_MASK:
        pass


def ec_command_v2():
    raise NotImplementedError


def ec_command_v3(version: UInt8, command: UInt32, outsize: UInt16, insize: UInt32, data: bytes = None,
                  warn: bool = True) -> bytes:
    """
    Send a command to the EC and return the response. Uses the v3 command protocol over LPC.
    @param version: Command version number (often 0).
    @param command: Command to send (EC_CMD_...).
    @param outsize: Outgoing length in bytes.
    @param insize: Max number of bytes to accept from the EC.
    @param data: Outgoing data to EC.
    @param warn: Whether to warn if the response size is not as expected. Default is True.
    @return: Response from the EC.
    """
    csum = 0
    request = bytearray(struct.pack("BBHBxH", EC_HOST_REQUEST_VERSION, csum, command, version, outsize))

    # Fail if output size is too big
    if outsize + len(request) > EC_LPC_HOST_PACKET_SIZE:
        raise ValueError("Output size too big!")

    # Copy data and start checksum
    for i in range(outsize):
        portio.outb(data[i], EC_LPC_ADDR_HOST_PACKET + len(request) + i)
        csum += data[i]

    # Finish checksum
    for i in range(len(request)):
        csum += request[i]

    request[1] = (-csum) & 0xff

    # Copy header
    for i in range(len(request)):
        portio.outb(request[i], EC_LPC_ADDR_HOST_PACKET + i)

    # Start the command
    portio.outb(EC_COMMAND_PROTOCOL_3, EC_LPC_ADDR_HOST_CMD)

    wait_for_ec()

    # Check result
    i = portio.inb(EC_LPC_ADDR_HOST_DATA)
    if i:
        raise ECError(i)

    # Read back response and start checksum
    csum = 0
    data_out = bytearray(1 + 1 + 2 + 2 + 2)
    for i in range(len(data_out)):
        data_out[i] = portio.inb(EC_LPC_ADDR_HOST_PACKET + i)
        csum += data_out[i]

    response = struct.unpack("BBHHH", data_out)

    if response[0] != EC_HOST_RESPONSE_VERSION:
        raise IOError("Invalid response version!")

    if response[4]:
        # Reserved should be 0
        raise IOError("Invalid response!")

    if response[3] != insize and warn:
        warnings.warn(f"Expected {insize} bytes, got {response[3]} back from EC", RuntimeWarning)

    # Read back data
    data = bytearray()
    for i in range(response[3]):
        data.append(portio.inb(EC_LPC_ADDR_HOST_PACKET + len(data_out) + i))
        csum += data[i]

    if csum & 0xff:
        raise IOError("Checksum error!")

    return bytes(data)


def ec_command(*args):
    """
    Stub function, will get overwritten in ec_get_cmd_version.
    """
    raise NotImplementedError


def ec_get_cmd_version(address: Int32 = EC_LPC_ADDR_MEMMAP) -> int:
    global ec_command

    version = portio.inb(address + EC_MEMMAP_HOST_CMD_FLAGS)

    if version & EC_HOST_CMD_FLAG_VERSION_3:
        ec_command = ec_command_v3
        return 3
    elif version & EC_HOST_CMD_FLAG_LPC_ARGS_SUPPORTED:
        ec_command = ec_command_v2
        return 2
    else:
        warnings.warn("EC doesn't support commands!", RuntimeWarning)
        return 0


def ec_readmem(offset: Int32, num_bytes: Int32, address: Int32 = EC_LPC_ADDR_MEMMAP) -> bytes:
    """
    Read memory from the EC.
    @param offset: Offset to read from.
    @param num_bytes: Number of bytes to read.
    @param address: Address of the EC memory map.
    @return: Bytes read from the EC.
    """
    data = bytearray()
    for i in range(num_bytes):
        data.append(portio.inb(address + offset + i))
    return bytes(data)
