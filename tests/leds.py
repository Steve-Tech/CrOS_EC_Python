import unittest
from cros_ec_python import get_cros_ec, leds as ec_leds

ec = get_cros_ec()


class TestLedControl(unittest.TestCase):
    def test1_led_control_get_max_values(self):
        resp = ec_leds.led_control_get_max_values(ec, ec_leds.EcLedId.EC_LED_ID_BATTERY_LED)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)

    def test2_led_control(self):
        resp = ec_leds.led_control(ec, ec_leds.EcLedId.EC_LED_ID_BATTERY_LED, 0, [1, 0, 0, 0, 0, 0])
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)
        self.assertEqual(input("Is the battery indicator red? [y/N]: "), "y")

    def test3_led_control_set_color(self):
        resp = ec_leds.led_control_set_color(ec, ec_leds.EcLedId.EC_LED_ID_BATTERY_LED, 1,
                                             ec_leds.EcLedColors.EC_LED_COLOR_GREEN)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)
        self.assertEqual(input("Is the battery indicator green? [y/N]: "), "y")

    def test4_led_control_set_auto(self):
        resp = ec_leds.led_control_set_auto(ec, ec_leds.EcLedId.EC_LED_ID_BATTERY_LED)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)
        self.assertEqual(input("Is the battery indicator normal? [y/N]: "), "y")


if __name__ == '__main__':
    unittest.main()
