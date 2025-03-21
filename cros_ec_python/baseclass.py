"""
This file includes the base class for CrOS EC devices.

It doesn't do anything on its own, but it is used as a base for all CrosEc classes to inherit from.

See `cros_ec_python.devices` for a few examples of a class that inherits from this class.
"""

import abc

from .constants.COMMON import *


class CrosEcClass(metaclass=abc.ABCMeta):
    """
    Base class for CrOS EC devices to inherit from.
    """

    @staticmethod
    @abc.abstractmethod
    def detect() -> bool:
        """
        Detect the EC type.
        """
        pass

    @abc.abstractmethod
    def ec_init(self) -> None:
        """
        Initialise the EC, this shouldn't need to be called unless the keyword arg init was set to false.
        """
        pass

    @abc.abstractmethod
    def ec_exit(self) -> None:
        """
        Close connection to the EC.
        """
        pass

    @abc.abstractmethod
    def command(
        self,
        version: Int32,
        command: Int32,
        outsize: Int32,
        insize: Int32,
        data: bytes = None,
        warn: bool = True,
    ) -> bytes:
        """
        Send a command to the EC and return the response.
        :param version: Command version number (often 0).
        :param command: Command to send (EC_CMD_...).
        :param outsize: Outgoing length in bytes.
        :param insize: Max number of bytes to accept from the EC.
        :param data: Outgoing data to EC.
        :param warn: Whether to warn if the response size is not as expected. Default is True.
        :return: Response from the EC.
        """
        pass

    @abc.abstractmethod
    def memmap(self, offset: Int32, num_bytes: Int32) -> bytes:
        """
        Read memory from the EC.
        :param offset: Offset to read from.
        :param num_bytes: Number of bytes to read.
        :return: Bytes read from the EC.
        """
        pass
