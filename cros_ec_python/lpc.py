import portio
from .constants.LPC import *
from .constants.MEMMAP import *


def ec_init(address: int = EC_LPC_ADDR_MEMMAP):
    if portio.ioperm(EC_LPC_ADDR_MEMMAP, EC_MEMMAP_SIZE, True):
        print("Permission denied. Try running as root.")
        exit(1)


def ec_readmem(offset: int, num_bytes: int, address: int = EC_LPC_ADDR_MEMMAP) -> bytes:
    """
    Read memory from the EC.
    @param offset: Offset to read from.
    @param num_bytes: Number of bytes to read.
    @return: Bytes read from the EC.
    """
    buf = None
    print(portio.insb(address + offset, buf, num_bytes))
    return buf
