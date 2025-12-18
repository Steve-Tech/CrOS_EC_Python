import unittest
from cros_ec_python import get_cros_ec, thermal as ec_thermal

ec = get_cros_ec()

# Some tests are commented out because I don't want to reconfigure the EC
# on my laptop every time I run the tests.


class TestGetThresholds(unittest.TestCase):
    def test(self):
        resp = ec_thermal.thermal_get_thresholds(ec, 0)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)


# class TestSetThresholds(unittest.TestCase):
#     def test(self):
#         new_config = {
#             "temp_host": [70, 80, 120],
#             "temp_host_release": [50, 55, 115],
#             "temp_fan_off": 40,
#             "temp_fan_max": 70,
#         }
#         ec_thermal.thermal_set_thresholds(ec, 0, new_config)
#         resp = ec_thermal.thermal_get_thresholds(ec, 0)
#         print(type(self).__name__, "-", "Resp after set:", resp)
#         self.assertEqual(resp["temp_host"], new_config["temp_host"])
#         self.assertEqual(resp["temp_host_release"], new_config["temp_host_release"])
#         self.assertEqual(resp["temp_fan_off"], new_config["temp_fan_off"])
#         self.assertEqual(resp["temp_fan_max"], new_config["temp_fan_max"])


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
