from enum import Enum

# Type hints, only for code readability
Int8 = int
Int16 = int
Int32 = int
Int64 = int
UInt8 = int
UInt16 = int
UInt32 = int
UInt64 = int


# Macros from linux
def BIT(nr):
    return 1 << nr


class EcStatus(Enum):
    """
    Host command response codes (16-bit).
    """
    EC_RES_SUCCESS = 0
    EC_RES_INVALID_COMMAND = 1
    EC_RES_ERROR = 2
    EC_RES_INVALID_PARAM = 3
    EC_RES_ACCESS_DENIED = 4
    EC_RES_INVALID_RESPONSE = 5
    EC_RES_INVALID_VERSION = 6
    EC_RES_INVALID_CHECKSUM = 7
    EC_RES_IN_PROGRESS = 8
    "Accepted, command in progress"
    EC_RES_UNAVAILABLE = 9
    "No response available"
    EC_RES_TIMEOUT = 10
    "We got a timeout"
    EC_RES_OVERFLOW = 11
    "Table / data overflow"
    EC_RES_INVALID_HEADER = 12
    "Header contains invalid data"
    EC_RES_REQUEST_TRUNCATED = 13
    "Didn't get the entire request"
    EC_RES_RESPONSE_TOO_BIG = 14
    "Response was too big to handle"
    EC_RES_BUS_ERROR = 15
    "Communications bus error"
    EC_RES_BUSY = 16
    "Up but too busy.  Should retry"
    EC_RES_INVALID_HEADER_VERSION = 17
    "Header version invalid"
    EC_RES_INVALID_HEADER_CRC = 18
    "Header CRC invalid"
    EC_RES_INVALID_DATA_CRC = 19
    "Data CRC invalid"
    EC_RES_DUP_UNAVAILABLE = 20
    "Can't resend response"
