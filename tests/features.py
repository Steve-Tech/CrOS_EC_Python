import unittest
from cros_ec_python import get_cros_ec, features as ec_features

ec = get_cros_ec()


class TestGetFeatures(unittest.TestCase):
    def test_version0(self):
        resp = ec_features.get_features(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)

    def test_decode(self):
        resp = ec_features.get_features(ec)
        decode = ec_features.decode_features(resp)
        print(type(self).__name__, "-", "Decode:", decode)
        self.assertIsInstance(decode, list)


if __name__ == '__main__':
    unittest.main()
