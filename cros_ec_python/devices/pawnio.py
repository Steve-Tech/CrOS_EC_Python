import struct
import warnings
import ctypes
import os
from ctypes import wintypes
from ctypes import util as ctypes_util

from ..baseclass import CrosEcClass
from ..constants.COMMON import *
from ..exceptions import ECError


class CrosEcPawnIO(CrosEcClass):
    """
    Class to interact with the EC using the Windows PawnIO driver.
    """

    def __init__(self, dll: str | None = None, bin: str | None = None):
        """
        Initialise the EC using the Linux cros_ec device.
        :param dll: Path to the DLL to use. If None, will use the default path.
        :param bin: Path to the binary to load. If None, will use the default path.
        """

        self.bin = bin or "LpcCrOSEC.bin"

        if dll or (dll := ctypes_util.find_library("PawnIOLib.dll")):
            self.pawniolib = ctypes.OleDLL(dll)
        else:
            # Let this raise an error if we can't find it
            self.pawniolib = ctypes.OleDLL("C:\\Program Files\\PawnIO\\PawnIOLib.dll")

        self.pawniolib.pawnio_version.argtypes = [ctypes.POINTER(wintypes.ULONG)]
        self.pawniolib.pawnio_open.argtypes = [ctypes.POINTER(wintypes.HANDLE)]
        self.pawniolib.pawnio_load.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_size_t,
        ]
        self.pawniolib.pawnio_execute.argtypes = [
            wintypes.HANDLE,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_ulonglong),
            ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_size_t),
        ]
        self.pawniolib.pawnio_close.argtypes = [wintypes.HANDLE]

        self.ec_init()

    def __del__(self):
        self.ec_exit()

    def _pawnio_version(self) -> str:
        version = wintypes.ULONG()
        self.pawniolib.pawnio_version(ctypes.byref(version))
        major, minor, patch = (
            version.value >> 16,
            (version.value >> 8) & 0xFF,
            version.value & 0xFF,
        )
        return f"{major}.{minor}.{patch}"

    def _pawnio_open(self) -> None:
        self.handle = wintypes.HANDLE()
        self.pawniolib.pawnio_open(ctypes.byref(self.handle))

    def _pawnio_load(self, filepath: str) -> None:
        with open(filepath, "rb") as file:
            blob = file.read()
        size = len(blob)
        blob_array = (ctypes.c_ubyte * size)(*blob)
        self.pawniolib.pawnio_load(self.handle, blob_array, size)

    def _pawnio_execute(
        self,
        function: str,
        in_data: bytes,
        out_size: bytes,
        in_size: int | None = None,
    ) -> tuple[int | ctypes.Array]:
        function_bytes = function.encode("utf-8")
        in_size = in_size if in_size is not None else len(in_data)
        in_array = (ctypes.c_ulonglong * in_size)(*in_data)
        out_array = (ctypes.c_ulonglong * out_size)()
        return_size = ctypes.c_size_t()

        self.pawniolib.pawnio_execute(
            self.handle,
            function_bytes,
            in_array,
            in_size,
            out_array,
            out_size,
            ctypes.byref(return_size),
        )

        return (return_size.value, out_array)

    def _pawnio_close(self):
        self.pawniolib.pawnio_close(self.handle)

    @staticmethod
    def detect() -> bool:
        """
        Detect if the PawnIO driver is installed.
        """
        return bool(ctypes_util.find_library("PawnIOLib.dll")) or os.path.exists(
            "C:\\Program Files\\PawnIO\\PawnIOLib.dll"
        )

    def ec_init(self) -> None:
        self._pawnio_open()
        self._pawnio_load(self.bin)

    def ec_exit(self) -> None:
        """
        Close the file on exit.
        """
        if hasattr(self, "handle"):
            self._pawnio_close()

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
        # LpcCrOSEC returns the EC result too
        pawn_insize = insize + 1
        header = struct.pack("<HB", command, version)
        size, res = self._pawnio_execute(
            "ioctl_ec_command",
            header + (data or b""),
            pawn_insize,
            in_size=outsize + len(header),
        )

        if size != pawn_insize and warn:
            warnings.warn(
                f"Expected {pawn_insize} bytes, got {size} back from PawnIO",
                RuntimeWarning,
            )

        # If the first cell is negative, it has failed
        # Also convert to signed
        if res[0] & (1 << 63):
            signed_res = res[0] - (1 << 64)
            raise ECError(-signed_res)

        # Otherwise it's the length
        if res[0] != insize and warn:
            warnings.warn(
                f"Expected {pawn_insize} bytes, got {res[0]} back from EC",
                RuntimeWarning,
            )

        # The pawn cells are 64bit but all the values should fit in 8 bits
        return bytes(res[1:])

    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        :param offset: Offset to read from.
        :param num_bytes: Number of bytes to read.
        :return: Bytes read from the EC.
        """
        size, res = self._pawnio_execute(
            "ioctl_ec_readmem", offset.to_bytes(1), num_bytes
        )

        array = bytearray(size)
        for i in range(size):
            array[i] = res[i]
        return bytes(array)
