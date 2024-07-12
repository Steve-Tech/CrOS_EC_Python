import unittest
from cros_ec_python import get_cros_ec, thermal as ec_thermal

ec = get_cros_ec()


class TestAutoFanControl(unittest.TestCase):
    def test_version0(self):
        ec_thermal.thermal_auto_fan_ctrl(ec)

    def test_version1(self):
        ec_thermal.thermal_auto_fan_ctrl(ec, 0)


if __name__ == '__main__':
    unittest.main()
