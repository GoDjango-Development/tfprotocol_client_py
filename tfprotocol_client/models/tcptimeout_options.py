# coded by lagcleaner
# email: lagcleaner@gmail.com

from typing import Callable
from tfprotocol_client.models.status_server_code import StatusServerCode

from tfprotocol_client.models.status_info import StatusInfo


class TCPTimeoutOptions:
    """TCP timeout options. """

    def __init__(
        self,
        connect_timeout: int = 120 * 1000,
        connect_retry: int = 3,
        dns_resolution_timeout: int = 20 * 1000,
        status_server_callback: Callable[[StatusInfo], None] = None,
    ) -> None:
        self._connect_retry: int = connect_retry
        self._connect_timeout: int = connect_timeout
        self._dns_resolution_timeout: int = dns_resolution_timeout
        self.status_server_callback = (
            (lambda _: None)
            if status_server_callback is None
            else status_server_callback
        )

    @property
    def connect_timeout(self) -> int:
        return self._connect_timeout

    @connect_timeout.setter
    def set_connect_timeout(self, value: int):
        if value < 0:
            self.status_server_callback(
                StatusInfo(
                    status=StatusServerCode.FAILED,
                    opcode=-1,
                    message='connect_timeout has to be a non-negative number',
                )
            )
        else:
            self._connect_timeout = value

    @property
    def connect_retry(self) -> int:
        return self._connect_retry

    @connect_retry.setter
    def set_connect_retry(self, value: int):
        if value < 0:
            self.status_server_callback(
                StatusInfo(
                    status=StatusServerCode.FAILED,
                    opcode=-1,
                    message='connect_retry has to be a non-negative number',
                )
            )
        else:
            self._connect_retry = value

    @property
    def dns_resolution_timeout(self) -> int:
        return self._dns_resolution_timeout

    @dns_resolution_timeout.setter
    def set_dns_resolution_timeout(self, value: int):
        self._dns_resolution_timeout = value
