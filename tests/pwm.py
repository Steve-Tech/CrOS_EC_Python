import unittest
from cros_ec_python import get_cros_ec, pwm as ec_pwm, thermal as ec_thermal

ec = get_cros_ec()


class TestFanRpm(unittest.TestCase):
    def test_version0(self):
        rpm = 2500
        ec_pwm.pwm_set_fan_rpm(ec, rpm)
        print(type(self).__name__, "-", "Sent:", rpm, end=" ")
        resp = ec_pwm.pwm_get_fan_rpm(ec)
        print("Got:", resp)
        self.assertEqual(resp, rpm)

    def test_version1(self):
        rpm = 3000
        idx = 0
        ec_pwm.pwm_set_fan_rpm(ec, rpm, idx)
        print(type(self).__name__, "-", "Sent:", rpm, end=" ")
        resp = ec_pwm.pwm_get_fan_rpm(ec)
        print("Got:", resp)
        self.assertEqual(resp, rpm)

    @classmethod
    def tearDownClass(cls):
        ec_thermal.thermal_auto_fan_ctrl(ec, 0)
        print("Auto fan control enabled")


original_brightness = 0


class TestKeyboardBacklight(unittest.TestCase):
    def test_get_v0(self):
        global original_brightness
        resp = ec_pwm.pwm_get_keyboard_backlight(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)
        original_brightness = resp["percent"]

    def test_set50_v0(self):
        percent = 50
        ec_pwm.pwm_set_keyboard_backlight(ec, percent)
        print(type(self).__name__, "-", "Sent:", percent, end=" ")
        resp = ec_pwm.pwm_get_keyboard_backlight(ec)
        print("Got:", resp)
        self.assertIsInstance(resp, dict)
        self.assertEqual(resp["percent"], percent)

    def test_set_v0(self):
        ec_pwm.pwm_set_keyboard_backlight(ec, original_brightness)
        print(type(self).__name__, "-", "Sent:", original_brightness, end=" ")
        resp = ec_pwm.pwm_get_keyboard_backlight(ec)
        print("Got:", resp)
        self.assertEqual(resp["percent"], original_brightness)


class TestFanDuty(unittest.TestCase):

    def test_set100_v0(self):
        percent = 100
        idx = 0
        ec_pwm.pwm_set_fan_duty(ec, percent, idx)
        self.assertEqual(input("Is the fan running at 100%? [y/N]: ").lower(), "y")

    def test_set50_v0(self):
        percent = 50
        ec_pwm.pwm_set_fan_duty(ec, percent)
        self.assertEqual(input("Is the fan running at 50%? [y/N]: ").lower(), "y")

    @classmethod
    def tearDownClass(cls):
        ec_thermal.thermal_auto_fan_ctrl(ec, 0)
        print("Auto fan control enabled")


class TestPwm(unittest.TestCase):
    def test_get_kb_v0(self):
        global original_brightness
        resp = ec_pwm.pwm_get_duty(ec, ec_pwm.EcPwmType.EC_PWM_TYPE_KB_LIGHT)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)
        original_brightness = resp

    def test_set50_kb_v0(self):
        duty = ec_pwm.EC_PWM_MAX_DUTY // 2
        ec_pwm.pwm_set_duty(ec, duty, ec_pwm.EcPwmType.EC_PWM_TYPE_KB_LIGHT)
        print(type(self).__name__, "-", "Sent:", duty, end=" ")
        resp = ec_pwm.pwm_get_duty(ec, ec_pwm.EcPwmType.EC_PWM_TYPE_KB_LIGHT)
        print("Got:", resp)
        self.assertEqual(resp, duty)

    def test_set_kb_v0(self):
        ec_pwm.pwm_set_duty(ec, original_brightness, ec_pwm.EcPwmType.EC_PWM_TYPE_KB_LIGHT)
        print(type(self).__name__, "-", "Sent:", original_brightness, end=" ")
        resp = ec_pwm.pwm_get_duty(ec, ec_pwm.EcPwmType.EC_PWM_TYPE_KB_LIGHT)
        print("Got:", resp)
        self.assertEqual(resp, original_brightness)


if __name__ == '__main__':
    unittest.main()
