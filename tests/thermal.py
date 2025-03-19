import unittest
from cros_ec_python import get_cros_ec, thermal as ec_thermal

ec = get_cros_ec()


class TestAutoFanControl(unittest.TestCase):
    def test_version0(self):
        ec_thermal.thermal_auto_fan_ctrl(ec)

    def test_version1(self):
        ec_thermal.thermal_auto_fan_ctrl(ec, 0)

class TestTempSensorInfo(unittest.TestCase):
    def test(self):
        resp = ec_thermal.temp_sensor_get_info(ec, 0)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)

class TestTempSensors(unittest.TestCase):
    def test(self):
        resp = ec_thermal.get_temp_sensors(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)

if __name__ == '__main__':
    unittest.main()
