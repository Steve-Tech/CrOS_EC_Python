from enum import Enum
from . import dev, lpc

class DeviceTypes(Enum):
    LinuxDev = 0
    LPC = 1

class CrOS_EC:
    def __init__(self, dev_type: DeviceTypes = DeviceTypes.LinuxDev, init: bool = True, **kwargs) -> None:
        """
        Initialise the CrOS_EC class, and by default the EC communication too.
        dev_type: The device type to use.
        init: Whether to initialise the communication
        """
        self.dev_type = dev_type
        self.kwargs = kwargs
        if init:
            self.ec_init()

    def ec_init(self) -> None:
        """
        Initialise the EC, this shouldn't need to be called unless the keyword arg init was set to false.
        """
        match (self.dev_type):
            case DeviceTypes.LinuxDev:
                if "fd" not in self.kwargs:
                    file = self.kwargs.get("file", "/dev/cros_ec")
                    self.kwargs["fd"] = open(file, "wb")
            case DeviceTypes.LPC:
                lpc.ec_init(self.kwargs.get("address"))
            case _:
                raise NotImplementedError

    
    def command(self, version: int, command: int, outsize: int, insize: int, data: bytes = None) -> bytes:
        """
        Send a command to the EC and return the response.
        version: Command version number (often 0).
        command: Command to send (EC_CMD_...).
        outsize: Outgoing length in bytes.
        insize: Max number of bytes to accept from the EC. None for unlimited.
        data: Outgoing data to EC.
        """
        match (self.dev_type):
            case DeviceTypes.LinuxDev:
                return dev.ec_command_fd(self.kwargs["fd"], version, command, outsize, insize, data)
            case _:
                raise NotImplementedError
            
    def memmap(self, offset: int, num_bytes: int) -> bytes:
        match (self.dev_type):
            case DeviceTypes.LinuxDev:
                return dev.ec_readmem_fd(self.kwargs["fd"], offset, num_bytes)
            case DeviceTypes.LPC:
                return lpc.ec_readmem(offset, num_bytes, self.kwargs.get("address"))
            case _:
                raise NotImplementedError
