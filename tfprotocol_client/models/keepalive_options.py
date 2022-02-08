from enum import Enum


class KeepAliveMechanismType(Enum):
    UDP_HOSTCHECK = 0
    UDP_PROCHECK = 1


class KeepAliveOptions:
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
