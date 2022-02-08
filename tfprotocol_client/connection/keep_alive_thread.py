from socket import socket
from threading import Thread
from typing import Any, Optional
from tfprotocol_client.connection.protocol_client import ProtocolClient

from tfprotocol_client.models.keepalive_options import (
    KeepAliveMechanismType,
    KeepAliveOptions,
)


class KeepAliveHandler:
    pass


class KeepAliveThread(Thread):
    def __init__(
        self,
        proto_client: Any,
        ka_handler: KeepAliveHandler,
        options: KeepAliveOptions,
    ) -> None:
        super().__init__()
        self._keepalive_mechanism: KeepAliveMechanismType = options.keepalive_mechanism
        self._proto_client: ProtocolClient = proto_client
        self._idle: int = options.idle
        self._timeout: int = options.timeout
        self._max_tries: int = options.max_tries
        self._counter: int = 0
        self._prockey: str = ''
        self._datagram_socket: Optional[socket] = None
        self._handler: KeepAliveHandler = ka_handler
        #
        self._proto_client.socket.settimeout(options.timeout)
