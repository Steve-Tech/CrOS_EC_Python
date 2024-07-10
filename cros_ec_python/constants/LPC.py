from .COMMON import BIT
from typing import Final

# I/O addresses for ACPI commands
EC_LPC_ADDR_ACPI_DATA  : Final = 0x62
EC_LPC_ADDR_ACPI_CMD   : Final = 0x66

# I/O addresses for host command
EC_LPC_ADDR_HOST_DATA  : Final = 0x200
EC_LPC_ADDR_HOST_CMD   : Final = 0x204

# I/O addresses for host command args and params
# Protocol version 2
EC_LPC_ADDR_HOST_ARGS    : Final = 0x800  # And 0x801, 0x802, 0x803
EC_LPC_ADDR_HOST_PARAM   : Final = 0x804  # For version 2 params; size is
				  # EC_PROTO2_MAX_PARAM_SIZE
					
# Protocol version 3
EC_LPC_ADDR_HOST_PACKET  : Final = 0x800  # Offset of version 3 packet
EC_LPC_HOST_PACKET_SIZE  : Final = 0x100  # Max size of version 3 packet


# The actual block is 0x800-0x8ff, but some BIOSes think it's 0x880-0x8ff
# and they tell the kernel that so we have to think of it as two parts.
#
# Other BIOSes report only the I/O port region spanned by the Microchip
# MEC series EC; an attempt to address a larger region may fail.

EC_HOST_CMD_REGION0       : Final = 0x800
EC_HOST_CMD_REGION1       : Final = 0x880
EC_HOST_CMD_REGION_SIZE    : Final = 0x80
EC_HOST_CMD_MEC_REGION_SIZE : Final = 0x8

# EC command register bit functions
EC_LPC_CMDR_DATA	: Final = BIT(0)  # Data ready for host to read
EC_LPC_CMDR_PENDING	: Final = BIT(1)  # Write pending to EC
EC_LPC_CMDR_BUSY	: Final = BIT(2)  # EC is busy processing a command
EC_LPC_CMDR_CMD		: Final = BIT(3)  # Last host write was a command
EC_LPC_CMDR_ACPI_BRST	: Final = BIT(4)  # Burst mode (not used)
EC_LPC_CMDR_SCI		: Final = BIT(5)  # SCI event is pending
EC_LPC_CMDR_SMI		: Final = BIT(6)  # SMI event is pending

EC_LPC_ADDR_MEMMAP       : Final = 0x900
