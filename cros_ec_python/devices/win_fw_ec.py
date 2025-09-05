from typing import Final
import warnings
import os
import ctypes
from ctypes import wintypes

# Workaround for pdoc failing on Linux
if os.name == 'nt':
    from ctypes import windll

__all__ = ["WinFrameworkEc"]

from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..constants.MEMMAP import EC_MEMMAP_SIZE
from ..exceptions import ECError

FILE_GENERIC_READ: Final    = 0x80000000
FILE_GENERIC_WRITE: Final   = 0x40000000
FILE_SHARE_READ: Final      = 0x00000001
FILE_SHARE_WRITE: Final     = 0x00000002
OPEN_EXISTING: Final        = 3

FILE_READ_DATA: Final       = 0x0001
FILE_WRITE_DATA: Final      = 0x0002
FILE_READ_ACCESS: Final     = 0x0001
METHOD_BUFFERED: Final      = 0

INVALID_HANDLE_VALUE: Final = -1


def CTL_CODE(device_type, function, method, access) -> int:
    return (device_type << 16) | (access << 14) | (function << 2) | method


CROSEC_CMD_MAX_REQUEST = 0x100

FILE_DEVICE_CROS_EMBEDDED_CONTROLLER = 0x80EC

IOCTL_CROSEC_XCMD = CTL_CODE(
    FILE_DEVICE_CROS_EMBEDDED_CONTROLLER,
    0x801,
    METHOD_BUFFERED,
    FILE_READ_DATA | FILE_WRITE_DATA,
)
IOCTL_CROSEC_RDMEM = CTL_CODE(
    FILE_DEVICE_CROS_EMBEDDED_CONTROLLER,
    0x802,
    METHOD_BUFFERED,
    FILE_READ_ACCESS,
)


def CreateFileW(
    filename: str, access: int, mode: int, creation: int, flags: int
) -> wintypes.HANDLE:
    knl32_CreateFileW = windll.kernel32.CreateFileW
    knl32_CreateFileW.argtypes = [
            wintypes.LPCWSTR, # lpFileName
            wintypes.DWORD,   # dwDesiredAccess
            wintypes.DWORD,   # dwShareMode
            wintypes.LPVOID,  # lpSecurityAttributes
            wintypes.DWORD,   # dwCreationDisposition
            wintypes.DWORD,   # dwFlagsAndAttributes
            wintypes.HANDLE,  # hTemplateFile
        ]
    knl32_CreateFileW.restype = wintypes.HANDLE

    return wintypes.HANDLE(
        knl32_CreateFileW(filename, access, mode, 0, creation, flags, 0)
    )


def DeviceIoControl(
    handle: wintypes.HANDLE,
    ioctl: int,
    inbuf: ctypes.pointer,
    insize: int,
    outbuf: ctypes.pointer,
    outsize: int,
) -> bool:
    knl32_DeviceIoControl = windll.kernel32.DeviceIoControl
    knl32_DeviceIoControl.argtypes = [
        wintypes.HANDLE,  # hDevice
        wintypes.DWORD,   # dwIoControlCode
        wintypes.LPVOID,  # lpInBuffer
        wintypes.DWORD,   # nInBufferSize
        wintypes.LPVOID,  # lpOutBuffer
        wintypes.DWORD,   # nOutBufferSize
        wintypes.LPDWORD, # lpBytesReturned
        wintypes.LPVOID,  # lpOverlapped
    ]
    knl32_DeviceIoControl.restype = wintypes.BOOL

    status = knl32_DeviceIoControl(
        handle, ioctl, inbuf, insize, outbuf, outsize, None, None
    )

    return bool(status)


class WinFrameworkEc(CrosEcClass):
    """
    Class to interact with the EC using the Framework EC Windows Driver.
    """

    def __init__(self, handle: wintypes.HANDLE | None = None):
        """
        Initialise communication with the Framework EC driver.
        :param handle: Use a custom device handle, opens one by default.
        """
        if handle is None:
            handle = CreateFileW(
                r"\\.\GLOBALROOT\Device\CrosEC",
                FILE_GENERIC_READ | FILE_GENERIC_WRITE,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                OPEN_EXISTING,
                0,
            )

        if handle.value == wintypes.HANDLE(INVALID_HANDLE_VALUE).value:
            errno = windll.kernel32.GetLastError()
            raise OSError(f"{errno}: {ctypes.FormatError(errno)}")

        self.handle: wintypes.HANDLE = handle
        r"""The handle for \\.\GLOBALROOT\Device\CrosEC."""

    def __del__(self):
        self.ec_exit()

    @staticmethod
    def detect() -> bool:
        r"""
        Checks for `\\.\GLOBALROOT\Device\CrosEC` and returns True if it exists.
        """
        return os.path.exists(r"\\.\GLOBALROOT\Device\CrosEC")

    def ec_init(self) -> None:
        pass

    def ec_exit(self) -> None:
        """
        Close the file on exit.
        """
        if hasattr(self, "handle"):
            windll.kernel32.CloseHandle(self.handle)

    def command(
        self,
        version: Int32,
        command: Int32,
        outsize: Int32,
        insize: Int32,
        data: bytes = None,
        warn: bool = True,
    ) -> bytes:
        """
        Send a command to the EC and return the response.
        :param version: Command version number (often 0).
        :param command: Command to send (EC_CMD_...).
        :param outsize: Outgoing length in bytes.
        :param insize: Max number of bytes to accept from the EC.
        :param data: Outgoing data to EC.
        :param warn: Whether to warn if the response size is not as expected. Default is True.
        :return: Incoming data from EC.
        """
        if data is None:
            data = bytes(outsize)

        class CrosEcCommand(ctypes.Structure):
            _fields_ = [
                ("version", ctypes.c_uint32),
                ("command", ctypes.c_uint32),
                ("outsize", ctypes.c_uint32),
                ("insize", ctypes.c_uint32),
                ("result", ctypes.c_uint32),
                ("buffer", ctypes.c_ubyte * (CROSEC_CMD_MAX_REQUEST - (4 * 5))),
            ]

        cmd = CrosEcCommand()
        cmd.version = version
        cmd.command = command
        cmd.outsize = outsize
        cmd.insize = insize
        cmd.result = 0xFF
        ctypes.memmove(ctypes.addressof(cmd.buffer), data, len(data))
        p_cmd = ctypes.pointer(cmd)

        status = DeviceIoControl(
            self.handle,
            IOCTL_CROSEC_XCMD,
            p_cmd,
            ctypes.sizeof(CrosEcCommand),
            p_cmd,
            ctypes.sizeof(CrosEcCommand),
        )
        if not status:
            errno = windll.kernel32.GetLastError()
            raise IOError(
                f"ioctl failed with error {errno}: {ctypes.FormatError(errno)}"
            )

        if cmd.insize != insize:
            warnings.warn(
                f"Expected {insize} bytes, got {cmd.insize} back from EC",
                RuntimeWarning,
            )

        if cmd.result != 0:
            raise ECError(cmd.result)

        return bytes(cmd.buffer[:insize])

    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        :param offset: Offset to read from.
        :param num_bytes: Number of bytes to read.
        :return: Bytes read from the EC.
        """

        class CrosEcReadMem(ctypes.Structure):
            _fields_ = [
                ("offset", ctypes.c_uint32),
                ("bytes", ctypes.c_uint32),
                ("buffer", ctypes.c_ubyte * EC_MEMMAP_SIZE),
            ]

        data = CrosEcReadMem()
        data.offset = offset
        data.bytes = num_bytes
        p_data = ctypes.pointer(data)

        status = DeviceIoControl(
            self.handle,
            IOCTL_CROSEC_RDMEM,
            p_data,
            ctypes.sizeof(CrosEcReadMem),
            p_data,
            ctypes.sizeof(CrosEcReadMem),
        )

        if not status:
            errno = windll.kernel32.GetLastError()
            raise IOError(
                f"ioctl failed with error {errno}: {ctypes.FormatError(errno)}"
            )

        if data.bytes != num_bytes:
            warnings.warn(
                f"Expected {num_bytes} bytes, got {data.bytes} back from EC",
                RuntimeWarning,
            )

        return bytes(data.buffer[:num_bytes])
