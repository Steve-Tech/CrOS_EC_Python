import struct
import warnings
import errno
import sys

from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..constants.LPC import *
from ..constants.MEC import *
from ..constants.MEMMAP import *
from ..exceptions import ECError

from ..ioports import PortIO


class CrosEcMec(CrosEcClass):
    """
    Class to interact with the EC using the MEC LPC interface.
    """

    def __init__(
        self, init: bool = True, portio: PortIO | None = None
    ):
        """
        Detect and initialise the EC.
        :param init: Whether to initialise the EC on creation. Default is True.
        :param address: Specify a custom memmap address, will be detected if not specified.
        :param portio: PortIO object to use. Default is auto-detected.
        """

        if portio is None:
            portio = PortIO()

        self.portio: PortIO = portio
        """PortIO object to use."""

        if init:
            self.ec_init()

    @staticmethod
    def detect() -> bool:
        """
        Checks for known CrOS EC memory map addresses in `/proc/ioports`.
        """
        if sys.platform == "linux":
            try:
                with open("/proc/ioports", "r") as f:
                    for line in f:
                        if line.lstrip()[:4] == format(EC_HOST_CMD_REGION0, "04x"):
                            return True
                return False
            except FileNotFoundError:
                pass
        elif sys.platform == "win32":
            try:
                from wmi import WMI

                c = WMI()
                for resource in c.Win32_PortResource():
                    start_address = int(resource.StartingAddress)
                    if start_address == EC_HOST_CMD_REGION0:
                        return True
                return False
            except ImportError:
                pass

        # Probe for the EC as a last resort
        return CrosEcMec.probe()

    @staticmethod
    def probe(portio: PortIO | None = None) -> bool:
        """
        Probe the EC memory map address.
        :return: True if the EC is found, False otherwise.
        """
        if portio is None:
            portio = PortIO()

        # Request I/O permissions
        if (
            (res := portio.ioperm(EC_LPC_ADDR_HOST_DATA, 1, True))
            or (res := portio.ioperm(EC_LPC_ADDR_HOST_CMD, 1, True))
            or (
                res := portio.ioperm(
                    EC_HOST_CMD_REGION0, EC_HOST_CMD_MEC_REGION_SIZE, True
                )
            )
        ):
            if res == errno.EPERM:
                raise PermissionError("Permission denied. Try running as root.")
            warnings.warn(f"ioperm returned {errno.errorcode[res]} ({res})!")

        status = 0xFF

        # Read status bits, at least one should be 0
        status &= portio.inb(EC_LPC_ADDR_HOST_CMD)
        status &= portio.inb(EC_LPC_ADDR_HOST_DATA)

        if status != 0xFF:
            # Check for 'EC' in memory map
            portio.outw(
                EC_MEC_ADDR_MEMMAP + EC_MEMMAP_ID & 0xFFFC | MEC_ACCESS_TYPE_WORD,
                MEC_EMI_EC_ADDRESS_B0,
            )
            if portio.inw(MEC_EMI_EC_DATA_B0).to_bytes(2, "little") == b"EC":
                # Found it!
                return True

        # Nothing here
        portio.ioperm(EC_LPC_ADDR_HOST_DATA, 1, False)
        portio.ioperm(EC_LPC_ADDR_HOST_CMD, 1, False)
        portio.ioperm(EC_HOST_CMD_REGION0, EC_HOST_CMD_MEC_REGION_SIZE, False)
        return False

    def ec_init(self) -> None:
        """
        Initialise the EC.
        """
        if not self.probe():
            raise OSError("Could not find EC!")

    def ec_exit(self) -> None:
        pass

    def wait_for_ec(self, status_addr: Int32 = EC_LPC_ADDR_HOST_CMD) -> None:
        """
        Wait for the EC to be ready after sending a command.
        :param status_addr: The status register to read.
        """
        while self.portio.inb(status_addr) & EC_LPC_STATUS_BUSY_MASK:
            pass

    def command(
        self,
        version: UInt8,
        command: UInt32,
        outsize: UInt16,
        insize: UInt32,
        data: bytes = None,
        warn: bool = True,
    ) -> bytes:
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
        request = bytearray(
            struct.pack(
                "BBHBxH", EC_HOST_REQUEST_VERSION, csum, command, version, outsize
            )
        )
        # (struct_version: UInt8, checksum: UInt8, command: UInt16,
        # command_version: UInt8, reserved: UInt8, data_len: UInt16)

        # Fail if output size is too big
        if outsize + len(request) > EC_LPC_HOST_PACKET_SIZE:
            raise ValueError("Output size too big!")

        packet = request + (data or bytes())
        # Calculate checksum
        for i in packet:
            csum += i

        # Write checksum field so the entire packet sums to 0
        packet[1] = (-csum) & 0xFF

        # Copy data
        self.mec_xfer(0, len(packet), write=True, data=packet)

        # Start the command
        self.portio.outb(EC_COMMAND_PROTOCOL_3, EC_LPC_ADDR_HOST_CMD)

        self.wait_for_ec()

        # Check result
        i = self.portio.inb(EC_LPC_ADDR_HOST_DATA)
        if i:
            raise ECError(i)

        # Read back response and start checksum
        csum = 0
        data_out = self.mec_xfer(0, struct.calcsize("BBHHH"), write=False)
        for i in data_out:
            csum += i

        response = struct.unpack("BBHHH", data_out)
        # (struct_version: UInt8, checksum: UInt8, result: UInt16, data_len: UInt16, reserved: UInt16)

        if response[0] != EC_HOST_RESPONSE_VERSION:
            raise IOError("Invalid response version!")

        if response[4]:
            # Reserved should be 0
            raise IOError("Invalid response!")

        if response[3] != insize and warn:
            warnings.warn(
                f"Expected {insize} bytes, got {response[3]} back from EC",
                RuntimeWarning,
            )

        # Read back data
        if response[3] != 0:
            data = self.mec_xfer(struct.calcsize("BBHHH"), response[3], write=False)
            for i in data:
                csum += i
        else:
            data = bytes()

        if csum & 0xFF:
            raise IOError("Checksum error!")

        return bytes(data)

    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        :param offset: Offset to read from.
        :param num_bytes: Number of bytes to read.
        :param address: Address of the EC memory map.
        :return: Bytes read from the EC.
        """
        return self.mec_xfer(EC_MEC_ADDR_MEMMAP + offset, num_bytes)
    
    def mec_xfer_direct(self, address: Int32, length: Int32, write: bool = False, data: bytes = None) -> bytes | None:
        """
        Transfer data to/from the MEC EC using the MEC-specific LPC access method. Direct method for single access.
        :param address: Address to read/write.
        :param length: Number of bytes to read/write.
        :param write: True to write, False to read. Default is False (read).
        :param data: Data to write if write is True.
        :return: Data read from the EC if write is False, otherwise None.
        """
        if write and (data is None or len(data) < length):
            raise ValueError("Insufficient data provided for write operation.")

        if address % 4 + length <= 4:
            access_type = (MEC_ACCESS_TYPE_BYTE, MEC_ACCESS_TYPE_WORD, MEC_ACCESS_TYPE_BYTE, MEC_ACCESS_TYPE_LONG)[length - 1]
            self.portio.outw(address & 0xFFFC | access_type, MEC_EMI_EC_ADDRESS_B0)
            if write:
                match length:
                    case 1:
                        self.portio.outb(data[0], MEC_EMI_EC_DATA_B0 + (address % 4))
                    case 2:
                        self.portio.outw(int.from_bytes(data[0:2], "little"), MEC_EMI_EC_DATA_B0 + (address % 4))
                    case 3:
                        self.portio.outw(int.from_bytes(data[0:2], "little"), MEC_EMI_EC_DATA_B0 + (address % 4))
                        self.portio.outb(data[2], MEC_EMI_EC_DATA_B2 + (address % 4))
                    case 4:
                        self.portio.outl(int.from_bytes(data[0:4], "little"), MEC_EMI_EC_DATA_B0)
            else:
                match length:
                    case 1:
                        return self.portio.inb(
                            MEC_EMI_EC_DATA_B0 + (address % 4)
                        ).to_bytes(1, "little")
                    case 2:
                        return self.portio.inw(MEC_EMI_EC_DATA_B0 + (address % 4)).to_bytes(2, "little")
                    case 3:
                        word1 = self.portio.inw(MEC_EMI_EC_DATA_B0 + (address % 4)).to_bytes(2, "little")
                        byte1 = self.portio.inb(MEC_EMI_EC_DATA_B2 + (address % 4)).to_bytes(1, "little")
                        return word1 + byte1
                    case 4:
                        return self.portio.inl(MEC_EMI_EC_DATA_B0).to_bytes(4, "little")
        else:
            raise ValueError("Direct access only supports single 1-4 byte accesses.")

    def mec_xfer_aligned_64(self, address: Int32, length: Int32, write: bool = False, data: bytes = None) -> bytes | None:
        """
        Transfer data to/from the MEC EC using the MEC-specific LPC access method. Aligned 64-bit method.
        :param address: Address to read/write.
        :param length: Number of bytes to read/write.
        :param write: True to write, False to read. Default is False (read).
        :param data: Data to write if write is True.
        :return: Data read from the EC if write is False, otherwise None.
        """
        if write and (data is None or len(data) < length):
            raise ValueError("Insufficient data provided for write operation.")

        if address % 4 == 0 and length % 4 == 0:
            result = bytearray()
            self.portio.outw(address & 0xFFFC | MEC_ACCESS_TYPE_LONG_AUTOINCREMENT, MEC_EMI_EC_ADDRESS_B0)
            for i in range(0, length, 4):
                if write:
                    self.portio.outl(int.from_bytes(data[i:i+4], "little"), MEC_EMI_EC_DATA_B0)
                else:
                    result.extend(self.portio.inl(MEC_EMI_EC_DATA_B0).to_bytes(4, "little"))
            if not write:
                return bytes(result)
        else:
            raise ValueError("Aligned 64-bit access requires 4-byte aligned address and length.")

    def mec_xfer(self, address: Int32, length: Int32, write: bool = False, data: bytes = None) -> bytes | None:
        """
        Transfer data to/from the MEC EC using the MEC-specific LPC access method.
        :param address: Address to read/write.
        :param length: Number of bytes to read/write.
        :param write: True to write, False to read. Default is False (read).
        :param data: Data to write if write is True.
        :return: Data read from the EC if write is False, otherwise None.
        """
        if write and (data is None or len(data) < length):
            raise ValueError("Insufficient data provided for write operation.")

        result = bytearray()
        # Use some combination of the two methods for unaligned accesses
        if address % 4 != 0:
            # Handle unaligned start
            start_align = 4 - (address % 4)
            if write:
                self.mec_xfer_direct(address, start_align, write, data[0:start_align])
                address += start_align
                length -= start_align
                data = data[start_align:]
            else:
                part = self.mec_xfer_direct(address, start_align, write)
                address += start_align
                length -= start_align
                result = bytearray(part)
        # Handle aligned middle
        middle_length = length - (length % 4)
        if middle_length > 0:
            if write:
                self.mec_xfer_aligned_64(address, middle_length, write, data[0:middle_length])
                address += middle_length
                length -= middle_length
                data = data[middle_length:]
            else:
                part = self.mec_xfer_aligned_64(address, middle_length, write)
                address += middle_length
                length -= middle_length
                result.extend(part)
        # Handle unaligned end
        if length > 0:
            if write:
                self.mec_xfer_direct(address, length, write, data[0:length])
            else:
                part = self.mec_xfer_direct(address, length, write)
                result.extend(part)
        if not write:
            return bytes(result)
