import unittest
import sys
from cros_ec_python import get_cros_ec, ECError, general as ec_general

if sys.platform == "win32":
    from cros_ec_python.devices import win_fw_ec
else:
     win_fw_ec = None

ec = get_cros_ec()


class TestProtoVersion(unittest.TestCase):
    def test_version0(self):
        resp = ec_general.proto_version(ec)
        print(type(self).__name__, "-", "Resp:", resp)
        self.assertIsInstance(resp, int)


class TestHello(unittest.TestCase):
    def test_version0(self):
        in_data = 42
        resp = ec_general.hello(ec, in_data)
        print(type(self).__name__, "-", "Sent:", in_data, "Got:", resp - 0x01020304, "Raw:", resp)
        self.assertEqual(resp, in_data + 0x01020304)


class TestGetVersion(unittest.TestCase):
    def test_version0(self):
        resp = ec_general.get_version(ec, 0)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, dict)
        self.assertEqual(len(resp), 4)

    def test_version1(self):
        resp = ec_general.get_version(ec, 1)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, dict)
        self.assertEqual(len(resp), 5)


class TestBuildInfo(unittest.TestCase):
    def test_version0(self):
        resp = ec_general.get_build_info(ec)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, str)


class TestChipInfo(unittest.TestCase):
    def test_version0(self):
        resp = ec_general.get_chip_info(ec)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, dict)


class TestBoardVersion(unittest.TestCase):
    def test_version0(self):
        resp = ec_general.get_board_version(ec)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, int)


class TestCmdVersions(unittest.TestCase):
    def test_versionAny(self):
        resp = ec_general.get_cmd_versions(ec, ec_general.EC_CMD_GET_CMD_VERSIONS)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, int)

    def test_version0(self):
        resp = ec_general.get_cmd_versions(ec, ec_general.EC_CMD_GET_CMD_VERSIONS, 0)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, int)
        self.assertEqual(resp & 0x1, 0x1)

    def test_version1(self):
        resp = ec_general.get_cmd_versions(ec, ec_general.EC_CMD_GET_CMD_VERSIONS, 1)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, int)
        self.assertEqual(resp & 0x2, 0x2)

    def test_invalid(self):
        resp = ec_general.get_cmd_versions(ec, 0x7FFF)
        print(type(self).__name__, "-", resp)
        self.assertIsNone(resp)


class TestTestProtocol(unittest.TestCase):
    def test_version0(self):
        length = 32
        buf = bytes(range(length))
        resp = ec_general.test_protocol(ec, 0, length, buf)
        print(type(self).__name__, "-", resp)
        self.assertEqual(resp, buf)

    def test_error(self):
        with self.assertRaises(ECError):
            ec_general.test_protocol(ec, 1, 0, bytes())

    @unittest.skipIf(
        win_fw_ec is not None and isinstance(ec, win_fw_ec.WinFrameworkEc),
        "not supported on Framework's Driver",
    )
    def test_warning(self):
        with self.assertWarns(RuntimeWarning):
            length = 16
            buf = bytes(range(length))
            resp = ec_general.test_protocol(ec, 0, length, buf, length * 2)
            print(type(self).__name__, "-", resp)
            self.assertEqual(resp[:length], buf)


class TestProtocolInfo(unittest.TestCase):
    def test_version0(self):
        resp = ec_general.get_protocol_info(ec)
        print(type(self).__name__, "-", resp)
        self.assertIsInstance(resp, dict)


if __name__ == '__main__':
    unittest.main()
