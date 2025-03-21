"""
This file provides a way to interact with the WinRing0 library for port I/O on Windows.

For this to work, you will need to copy `WinRing0x64.dll` and `WinRing0x64.sys` to either
the same directory as `python.exe`, or to `C:\\Windows\\System32`.
"""

from enum import Enum
import ctypes

from .baseportio import PortIOClass


class WinPortIO(PortIOClass):
    """
    A class to interact with the WinRing0 library for port I/O on Windows.
    """

    winring0 = None

    def __init__(self):
        """
        Load and initialize the WinRing0 library.
        """
        self.winring0 = ctypes.WinDLL("WinRing0x64.dll")
        self.winring0.InitializeOls.restype = ctypes.c_bool
        self.winring0.GetDllStatus.restype = ctypes.c_ulong
        self.winring0.DeinitializeOls.restype = None
        # ReadIoPort (port)
        self.winring0.ReadIoPortByte.restype = ctypes.c_ubyte
        self.winring0.ReadIoPortByte.argtypes = [ctypes.c_ushort]
        self.winring0.ReadIoPortWord.restype = ctypes.c_ushort
        self.winring0.ReadIoPortWord.argtypes = [ctypes.c_ushort]
        self.winring0.ReadIoPortDword.restype = ctypes.c_ulong
        self.winring0.ReadIoPortDword.argtypes = [ctypes.c_ushort]
        # WriteIoPort (port, data)
        self.winring0.WriteIoPortByte.argtypes = [ctypes.c_ushort, ctypes.c_ubyte]
        self.winring0.WriteIoPortWord.argtypes = [ctypes.c_ushort, ctypes.c_ushort]
        self.winring0.WriteIoPortDword.argtypes = [ctypes.c_ushort, ctypes.c_ulong]

        self.winring0.InitializeOls()
        if error := self.winring0.GetDllStatus():
            raise OSError(f"WinRing0 Error: {self.Status(error)} ({error})")

    def __del__(self):
        """
        Deinitialize the WinRing0 library.
        """
        if self.winring0:
            self.winring0.DeinitializeOls()

    class Status(Enum):
        OLS_DLL_NO_ERROR = 0
        OLS_DLL_UNSUPPORTED_PLATFORM = 1
        OLS_DLL_DRIVER_NOT_LOADED = 2
        OLS_DLL_DRIVER_NOT_FOUND = 3
        OLS_DLL_DRIVER_UNLOADED = 4
        OLS_DLL_DRIVER_NOT_LOADED_ON_NETWORK = 5
        OLS_DLL_UNKNOWN_ERROR = 9

        OLS_DLL_DRIVER_INVALID_PARAM = 10
        OLS_DLL_DRIVER_SC_MANAGER_NOT_OPENED = 11
        OLS_DLL_DRIVER_SC_DRIVER_NOT_INSTALLED = 12
        OLS_DLL_DRIVER_SC_DRIVER_NOT_STARTED = 13
        OLS_DLL_DRIVER_SC_DRIVER_NOT_REMOVED = 14

    def outb(self, data: int, port: int) -> None:
        """
        Write a byte (8 bit) to the specified port.
        :param data: Byte to write.
        :param port: Port to write to.
        """
        self.winring0.WriteIoPortByte(port, data)

    def outw(self, data: int, port: int) -> None:
        """
        Write a word (16 bit) to the specified port.
        :param data: Word to write.
        :param port: Port to write to.
        """
        self.winring0.WriteIoPortWord(port, data)

    def outl(self, data: int, port: int) -> None:
        """
        Write a long (32 bit) to the specified port.
        :param data: Long to write.
        :param port: Port to write to.
        """
        self.winring0.WriteIoPortDword(port, data)

    def inb(self, port: int) -> int:
        """
        Read a byte (8 bit) from the specified port.
        :param port: Port to read from.
        :return: Byte read.
        """
        return self.winring0.ReadIoPortByte(port)

    def inw(self, port: int) -> int:
        """
        Read a word (16 bit) from the specified port.
        :param port: Port to read from.
        :return: Word read.
        """
        return self.winring0.ReadIoPortWord(port)

    def inl(self, port: int) -> int:
        """
        Read a long (32 bit) from the specified port.
        :param port: Port to read from.
        :return: Long read.
        """
        return self.winring0.ReadIoPortDword(port)

    def ioperm(self, port: int, num: int, turn_on: bool) -> None:
        """
        `ioperm` stub function. It's not required for WinRing0.
        """
        pass

    def iopl(self, level: int) -> None:
        """
        `iopl` stub function. It's not required for WinRing0.
        """
        pass
