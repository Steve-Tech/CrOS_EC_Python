import portio
from .constants.COMMON import *
from .constants.LPC import *
from .constants.MEMMAP import *


def ec_init(address: Int32 = EC_LPC_ADDR_MEMMAP):
    if portio.ioperm(address, EC_MEMMAP_SIZE, True):
        print("Permission denied. Try running as root.")
        exit(1)


def ec_readmem(offset: Int32, num_bytes: Int32, address: Int32 = EC_LPC_ADDR_MEMMAP) -> bytes:
    """
    Read memory from the EC.
    @param offset: Offset to read from.
    @param num_bytes: Number of bytes to read.
    @return: Bytes read from the EC.
    """
    data = bytearray()
    for i in range(num_bytes):
        data.append(portio.inb(address + offset + i))
    return bytes(data)
