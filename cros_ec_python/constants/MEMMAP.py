from .COMMON import BIT
from typing import Final

EC_MEMMAP_SIZE         : Final = 255 # ACPI IO buffer max is 255 bytes
EC_MEMMAP_TEXT_MAX     : Final = 8   # Size of a string in the memory map

# The offset address of each type of data in mapped memory.
EC_MEMMAP_TEMP_SENSOR      : Final = 0x00 # Temp sensors 0x00 - 0x0f
EC_MEMMAP_FAN              : Final = 0x10 # Fan speeds 0x10 - 0x17
EC_MEMMAP_TEMP_SENSOR_B    : Final = 0x18 # More temp sensors 0x18 - 0x1f
EC_MEMMAP_ID               : Final = 0x20 # 0x20 == 'E', 0x21 == 'C'
EC_MEMMAP_ID_VERSION       : Final = 0x22 # Version of data in 0x20 - 0x2f
EC_MEMMAP_THERMAL_VERSION  : Final = 0x23 # Version of data in 0x00 - 0x1f
EC_MEMMAP_BATTERY_VERSION  : Final = 0x24 # Version of data in 0x40 - 0x7f
EC_MEMMAP_SWITCHES_VERSION : Final = 0x25 # Version of data in 0x30 - 0x33
EC_MEMMAP_EVENTS_VERSION   : Final = 0x26 # Version of data in 0x34 - 0x3f
EC_MEMMAP_HOST_CMD_FLAGS   : Final = 0x27 # Host cmd interface flags (8 bits)
# Unused 0x28 - 0x2f
EC_MEMMAP_SWITCHES         : Final = 0x30	# 8 bits
# Unused 0x31 - 0x33
EC_MEMMAP_HOST_EVENTS      : Final = 0x34 # 64 bits
# Battery values are all 32 bits, unless otherwise noted.
EC_MEMMAP_BATT_VOLT        : Final = 0x40 # Battery Present Voltage
EC_MEMMAP_BATT_RATE        : Final = 0x44 # Battery Present Rate
EC_MEMMAP_BATT_CAP         : Final = 0x48 # Battery Remaining Capacity
EC_MEMMAP_BATT_FLAG        : Final = 0x4c # Battery State, see below (8-bit)
EC_MEMMAP_BATT_COUNT       : Final = 0x4d # Battery Count (8-bit)
EC_MEMMAP_BATT_INDEX       : Final = 0x4e # Current Battery Data Index (8-bit)
# Unused 0x4f
EC_MEMMAP_BATT_DCAP        : Final = 0x50 # Battery Design Capacity
EC_MEMMAP_BATT_DVLT        : Final = 0x54 # Battery Design Voltage
EC_MEMMAP_BATT_LFCC        : Final = 0x58 # Battery Last Full Charge Capacity
EC_MEMMAP_BATT_CCNT        : Final = 0x5c # Battery Cycle Count
# Strings are all 8 bytes (EC_MEMMAP_TEXT_MAX)
EC_MEMMAP_BATT_MFGR        : Final = 0x60 # Battery Manufacturer String
EC_MEMMAP_BATT_MODEL       : Final = 0x68 # Battery Model Number String
EC_MEMMAP_BATT_SERIAL      : Final = 0x70 # Battery Serial Number String
EC_MEMMAP_BATT_TYPE        : Final = 0x78 # Battery Type String
EC_MEMMAP_ALS              : Final = 0x80 # ALS readings in lux (2 X 16 bits)
# Unused 0x84 - 0x8f
EC_MEMMAP_ACC_STATUS       : Final = 0x90 # Accelerometer status (8 bits )
# Unused 0x91
EC_MEMMAP_ACC_DATA         : Final = 0x92 # Accelerometers data 0x92 - 0x9f
# 0x92: Lid Angle if available, LID_ANGLE_UNRELIABLE otherwise
# 0x94 - 0x99: 1st Accelerometer
# 0x9a - 0x9f: 2nd Accelerometer
EC_MEMMAP_GYRO_DATA        : Final = 0xa0 # Gyroscope data 0xa0 - 0xa5
# Unused 0xa6 - 0xdf


# ACPI is unable to access memory mapped data at or above this offset due to
# limitations of the ACPI protocol. Do not place data in the range 0xe0 - 0xfe
# which might be needed by ACPI.

EC_MEMMAP_NO_ACPI : Final = 0xe0

# Define the format of the accelerometer mapped memory status byte.
EC_MEMMAP_ACC_STATUS_SAMPLE_ID_MASK  : Final = 0x0f
EC_MEMMAP_ACC_STATUS_BUSY_BIT        : Final = BIT(4)
EC_MEMMAP_ACC_STATUS_PRESENCE_BIT    : Final = BIT(7)

# Number of temp sensors at EC_MEMMAP_TEMP_SENSOR
EC_TEMP_SENSOR_ENTRIES     : Final = 16

# Number of temp sensors at EC_MEMMAP_TEMP_SENSOR_B.
#
# Valid only if EC_MEMMAP_THERMAL_VERSION returns >= 2.

EC_TEMP_SENSOR_B_ENTRIES      : Final = 8

# Special values for mapped temperature sensors
EC_TEMP_SENSOR_NOT_PRESENT    : Final = 0xff
EC_TEMP_SENSOR_ERROR          : Final = 0xfe
EC_TEMP_SENSOR_NOT_POWERED    : Final = 0xfd
EC_TEMP_SENSOR_NOT_CALIBRATED : Final = 0xfc

# The offset of temperature value stored in mapped memory.  This allows
# reporting a temperature range of 200K to 454K = -73C to 181C.

EC_TEMP_SENSOR_OFFSET      : Final = 200


# Number of ALS readings at EC_MEMMAP_ALS

EC_ALS_ENTRIES             : Final = 2


# The default value a temperature sensor will return when it is present but
# has not been read this boot.  This is a reasonable number to avoid
# triggering alarms on the host.

EC_TEMP_SENSOR_DEFAULT     : Final = (296 - EC_TEMP_SENSOR_OFFSET)

EC_FAN_SPEED_ENTRIES       : Final = 4       # Number of fans at EC_MEMMAP_FAN
EC_FAN_SPEED_NOT_PRESENT   : Final = 0xffff  # Entry not present
EC_FAN_SPEED_STALLED       : Final = 0xfffe  # Fan stalled

# Battery bit flags at EC_MEMMAP_BATT_FLAG.
EC_BATT_FLAG_AC_PRESENT   : Final = 0x01
EC_BATT_FLAG_BATT_PRESENT : Final = 0x02
EC_BATT_FLAG_DISCHARGING  : Final = 0x04
EC_BATT_FLAG_CHARGING     : Final = 0x08
EC_BATT_FLAG_LEVEL_CRITICAL : Final = 0x10
# Set if some of the static/dynamic data is invalid (or outdated).
EC_BATT_FLAG_INVALID_DATA : Final = 0x20

# Switch flags at EC_MEMMAP_SWITCHES
EC_SWITCH_LID_OPEN               : Final = 0x01
EC_SWITCH_POWER_BUTTON_PRESSED   : Final = 0x02
EC_SWITCH_WRITE_PROTECT_DISABLED : Final = 0x04
# Was recovery requested via keyboard; now unused.
EC_SWITCH_IGNORE1		 : Final = 0x08
# Recovery requested via dedicated signal (from servo board)
EC_SWITCH_DEDICATED_RECOVERY     : Final = 0x10
# Was fake developer mode switch; now unused.  Remove in next refactor.
EC_SWITCH_IGNORE0                : Final = 0x20

# Host command interface flags
# Host command interface supports LPC args (LPC interface only)
EC_HOST_CMD_FLAG_LPC_ARGS_SUPPORTED  : Final = 0x01
# Host command interface supports version 3 protocol
EC_HOST_CMD_FLAG_VERSION_3   : Final = 0x02

# Wireless switch flags
EC_WIRELESS_SWITCH_ALL       : Final = ~0x00  # All flags
EC_WIRELESS_SWITCH_WLAN       : Final = 0x01  # WLAN radio
EC_WIRELESS_SWITCH_BLUETOOTH  : Final = 0x02  # Bluetooth radio
EC_WIRELESS_SWITCH_WWAN       : Final = 0x04  # WWAN power
EC_WIRELESS_SWITCH_WLAN_POWER : Final = 0x08  # WLAN power
