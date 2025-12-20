# CrOS_EC_Python

A Python library for interacting with a Chrome OS EC. Commonly found in Chromebooks and Framework laptops.

It provides a somewhat lower-level interface to the CrOS EC, allowing you to send and receive any EC command,
and read any byte from the memory map.
As well as a higher-level abstracted interface for easy access to some of the more common commands.

## Installation

### Linux

> [!NOTE]
> Don't forget to read the [permissions](#permissions) section below.

For a basic installation with full Linux Device support, run:

```bash
pip install cros-ec-python
```

Some interfaces require additional dependencies, for example the LPC interface performs best with the `portio` package:

```bash
pip install cros-ec-python[lpc]
```

#### Permissions

Since we're playing around with actual hardware, we're going to need some pretty high permissions.

The recommended way is to copy [`60-cros_ec_python.rules`](60-cros_ec_python.rules) to `/etc/udev/rules.d/` and run:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

This will give the current user access to both `/dev/cros_ec` for the Linux Device interface, and the IO ports for the LPC interface.


##### Linux Device Interface

This library requires write permission to `/dev/cros_ec` when using the Linux Device interface,
which is usually only accessible by root. You can either run your script as root, add a udev rule,
or just manually change the permissions. Read permission is not needed, only write.

##### LPC Bus Interface

This library requires access to IO ports using the `CAP_SYS_RAWIO` capability.
It's easiest just to run your script as root.

### Windows

> [!NOTE]
> Loading a driver will likely require administrator permissions, so you may need to run your script as an administrator.

The Windows version supports 3 different drivers to access the EC:

- The Framework EC driver which is provided in the driver bundles and requires a supported BIOS version. This driver does not require administrator and is the recommended way of using CrOS_EC_Python on supported devices.
- `PawnIO` which is a fairly new scriptable kernel driver, the official signed version can be downloaded [here](https://pawnio.eu/).
- `WinRing0` which while still signed, it has been abandoned and is listed on the Microsoft Vulnerable Driver Blocklist.

Install one of the drivers, and then install the package using pip:

```bash
pip install cros-ec-python
```

#### PawnIO

> [!TIP]
> PawnIO is [designed to be a secure alternative to WinRing0](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/issues/984#issuecomment-1585591691), and is recommended over WinRing0.

[PawnIO](https://pawnio.eu/) can be installed using the installer from the website.
PawnIO is signed and does not require disabling driver signature enforcement.

You will also need to download the [`LpcCrOSEC`](https://github.com/namazso/PawnIO.Modules/pull/3) module, and copy it to your working directory.

#### WinRing0

> [!WARNING]
> WinRing0 is listed on the Microsoft Vulnerable Driver Blocklist, making it frequently flagged by antivirus and anti cheat software. Download links are not provided, use at your own risk.

Alternatively, WinRing0 can be used to access the IO ports required for communication to the EC. You can find signed versions online, that do not require disabling driver signature enforcement.

You will need to copy `WinRing0x64.dll` and `WinRing0x64.sys` to either the same
directory as `python.exe`, or to `C:\Windows\System32`.

## Documentation

The documentation for this project can be found [here](https://steve-tech.github.io/CrOS_EC_Python).

There are also some examples in the [`examples`](https://github.com/Steve-Tech/CrOS_EC_Python/tree/main/examples) directory,
and every function has usage in the [`tests`](https://github.com/Steve-Tech/CrOS_EC_Python/tree/main/tests) directory.

### Running Tests

> [!CAUTION]
> This will test against your EC, nothing is mocked.

This package uses the built-in `unittest` module for testing. To run the tests, simply run:

```bash
cd tests
python -m unittest
```

### Generating Documentation

The documentation is generated using `pdoc`. To generate the documentation, run:

```bash
pdoc -o docs/ cros_ec_python
```

Or to generate the documentation and serve it locally:

```bash
pdoc cros_ec_python
```

### Supported Interfaces

- [x] Linux Device (Requires the `cros_ec_dev` kernel module)
- [x] Windows Framework EC Driver
- [x] Windows [PawnIO](https://pawnio.eu/) using [LpcCrOSEC](https://github.com/namazso/PawnIO.Modules/pull/3)
- [x] LPC Bus Interface (Soft-requires the [`portio` package](https://pypi.org/project/portio/))
- [ ] MEC LPC Interface
- [ ] I2C Interface
- [ ] Servo SPI Interface

### Supported Commands

> [!NOTE]
> The goal of this project is *not* to abstract away 100% of the CrOS EC commands, but to abstract the ones that may be useful.
> If a command is not abstracted it can still be used by calling the `ec.command()` method instead.

Here's a list of all known CrOS EC commands, and whether they are abstracted in this library.
The implemented commands are split up into modules for maintainability reasons.

<details>
<summary>Implemented CrOS commands</summary>

**General / test commands (`general`)**

- [x] `EC_CMD_PROTO_VERSION` (`0x0000`)
- [x] `EC_CMD_HELLO` (`0x0001`)
- [x] `EC_CMD_GET_VERSION` (`0x0002`)
- [ ] `EC_CMD_READ_TEST` (`0x0003`)
- [x] `EC_CMD_GET_BUILD_INFO` (`0x0004`)
- [x] `EC_CMD_GET_CHIP_INFO` (`0x0005`)
- [x] `EC_CMD_GET_BOARD_VERSION` (`0x0006`)
- [ ] `EC_CMD_READ_MEMMAP` (`0x0007`)
- [x] `EC_CMD_GET_CMD_VERSIONS` (`0x0008`)
- [ ] `EC_CMD_GET_COMMS_STATUS` (`0x0009`)
- [x] `EC_CMD_TEST_PROTOCOL` (`0x000A`)
- [x] `EC_CMD_GET_PROTOCOL_INFO` (`0x000B`)

**Get/Set miscellaneous values (`system`)**

- [ ] `EC_CMD_GSV_PAUSE_IN_S5` (`0x000C`)
- [x] `EC_CMD_GET_FEATURES` (`0x000D`)
- [ ] `EC_CMD_GET_SKU_ID` (`0x000E`)
- [ ] `EC_CMD_SET_SKU_ID` (`0x000F`)

**Flash commands (`flash`)**

- [ ] `EC_CMD_FLASH_INFO` (`0x0010`)
- [ ] `EC_CMD_FLASH_READ` (`0x0011`)
- [ ] `EC_CMD_FLASH_WRITE` (`0x0012`)
- [ ] `EC_CMD_FLASH_ERASE` (`0x0013`)
- [ ] `EC_CMD_FLASH_PROTECT` (`0x0015`)
- [ ] `EC_CMD_FLASH_REGION_INFO` (`0x0016`)
- [ ] `EC_CMD_FLASH_SPI_INFO` (`0x0018`)
- [ ] `EC_CMD_FLASH_SELECT` (`0x0019`)

**Cryptography and Sysinfo (`system`)**

- [ ] `EC_CMD_RAND_NUM` (`0x001A`)
- [ ] `EC_CMD_RWSIG_INFO` (`0x001B`)
- [ ] `EC_CMD_SYSINFO` (`0x001C`)

**PWM commands (`pwm`)**

- [x] `EC_CMD_PWM_GET_FAN_TARGET_RPM` (`0x0020`)
- [x] `EC_CMD_PWM_SET_FAN_TARGET_RPM` (`0x0021`)
- [x] `EC_CMD_PWM_GET_KEYBOARD_BACKLIGHT` (`0x0022`)
- [x] `EC_CMD_PWM_SET_KEYBOARD_BACKLIGHT` (`0x0023`)
- [x] `EC_CMD_PWM_SET_FAN_DUTY` (`0x0024`)
- [x] `EC_CMD_PWM_SET_DUTY` (`0x0025`)
- [x] `EC_CMD_PWM_GET_DUTY` (`0x0026`)

**Lightbar commands (`lightbar`)**

- [ ] `EC_CMD_LIGHTBAR_CMD` (`0x0028`)

**LED control commands (`leds`)**

- [x] `EC_CMD_LED_CONTROL` (`0x0029`)

**Verified boot commands (`system`)**

- [ ] `EC_CMD_VBOOT_HASH` (`0x002A`)

**Motion sense commands (`motion_sense`)**

- [ ] `EC_CMD_MOTION_SENSE_CMD` (`0x002B`)

**Power control commands (`system`)**

- [ ] `EC_CMD_FORCE_LID_OPEN` (`0x002C`)
- [ ] `EC_CMD_CONFIG_POWER_BUTTON` (`0x002D`)
- [ ] `EC_CMD_USB_CHARGE_SET_MODE` (`0x0030`)
- [ ] `EC_CMD_SET_TABLET_MODE` (`0x0031`)

**Persistent storage for host (`pstore`)**

- [ ] `EC_CMD_PSTORE_INFO` (`0x0040`)
- [ ] `EC_CMD_PSTORE_READ` (`0x0041`)
- [ ] `EC_CMD_PSTORE_WRITE` (`0x0042`)

**Real-time clock (`rtc`)**

- [ ] `EC_CMD_RTC_GET_VALUE` (`0x0044`)
- [ ] `EC_CMD_RTC_GET_ALARM` (`0x0045`)
- [ ] `EC_CMD_RTC_SET_VALUE` (`0x0046`)
- [ ] `EC_CMD_RTC_SET_ALARM` (`0x0047`)

**Port 80 log access (`system`)**

- [ ] `EC_CMD_PORT80_LAST_BOOT` (`0x0048`)
- [ ] `EC_CMD_PORT80_READ` (`0x0048`)

**Get persistent storage info (`pstore`)**

- [ ] `EC_CMD_VSTORE_INFO` (`0x0049`)
- [ ] `EC_CMD_VSTORE_READ` (`0x004A`)
- [ ] `EC_CMD_VSTORE_WRITE` (`0x004B`)

**Thermal engine commands (`thermal`)**

- [x] `EC_CMD_THERMAL_SET_THRESHOLD` (`0x0050`)
- [x] `EC_CMD_THERMAL_GET_THRESHOLD` (`0x0051`)
- [x] `EC_CMD_THERMAL_AUTO_FAN_CTRL` (`0x0052`)
- [ ] `EC_CMD_TMP006_GET_CALIBRATION` (`0x0053`)
- [ ] `EC_CMD_TMP006_SET_CALIBRATION` (`0x0054`)
- [ ] `EC_CMD_TMP006_GET_RAW` (`0x0055`)

**MKBP - Matrix KeyBoard Protocol (`mkbp`)**

- [ ] `EC_CMD_MKBP_STATE` (`0x0060`)
- [ ] `EC_CMD_MKBP_INFO` (`0x0061`)
- [ ] `EC_CMD_MKBP_SIMULATE_KEY` (`0x0062`)
- [ ] `EC_CMD_MKBP_SET_CONFIG` (`0x0064`)
- [ ] `EC_CMD_MKBP_GET_CONFIG` (`0x0065`)
- [ ] `EC_CMD_KEYSCAN_SEQ_CTRL` (`0x0066`)
- [ ] `EC_CMD_GET_NEXT_EVENT` (`0x0067`)
- [ ] `EC_CMD_KEYBOARD_FACTORY_TEST` (`0x0068`)
- [ ] `EC_CMD_MKBP_WAKE_MASK` (`0x0069`)

**Temperature sensor commands (`thermal`)**

- [x] `EC_CMD_TEMP_SENSOR_GET_INFO` (`0x0070`)

**Host event commands (`events`)**

- [ ] `EC_CMD_HOST_EVENT_GET_B` (`0x0087`)
- [ ] `EC_CMD_HOST_EVENT_GET_SMI_MASK` (`0x0088`)
- [ ] `EC_CMD_HOST_EVENT_GET_SCI_MASK` (`0x0089`)
- [ ] `EC_CMD_HOST_EVENT_GET_WAKE_MASK` (`0x008D`)
- [ ] `EC_CMD_HOST_EVENT_SET_SMI_MASK` (`0x008A`)
- [ ] `EC_CMD_HOST_EVENT_SET_SCI_MASK` (`0x008B`)
- [ ] `EC_CMD_HOST_EVENT_CLEAR` (`0x008C`)
- [ ] `EC_CMD_HOST_EVENT_SET_WAKE_MASK` (`0x008E`)
- [ ] `EC_CMD_HOST_EVENT_CLEAR_B` (`0x008F`)
- [ ] `EC_CMD_HOST_EVENT` (`0x00A4`)

**Switch commands (`system`)**

- [ ] `EC_CMD_SWITCH_ENABLE_BKLIGHT` (`0x0090`)
- [ ] `EC_CMD_SWITCH_ENABLE_WIRELESS` (`0x0091`)

**GPIO commands (`gpio`)**

- [ ] `EC_CMD_GPIO_SET` (`0x0092`)
- [ ] `EC_CMD_GPIO_GET` (`0x0093`)

**I2C commands (`i2c`)**

- [ ] `EC_CMD_I2C_READ` (`0x0094`)
- [ ] `EC_CMD_I2C_WRITE` (`0x0095`)

**Charge state commands (`charge`)**

- [ ] `EC_CMD_CHARGE_CONTROL` (`0x0096`)

**Console commands (`console`)**

- [ ] `EC_CMD_CONSOLE_SNAPSHOT` (`0x0097`)
- [ ] `EC_CMD_CONSOLE_READ` (`0x0098`)

**Battery commands (`charge`)**

- [ ] `EC_CMD_BATTERY_CUT_OFF` (`0x0099`)

**USB port mux control (`usb`)**

- [ ] `EC_CMD_USB_MUX` (`0x009A`)

**LDOs / FETs control (`power`)**

- [ ] `EC_CMD_LDO_SET` (`0x009B`)
- [ ] `EC_CMD_LDO_GET` (`0x009C`)

**Power info (`power`)**

- [ ] `EC_CMD_POWER_INFO` (`0x009D`)

**I2C passthru command (`i2c`)**

- [ ] `EC_CMD_I2C_PASSTHRU` (`0x009E`)

**Power button hang detect (`system`)**

- [ ] `EC_CMD_HANG_DETECT` (`0x009F`)

**Commands for battery charging (`charge`)**

- [ ] `EC_CMD_CHARGE_STATE` (`0x00A0`)
- [ ] `EC_CMD_CHARGE_CURRENT_LIMIT` (`0x00A1`)
- [ ] `EC_CMD_EXTERNAL_POWER_LIMIT` (`0x00A2`)
- [ ] `EC_CMD_OVERRIDE_DEDICATED_CHARGER_LIMIT` (`0x00A3`)
- [ ] `EC_CMD_CHARGESPLASH` (`0x00A5`)

**Hibernate/Deep Sleep Commands (`system`)**

- [ ] `EC_CMD_HIBERNATION_DELAY` (`0x00A8`)
- [ ] `EC_CMD_HOST_SLEEP_EVENT` (`0x00A9`)

**Device events (`events`)**

- [ ] `EC_CMD_DEVICE_EVENT` (`0x00AA`)

**Get s0ix counter (`system`)**

- [ ] `EC_CMD_GET_S0IX_COUNTER` (`0x00AB`)

**Smart battery pass-through (`battery`)**

- [ ] `EC_CMD_SB_READ_WORD` (`0x00B0`)
- [ ] `EC_CMD_SB_WRITE_WORD` (`0x00B1`)
- [ ] `EC_CMD_SB_READ_BLOCK` (`0x00B2`)
- [ ] `EC_CMD_SB_WRITE_BLOCK` (`0x00B3`)

**Battery vendor parameters (`battery`)**

- [ ] `EC_CMD_BATTERY_VENDOR_PARAM` (`0x00B4`)

**Smart Battery Firmware Update (`battery`)**

- [ ] `EC_CMD_SB_FW_UPDATE` (`0x00B5`)
- [ ] `EC_CMD_ENTERING_MODE` (`0x00B6`)

**I2C passthru protection (`i2c`)**

- [ ] `EC_CMD_I2C_PASSTHRU_PROTECT` (`0x00B7`)

**HDMI CEC commands (`hdmi`)**

- [ ] `EC_CMD_CEC_WRITE_MSG` (`0x00B8`)
- [ ] `EC_CMD_CEC_SET` (`0x00BA`)
- [ ] `EC_CMD_CEC_GET` (`0x00BB`)

**Commands for audio codec (`audio`)**

- [ ] `EC_CMD_EC_CODEC` (`0x00BC`)
- [ ] `EC_CMD_EC_CODEC_DMIC` (`0x00BD`)
- [ ] `EC_CMD_EC_CODEC_I2S_RX` (`0x00BE`)
- [ ] `EC_CMD_EC_CODEC_WOV` (`0x00BF`)

**Commands for PoE PSE controller (`power`)**

- [ ] `EC_CMD_PSE` (`0x00C0`)

**System commands (`system`)**

- [ ] `EC_CMD_REBOOT_EC` (`0x00D2`)
- [ ] `EC_CMD_GET_PANIC_INFO` (`0x00D3`)
- [ ] `EC_CMD_REBOOT` (`0x00D1`) 'Think "die"'
- [ ] `EC_CMD_RESEND_RESPONSE` (`0x00DB`)
- [ ] `EC_CMD_VERSION0` (`0x00DC`)
- [ ] `EC_CMD_MEMORY_DUMP_GET_METADATA` (`0x00DD`)
- [ ] `EC_CMD_MEMORY_DUMP_GET_ENTRY_INFO` (`0x00DE`)
- [ ] `EC_CMD_MEMORY_DUMP_READ_MEMORY` (`0x00DF`)

**PD commands (`usb`)**

- [ ] `EC_CMD_PD_EXCHANGE_STATUS` (`0x0100`)
- [ ] `EC_CMD_PD_HOST_EVENT_STATUS` (`0x0104`)
- [ ] `EC_CMD_USB_PD_CONTROL` (`0x0101`)
- [ ] `EC_CMD_USB_PD_PORTS` (`0x0102`)
- [ ] `EC_CMD_USB_PD_POWER_INFO` (`0x0103`)
- [ ] `EC_CMD_CHARGE_PORT_COUNT` (`0x0105`)
- [ ] `EC_CMD_USB_PD_DPS_CONTROL` (`0x0106`)
- [ ] `EC_CMD_USB_PD_FW_UPDATE` (`0x0110`)
- [ ] `EC_CMD_USB_PD_RW_HASH_ENTRY` (`0x0111`)
- [ ] `EC_CMD_USB_PD_DEV_INFO` (`0x0112`)
- [ ] `EC_CMD_USB_PD_DISCOVERY` (`0x0113`)
- [ ] `EC_CMD_PD_CHARGE_PORT_OVERRIDE` (`0x0114`)
- [ ] `EC_CMD_PD_GET_LOG_ENTRY` (`0x0115`)
- [ ] `EC_CMD_USB_PD_GET_AMODE` (`0x0116`)
- [ ] `EC_CMD_USB_PD_SET_AMODE` (`0x0117`)
- [ ] `EC_CMD_PD_WRITE_LOG_ENTRY` (`0x0118`)
- [ ] `EC_CMD_PD_CONTROL` (`0x0119`)
- [ ] `EC_CMD_USB_PD_MUX_INFO` (`0x011A`)
- [ ] `EC_CMD_PD_CHIP_INFO` (`0x011B`)

**Board commands (`board`)**

- [ ] `EC_CMD_RWSIG_CHECK_STATUS` (`0x011C`)
- [ ] `EC_CMD_RWSIG_ACTION` (`0x011D`)
- [ ] `EC_CMD_EFS_VERIFY` (`0x011E`)
- [ ] `EC_CMD_GET_CROS_BOARD_INFO` (`0x011F`)
- [ ] `EC_CMD_SET_CROS_BOARD_INFO` (`0x0120`)
- [ ] `EC_CMD_GET_UPTIME_INFO` (`0x0121`)
- [ ] `EC_CMD_ADD_ENTROPY` (`0x0122`)
- [ ] `EC_CMD_ADC_READ` (`0x0123`)
- [ ] `EC_CMD_ROLLBACK_INFO` (`0x0124`)
- [ ] `EC_CMD_AP_RESET` (`0x0125`)
- [ ] `EC_CMD_LOCATE_CHIP` (`0x0126`)
- [ ] `EC_CMD_REBOOT_AP_ON_G3` (`0x0127`)
- [ ] `EC_CMD_GET_PD_PORT_CAPS` (`0x0128`)
- [ ] `EC_CMD_BUTTON` (`0x0129`)
- [ ] `EC_CMD_GET_KEYBD_CONFIG` (`0x012A`)

**Smart discharge (`charge`)**

- [ ] `EC_CMD_SMART_DISCHARGE` (`0x012B`)

**Regulator commands (`power`)**

- [ ] `EC_CMD_REGULATOR_GET_INFO` (`0x012C`)
- [ ] `EC_CMD_REGULATOR_ENABLE` (`0x012D`)
- [ ] `EC_CMD_REGULATOR_IS_ENABLED` (`0x012E`)
- [ ] `EC_CMD_REGULATOR_SET_VOLTAGE` (`0x012F`)
- [ ] `EC_CMD_REGULATOR_GET_VOLTAGE` (`0x0130`)

**Type-C commands (`usb`)**

- [ ] `EC_CMD_TYPEC_DISCOVERY` (`0x0131`)
- [ ] `EC_CMD_TYPEC_CONTROL` (`0x0132`)
- [ ] `EC_CMD_TYPEC_STATUS` (`0x0133`)
- [ ] `EC_CMD_PCHG_COUNT` (`0x0134`)
- [ ] `EC_CMD_PCHG` (`0x0135`)
- [ ] `EC_CMD_PCHG_UPDATE` (`0x0136`)

**Charging related? (`charge`)**

- [ ] `EC_CMD_DISPLAY_SOC` (`0x0137`)
- [ ] `EC_CMD_SET_BASE_STATE` (`0x0138`)

**Subcommands for I2C control (`i2c`)**

- [ ] `EC_CMD_I2C_CONTROL` (`0x0139`)

**RGB keyboard commands (`rgb_keyboard`)**

- [ ] `EC_CMD_RGBKBD_SET_COLOR` (`0x013A`)
- [ ] `EC_CMD_RGBKBD` (`0x013B`)

**Type C VDM response (`usb`)**

- [ ] `EC_CMD_TYPEC_VDM_RESPONSE` (`0x013C`)

**Fingerprint MCU commands (`fingerprint`)**

- [ ] `EC_CMD_FP_PASSTHRU` (`0x0400`)
- [ ] `EC_CMD_FP_MODE` (`0x0402`)
- [ ] `EC_CMD_FP_INFO` (`0x0403`)
- [ ] `EC_CMD_FP_FRAME` (`0x0404`)
- [ ] `EC_CMD_FP_TEMPLATE` (`0x0405`)
- [ ] `EC_CMD_FP_CONTEXT` (`0x0406`)
- [ ] `EC_CMD_FP_STATS` (`0x0407`)
- [ ] `EC_CMD_FP_SEED` (`0x0408`)
- [ ] `EC_CMD_FP_ENC_STATUS` (`0x0409`)
- [ ] `EC_CMD_FP_READ_MATCH_SECRET` (`0x040A`)
- [ ] `EC_CMD_FP_ESTABLISH_PAIRING_KEY_KEYGEN` (`0x0410`)
- [ ] `EC_CMD_FP_ESTABLISH_PAIRING_KEY_WRAP` (`0x0411`)

**Touchpad MCU commands (`touchpad`)**

- [ ] `EC_CMD_TP_SELF_TEST` (`0x0500`)
- [ ] `EC_CMD_TP_FRAME_INFO` (`0x0501`)
- [ ] `EC_CMD_TP_FRAME_SNAPSHOT` (`0x0502`)
- [ ] `EC_CMD_TP_FRAME_GET` (`0x0503`)

</details>

<details>

<summary>Implemented Manufacturer commands</summary>

**Framework Specific Commands (`framework_laptop`)**

- [ ] `EC_CMD_FLASH_NOTIFIED` (`0x3E01`)
- [ ] `EC_CMD_FACTORY_MODE` (`0x3E02`)
- [x] `EC_CMD_CHARGE_LIMIT_CONTROL` (`0x3E03`)
- [x] `EC_CMD_PWM_GET_FAN_ACTUAL_RPM` (`0x3E04`)
- [ ] `EC_CMD_SET_AP_REBOOT_DELAY` (`0x3E05`)
- [ ] `EC_CMD_ME_CONTROL` (`0x3E06`)
- [ ] `EC_CMD_NON_ACPI_NOTIFY` (`0x3E07`)
- [ ] `EC_CMD_DISABLE_PS2_EMULATION` (`0x3E08`)
- [x] `EC_CMD_CHASSIS_INTRUSION` (`0x3E09`)
- [ ] `EC_CMD_BB_RETIMER_CONTROL` (`0x3E0A`)
- [ ] `EC_CMD_DIAGNOSIS` (`0x3E0B`)
- [ ] `EC_CMD_UPDATE_KEYBOARD_MATRIX` (`0x3E0C`)
- [ ] `EC_CMD_VPRO_CONTROL` (`0x3E0D`)
- [x] `EC_CMD_FP_LED_LEVEL_CONTROL` (`0x3E0E`)
- [x] `EC_CMD_CHASSIS_OPEN_CHECK` (`0x3E0F`)
- [ ] `EC_CMD_ACPI_NOTIFY` (`0x3E10`)
- [ ] `EC_CMD_READ_PD_VERSION` (`0x3E11`)
- [ ] `EC_CMD_THERMAL_QEVENT` (`0x3E12`)
- [ ] `EC_CMD_STANDALONE_MODE` (`0x3E13`)
- [x] `EC_CMD_PRIVACY_SWITCHES_CHECK_MODE` (`0x3E14`)
- [x] `EC_CMD_CHASSIS_COUNTER` (`0x3E15`)
- [ ] `EC_CMD_CHECK_DECK_STATE` (`0x3E16`)
- [x] `EC_CMD_GET_SIMPLE_VERSION` (`0x3E17`)
- [x] `EC_CMD_GET_ACTIVE_CHARGE_PD_CHIP` (`0x3E18`)
- [ ] `EC_CMD_UEFI_APP_MODE` (`0x3E19`)
- [ ] `EC_CMD_UEFI_APP_BTN_STATUS` (`0x3E1A`)
- [ ] `EC_CMD_EXPANSION_BAY_STATUS` (`0x3E1B`)
- [ ] `EC_CMD_GET_HW_DIAG` (`0x3E1C`)
- [?] `EC_CMD_GET_GPU_SERIAL` (`0x3E1D`)
- [?] `EC_CMD_GET_GPU_PCIE` (`0x3E1E`)
- [ ] `EC_CMD_PROGRAM_GPU_EEPROM` (`0x3E1F`)
- [?] `EC_CMD_FP_CONTROL` (`0x3E20`)
- [ ] `EC_CMD_GET_CUTOFF_STATUS` (`0x3E21`)
- [x] `EC_CMD_BATTERY_EXTENDER` (`0x3E24`)

</details>
