import unittest
from cros_ec_python import get_cros_ec, framework_laptop as ec_fw

ec = get_cros_ec()

# Some tests are commented out because I don't want to reconfigure the EC
# on my laptop every time I run the tests.

# class TestDisableChargeLimit(unittest.TestCase):
#     def test(self):
#         resp = ec_fw.disable_charge_limit(ec)
#         print(type(self).__name__, "-", "Resp:", resp)
#         self.assertIsNone(resp)


class TestGetChargeLimit(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_charge_limit(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, tuple)


# class TestSetChargeLimit(unittest.TestCase):
#     def test(self):
#         resp = ec_fw.set_charge_limit(ec, 98, 2)
#         print(type(self).__name__, "-", "Resp:", resp)
#         self.assertIsNone(resp)

# class TestOverrideChargeLimit(unittest.TestCase):
#     def test(self):
#         resp = ec_fw.override_charge_limit(ec)
#         print(type(self).__name__, "-", "Resp:", resp)
#         self.assertIsNone(resp)


class TestPwmGetFanRpm(unittest.TestCase):
    def test(self):
        resp = ec_fw.pwm_get_fan_rpm(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)


class TestGetChassisIntrusion(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_chassis_intrusion(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)


# class TestSetFpLedLevel(unittest.TestCase):
#     def test0(self):
#         resp = ec_fw.set_fp_led_level(ec, 0)
#         print(type(self).__name__, "-", "Resp:", resp)
#         self.assertIsNone(resp)

#     def test1(self):
#         resp = ec_fw.set_fp_led_level(ec, 1)
#         print(type(self).__name__, "-", "Resp:", resp)
#         self.assertIsNone(resp)

#     def test2(self):
#         resp = ec_fw.set_fp_led_level(ec, 2)
#         print(type(self).__name__, "-", "Resp:", resp)
#         self.assertIsNone(resp)


class TestGetFpLedLevel(unittest.TestCase):
    def test_int(self):
        resp = ec_fw.get_fp_led_level_int(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)

    def test_enum(self):
        resp = ec_fw.get_fp_led_level(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, ec_fw.FpLedBrightnessLevel)


class TestGetChassisOpenCheck(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_chassis_open_check(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, bool)


class TestGetPrivacySwitches(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_privacy_switches(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)


class TestGetChassisCounter(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_chassis_counter(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)


class TestGetSimpleVersion(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_simple_version(ec)
        print(type(self).__name__, "-", "Resp:", f"'{resp}'")
        self.assertIsInstance(resp, str)


class TestGetActiveChargePdChip(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_active_charge_pd_chip(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)


class TestGetBatteryExtender(unittest.TestCase):
    def test(self):
        resp = ec_fw.get_battery_extender(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)


class TestSetBatteryExtender(unittest.TestCase):
    def test(self):
        resp = ec_fw.set_battery_extender(ec, 0, 0, 0)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsNone(resp)


if __name__ == "__main__":
    unittest.main()
