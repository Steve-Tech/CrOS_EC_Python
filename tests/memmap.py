import unittest
from cros_ec_python import CrOS_EC, memmap as ec_memmap

ec = CrOS_EC()


class TestGetTemps(unittest.TestCase):
    def test(self):
        resp = ec_memmap.get_temps(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)


class TestGetFans(unittest.TestCase):
    def test(self):
        resp = ec_memmap.get_fans(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)


class TestGetSwitches(unittest.TestCase):
    def test(self):
        resp = ec_memmap.get_switches(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)


class TestGetBattery(unittest.TestCase):
    def test(self):
        resp = ec_memmap.get_battery_values(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, dict)


class TestGetALS(unittest.TestCase):
    def test(self):
        resp = ec_memmap.get_als(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)


class TestGetAccel(unittest.TestCase):
    def test(self):
        resp = ec_memmap.get_accel(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, list)


if __name__ == '__main__':
    unittest.main()
