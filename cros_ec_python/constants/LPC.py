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
EC_LPC_ADDR_MEMMAP_FWAMD : Final = 0xE00  # Address on AMD Framework Laptops


# Value written to legacy command port / prefix byte to indicate protocol
# 3+ structs are being used.  Usage is bus-dependent.

EC_COMMAND_PROTOCOL_3: Final = 0xda

EC_HOST_REQUEST_VERSION: Final = 3

EC_HOST_RESPONSE_VERSION: Final = 3


# LPC command status byte masks
# EC has written a byte in the data register and host hasn't read it yet
EC_LPC_STATUS_TO_HOST     :Final = 0x01
# Host has written a command/data byte and the EC hasn't read it yet
EC_LPC_STATUS_FROM_HOST   :Final = 0x02
# EC is processing a command
EC_LPC_STATUS_PROCESSING  :Final = 0x04
# Last write to EC was a command, not data
EC_LPC_STATUS_LAST_CMD    :Final = 0x08
# EC is in burst mode
EC_LPC_STATUS_BURST_MODE  :Final = 0x10
# SCI event is pending (requesting SCI query)
EC_LPC_STATUS_SCI_PENDING :Final = 0x20
# SMI event is pending (requesting SMI query)
EC_LPC_STATUS_SMI_PENDING :Final = 0x40
# (reserved)
EC_LPC_STATUS_RESERVED    :Final = 0x80


# EC is busy.  This covers both the EC processing a command, and the host has
# written a new command but the EC hasn't picked it up yet.

EC_LPC_STATUS_BUSY_MASK :Final = EC_LPC_STATUS_FROM_HOST | EC_LPC_STATUS_PROCESSING


# Flags for ec_lpc_host_args.flags
#
# Args are from host.  Data area at EC_LPC_ADDR_HOST_PARAM contains command
# params.
#
# If EC gets a command and this flag is not set, this is an old-style command.
# Command version is 0 and params from host are at EC_LPC_ADDR_OLD_PARAM with
# unknown length.  EC must respond with an old-style response (that is,
# without setting EC_HOST_ARGS_FLAG_TO_HOST).

EC_HOST_ARGS_FLAG_FROM_HOST: Final = 0x01

# Args are from EC.  Data area at EC_LPC_ADDR_HOST_PARAM contains response.
#
# If EC responds to a command and this flag is not set, this is an old-style
# response.  Command version is 0 and response data from EC is at
# EC_LPC_ADDR_OLD_PARAM with unknown length.

EC_HOST_ARGS_FLAG_TO_HOST: Final = 0x02
