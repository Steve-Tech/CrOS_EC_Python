"""
This file includes the exceptions raised from CrOS EC devices.

See `cros_ec_python.constants.COMMON.EcStatus` for possible error codes.
"""

from .constants.COMMON import EcStatus


class ECError(IOError):
    """
    Exception raised for errors in the EC interface.

    See `cros_ec_python.constants.COMMON.EcStatus` for possible error codes.
    """

    def __init__(self, status: int, message: str | None = None):
        self.status: int = status
        """The error code returned by the EC."""

        self.ec_status: EcStatus = EcStatus(status)
        """The error code as an `cros_ec_python.constants.COMMON.EcStatus` enum."""

        self.status_str: str = self.ec_status.name
        """The error code as a string."""

        self.message:str = f"EC returned error code {self.status_str} ({self.status})" if message is None else message
        """A human-readable message describing the error."""

        super().__init__(self.message)
