from io import BytesIO
import sys
import time
import socket
import socks
from threading import Thread
from typing import Optional
from tfprotocol_client.connection.protocol_client import ProtocolClient
from tfprotocol_client.misc.build_utils import MessageUtils
from tfprotocol_client.misc.constants import BYTE_SIZE
from tfprotocol_client.models.exceptions import TfException

from tfprotocol_client.models.keepalive_options import (
    KeepAliveMechanismType,
    KeepAliveOptions,
)
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.tfprotocol_keepalive import TfProtocolKeepAliveWrapper


class KeepAliveHandler:
    '''The callback system where server connection close is notified.'''

    def connection_closed(self):
        pass


class KeepAliveThread(Thread):
    """Keep Alive mechanism threaded."""

    def __init__(
        self,
        proto_client: ProtocolClient,
        options: KeepAliveOptions,
        proxy_options: ProxyOptions = None,
        ka_handler: KeepAliveHandler = None,
    ) -> None:
        super().__init__(name='keepalive_t')
        self.is_active=False
        self._keepalive_mechanism: KeepAliveMechanismType = options.keepalive_mechanism
        self._proxy_options: ProxyOptions = proxy_options
        self._proto_client: ProtocolClient = proto_client
        self._idle: int = options.idle
        self._timeout: int = options.timeout
        self._max_tries: int = options.max_tries
        self._counter: int = 0
        self._prockey: str = ''

        try:
            self._datagram_socket: Optional[socks.socksocket] = socks.socksocket(
                socket.AF_INET, socket.SOCK_DGRAM
            )
            if proxy_options is not None:
                self._datagram_socket.set_proxy(
                    proxy_options.proxy_type,
                    proxy_options.address,
                    proxy_options.port,
                    username=proxy_options.username,
                    password=proxy_options.password,
                )
            self._handler: KeepAliveHandler = ka_handler if ka_handler else KeepAliveHandler()
            #
            # TODO: TEST DATAGRAM SOCKET (BIND FIRST)
            self._datagram_socket.connect(dest_pair=self.addrs)
            self._datagram_socket.settimeout(options.timeout)
            success = False
            if options.keepalive_mechanism is KeepAliveMechanismType.UDP_PROCHECK:
                self._proto_client.socket.settimeout(options.timeout)
                proto_wrapper = TfProtocolKeepAliveWrapper(self._proto_client)
                for _ in range(options.max_tries):
                    self._prockey = proto_wrapper.prockey_command()
                    self.is_active = proto_wrapper.keepalive_command(
                        True, 1, options.idle, options.max_tries
                    )
                    if not self._prockey or not self.is_active:
                        continue
                    self._proto_client.socket.settimeout(0)
                    success = True
                    break
                if not success:
                    self.stop_connection()
        except IOError as e:
            raise TfException(exception=e)

    @property
    def client(self):
        return self._proto_client

    @property
    def udp_sock(self):
        return self._datagram_socket

    @property
    def addrs(self):
        return self._proto_client.address, self._proto_client.port

    def stop_connection(self):
        self._datagram_socket.close()
        self.client.stop_connection()
        self.is_active = False
        if self._handler:
            self._handler.connection_closed()
        return self.client.socket.isClosed()

    def _stop(self):
        self.stop_connection()
        super()._stop()

    def udp_hostcheck(self):
        try:
            data_to_send = bytes((0,))
            _ = self.udp_sock.sendto(data_to_send, self.addrs)
            data_recvd, _ = self.udp_sock.recvfrom(1)
            if data_recvd[0] == 1:
                self._counter = 0
        except IOError:
            pass
        finally:
            self._counter += 1
            if self._counter == self._max_tries:
                self.stop_connection()
            else:
                try:
                    time.sleep(self._idle)
                except InterruptedError:
                    pass

    def udp_procheck(self):
        try:
            payload = BytesIO()
            payload.write(MessageUtils.encode_value(1, size=BYTE_SIZE))
            payload.write(MessageUtils.encode_value(self._prockey))
            _ = self.udp_sock.sendto(payload.getvalue(), self.addrs)

            data_recvd, _ = self.udp_sock.recvfrom(1)
            if data_recvd[0] == 0:
                self.stop_connection()
                return
            if data_recvd[0] == 1:
                self._counter = 0
        except IOError:
            pass
        finally:
            self._counter += 1
            if self._counter == self._max_tries:
                self.stop_connection()
            else:
                try:
                    time.sleep(self._idle)
                except InterruptedError:
                    pass

    def run(self) -> None:
        # return super().run()
        while self.is_active and self.client.is_connect():
            if self._keepalive_mechanism is KeepAliveMechanismType.UDP_HOSTCHECK:
                self.udp_hostcheck()
            elif self._keepalive_mechanism is KeepAliveMechanismType.UDP_PROCHECK:
                self.udp_procheck()
            else:
                sys.stderr.write(
                    f'Unhandled exception: {self._keepalive_mechanism} implementation not found.'
                )
