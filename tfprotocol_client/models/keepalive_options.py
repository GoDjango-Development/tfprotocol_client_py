# coded by lagcleaner
# email: lagcleaner@gmail.com

from enum import Enum


class KeepAliveMechanismType(Enum):
    """Keep alive mechanism types
    """

    UDP_HOSTCHECK = 0
    UDP_PROCHECK = 1
    TCP_NATIVE = 2


class KeepAliveOptions:
    """Keep Alive model to contain the options in case of keep alive.
    """

    def __init__(
        self,
        keepalive_mechanism: KeepAliveMechanismType,
        idle: int,
        timeout: int,
        max_tries: int,
    ) -> None:
        super().__init__()
        self.keepalive_mechanism: KeepAliveMechanismType = keepalive_mechanism
        self.idle: int = idle
        self.timeout: int = timeout
        self.max_tries: int = max_tries
