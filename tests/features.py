import unittest
from cros_ec_python import CrOS_EC
from cros_ec_python.commands.features import *

ec = CrOS_EC()


class TestGetFeatures(unittest.TestCase):
    def test_version0(self):
        resp = get_features(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)

    def test_decode(self):
        resp = get_features(ec)
        decode = decode_features(resp)
        print(type(self).__name__, "-", "Decode:", decode)
        self.assertIsInstance(decode, list)


if __name__ == '__main__':
    unittest.main()
