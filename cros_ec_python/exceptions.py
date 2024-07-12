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
        self.status = status
        self.status_str = EcStatus(status).name
        self.message = f"EC returned error code {self.status_str} ({self.status})" if message is None else message
        super().__init__(self.message)
