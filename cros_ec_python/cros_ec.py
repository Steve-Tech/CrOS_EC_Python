from enum import Enum
from . import dev, lpc
from .constants.COMMON import *


class DeviceTypes(Enum):
    LinuxDev = 0
    LPC = 1


class CrOS_EC:
    def __init__(self, dev_type: DeviceTypes = DeviceTypes.LinuxDev, init: bool = True, **kwargs) -> None:
        """
        Initialise the CrOS_EC class, and by default the EC communication too.
        @param dev_type: The device type to use.
        @param init: Whether to initialise the communication
        """
        self.dev_type = dev_type
        self.kwargs = kwargs
        self.init_ec = init
        if init:
            self.ec_init()

    def __del__(self) -> None:
        """
        Close the file descriptor if it was initialised by this class.
        """
        if self.init_ec:
            self.ec_exit()

    def ec_init(self) -> None:
        """
        Initialise the EC, this shouldn't need to be called unless the keyword arg init was set to false.
        """
        match self.dev_type:
            case DeviceTypes.LinuxDev:
                if "fd" not in self.kwargs:
                    file = self.kwargs.get("file", "/dev/cros_ec")
                    self.kwargs["fd"] = open(file, "wb")
            case DeviceTypes.LPC:
                lpc.ec_init(self.kwargs.get("address"))
            case _:
                raise NotImplementedError

    def ec_exit(self) -> None:
        """
        Close the file descriptor if it exists.
        """
        match self.dev_type:
            case DeviceTypes.LinuxDev:
                if "fd" in self.kwargs:
                    self.kwargs["fd"].close()
            case _:
                pass

    def command(self, version: Int32, command: Int32, outsize: Int32, insize: Int32, data: bytes = None,
                warn: bool = True) -> bytes:
        """
        Send a command to the EC and return the response.
        @param version: Command version number (often 0).
        @param command: Command to send (EC_CMD_...).
        @param outsize: Outgoing length in bytes.
        @param insize: Max number of bytes to accept from the EC.
        @param data: Outgoing data to EC.
        @param warn: Whether to warn if the response size is not as expected. Default is True.
        @return: Response from the EC.
        """
        match self.dev_type:
            case DeviceTypes.LinuxDev:
                return dev.ec_command_fd(self.kwargs["fd"], version, command, outsize, insize, data, warn)
            case DeviceTypes.LPC:
                return lpc.ec_command(version, command, outsize, insize, data, warn)
            case _:
                raise NotImplementedError

    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        @param offset: Offset to read from.
        @param num_bytes: Number of bytes to read.
        @return: Bytes read from the EC.
        """
        match self.dev_type:
            case DeviceTypes.LinuxDev:
                return dev.ec_readmem_fd(self.kwargs["fd"], offset, num_bytes)
            case DeviceTypes.LPC:
                return lpc.ec_readmem(offset, num_bytes, self.kwargs.get("address"))
            case _:
                raise NotImplementedError
