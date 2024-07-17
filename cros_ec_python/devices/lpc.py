import struct
import warnings
import errno
from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..constants.LPC import *
from ..constants.MEMMAP import *
from ..exceptions import ECError

try:
    import portio
    _import_portio_error = None
except ImportError as e:
    _import_portio_error = e
    warnings.warn(f"Failed to import portio: {e}, using /dev/port instead.", ImportWarning)
    from ..utils import devportio as portio


class CrosEcLpc(CrosEcClass):
    """
    Class to interact with the EC using the LPC interface.
    """

    def __init__(self, init: bool = True, address: Int32 = None, portio_warn: bool = True):
        """
        Detect and initialise the EC.
        :param init: Whether to initialise the EC on creation. Default is True.
        :param address: Specify a custom memmap address, will be detected if not specified.
        :param portio_warn: Whether to warn if portio couldn't be imported. Default is True.
        """
        if portio_warn and _import_portio_error is not None:
            warnings.warn(f"Failed to import portio: {_import_portio_error}, using /dev/port instead.",
                          RuntimeWarning)

        self.address = address
        if init:
            self.ec_init()

    @staticmethod
    def detect() -> bool:
        """
        Checks for known CrOS EC memory map addresses in `/proc/ioports`.
        """
        with open("/proc/ioports", "r") as f:
            for line in f:
                if line.lstrip()[:4] in (format(EC_LPC_ADDR_MEMMAP, "04x"), format(EC_LPC_ADDR_MEMMAP_FWAMD, "04x")):
                    return True

    @staticmethod
    def find_address(*addresses) -> int | None:
        """
        Find the EC memory map address.
        :param addresses: A list of addresses to check.
        :return: The address of the EC memory map, or None if not found.
        """
        for a in addresses:
            if res := portio.ioperm(a, EC_MEMMAP_SIZE, True):
                if res == errno.EPERM:
                    raise PermissionError("Permission denied. Try running as root.")
                warnings.warn(f"ioperm returned {errno.errorcode[res]} ({res}), skipping address {a}...")
                continue
            # Check for 'EC' in memory map
            if portio.inw(a + EC_MEMMAP_ID) == int.from_bytes(b'EC', "little"):
                # Found it!
                return a
            else:
                # Nothing here
                portio.ioperm(a, EC_MEMMAP_SIZE, False)
                continue

    def ec_init(self) -> None:
        """
        Initialise the EC. Checks for the EC, and configures the library to speak the same version.
        :param address: Address of the EC memory map.
        """
        # Find memmap address
        if self.address is None:
            self.address = self.find_address(EC_LPC_ADDR_MEMMAP, EC_LPC_ADDR_MEMMAP_FWAMD)
            # find_address will leave ioperm enabled for the memmap
            if self.address is None:
                raise OSError("Could not find EC!")

        # Request I/O permissions
        if (res := portio.ioperm(EC_LPC_ADDR_HOST_DATA, EC_MEMMAP_SIZE, True)) or \
                (res := portio.ioperm(EC_LPC_ADDR_HOST_CMD, EC_MEMMAP_SIZE, True)) or \
                (res := portio.ioperm(EC_LPC_ADDR_HOST_PACKET, EC_LPC_HOST_PACKET_SIZE, True)):
            if res == errno.EPERM:
                raise PermissionError("Permission denied. Try running as root.")
            else:
                raise OSError(f"ioperm returned {errno.errorcode[res]} ({res})")

        status = 0xFF

        # Read status bits, at least one should be 0
        status &= portio.inb(EC_LPC_ADDR_HOST_CMD)
        status &= portio.inb(EC_LPC_ADDR_HOST_DATA)

        if status == 0xFF:
            raise OSError("No EC detected. Invalid status.")

        # Check for 'EC' in memory map
        if portio.inw(self.address + EC_MEMMAP_ID) != int.from_bytes(b'EC', "little"):
            raise OSError("Invalid EC signature.")

        self.ec_get_cmd_version()

    def ec_exit(self) -> None:
        pass

    @staticmethod
    def wait_for_ec(status_addr: Int32 = EC_LPC_ADDR_HOST_CMD) -> None:
        """
        Wait for the EC to be ready after sending a command.
        :param status_addr: The status register to read.
        """
        while portio.inb(status_addr) & EC_LPC_STATUS_BUSY_MASK:
            pass

    def ec_command_v2(self, version: UInt8, command: UInt32, outsize: UInt16, insize: UInt32, data: bytes = None,
                      warn: bool = True):
        """
        Send a command to the EC and return the response. Uses the v2 command protocol over LPC. UNTESTED!
        :param version: Command version number (often 0).
        :param command: Command to send (EC_CMD_...).
        :param outsize: Outgoing length in bytes.
        :param insize: Max number of bytes to accept from the EC.
        :param data: Outgoing data to EC.
        :param warn: Whether to warn if the response size is not as expected. Default is True.
        :return: Response from the EC.
        """
        warnings.warn("Support for v2 commands haven't been tested! Open an issue on github if it does "
                      "or doesn't work: https://github.com/Steve-Tech/CrOS_EC_Python/issues", RuntimeWarning)
        csum = 0
        args = bytearray(struct.pack("BBBB", EC_HOST_ARGS_FLAG_FROM_HOST, version, outsize, csum))
        # (flags: UInt8, command_version: UInt8, data_size: UInt8, checksum: UInt8)

        # Copy data and start checksum
        for i in range(outsize):
            portio.outb(data[i], EC_LPC_ADDR_HOST_PARAM + i)
            csum += data[i]

        # Finish checksum
        for i in range(len(args)):
            csum += args[i]

        args[3] = csum & 0xff

        # Copy header
        for i in range(len(args)):
            portio.outb(args[i], EC_LPC_ADDR_HOST_ARGS + i)

        # Start the command
        portio.outb(command, EC_LPC_ADDR_HOST_CMD)

        self.wait_for_ec()

        # Check result
        i = portio.inb(EC_LPC_ADDR_HOST_DATA)
        if i:
            raise ECError(i)

        # Read back args
        csum = 0
        data_out = bytearray(len(args))
        for i in range(len(data_out)):
            data_out[i] = portio.inb(EC_LPC_ADDR_HOST_ARGS + i)
            csum += data_out[i]

        response = struct.unpack("BBBB", data_out)
        # (flags: UInt8, command_version: UInt8, data_size: UInt8, checksum: UInt8)

        if response[0] != EC_HOST_ARGS_FLAG_TO_HOST:
            raise IOError("Invalid response!")

        if response[2] != insize and warn:
            warnings.warn(f"Expected {insize} bytes, got {response[2]} back from EC", RuntimeWarning)

        # Read back data
        data = bytearray()
        for i in range(response[2]):
            data.append(portio.inb(EC_LPC_ADDR_HOST_PARAM + i))
            csum += data[i]

        if response[3] != (csum & 0xff):
            raise IOError("Checksum error!")

        return bytes(data)

    def ec_command_v3(self, version: UInt8, command: UInt32, outsize: UInt16, insize: UInt32, data: bytes = None,
                      warn: bool = True) -> bytes:
        """
        Send a command to the EC and return the response. Uses the v3 command protocol over LPC.
        :param version: Command version number (often 0).
        :param command: Command to send (EC_CMD_...).
        :param outsize: Outgoing length in bytes.
        :param insize: Max number of bytes to accept from the EC.
        :param data: Outgoing data to EC.
        :param warn: Whether to warn if the response size is not as expected. Default is True.
        :return: Response from the EC.
        """
        csum = 0
        request = bytearray(struct.pack("BBHBxH", EC_HOST_REQUEST_VERSION, csum, command, version, outsize))
        # (struct_version: UInt8, checksum: UInt8, command: UInt16,
        # command_version: UInt8, reserved: UInt8, data_len: UInt16)

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

        self.wait_for_ec()

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
        # (struct_version: UInt8, checksum: UInt8, result: UInt16, data_len: UInt16, reserved: UInt16)

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

    def command(self, *args):
        """
        Stub function, will get overwritten in ec_get_cmd_version.
        """
        raise NotImplementedError("EC doesn't support commands!")

    def ec_get_cmd_version(self) -> int:
        version = portio.inb(self.address + EC_MEMMAP_HOST_CMD_FLAGS)

        if version & EC_HOST_CMD_FLAG_VERSION_3:
            self.command = self.ec_command_v3
            return 3
        elif version & EC_HOST_CMD_FLAG_LPC_ARGS_SUPPORTED:
            self.command = self.ec_command_v2
            return 2
        else:
            warnings.warn("EC doesn't support commands!", RuntimeWarning)
            return 0

    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        :param offset: Offset to read from.
        :param num_bytes: Number of bytes to read.
        :param address: Address of the EC memory map.
        :return: Bytes read from the EC.
        """
        data = bytearray()
        for i in range(num_bytes):
            data.append(portio.inb(self.address + offset + i))
        return bytes(data)
