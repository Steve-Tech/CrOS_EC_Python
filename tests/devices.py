import unittest
from cros_ec_python import CrosEcClass, CrosEcDev, CrosEcLpc, general
from cros_ec_python.constants import MEMMAP

ec: CrosEcClass | None = None


class TestLinuxDev(unittest.TestCase):
    def test1_init(self):
        global ec
        ec = CrosEcDev()
        self.assertIsNotNone(ec)

    def test2_memmap(self):
        resp = ec.memmap(MEMMAP.EC_MEMMAP_ID, 2)
        self.assertEqual(resp, b'EC')

    def test3_hello(self):
        data = b'\xa0\xb0\xc0\xd0'
        resp = ec.command(0, general.EC_CMD_HELLO, len(data), 4, data)
        self.assertEqual(resp, b'\xa4\xb3\xc2\xd1')


class TestLPC(unittest.TestCase):
    def test1_init(self):
        global ec
        ec = CrosEcLpc()
        self.assertIsNotNone(ec)

    def test2_memmap(self):
        resp = ec.memmap(MEMMAP.EC_MEMMAP_ID, 2)
        self.assertEqual(resp, b'EC')

    def test3_hello(self):
        data = b'\xa0\xb0\xc0\xd0'
        resp = ec.command(0, general.EC_CMD_HELLO, len(data), 4, data)
        self.assertEqual(resp, b'\xa4\xb3\xc2\xd1')


if __name__ == '__main__':
    unittest.main()
