# coded by lagcleaner
# email: lagcleaner@gmail.com

import socket
import sys
import time
from io import BytesIO
from platform import system as current_operating_system
from threading import Thread
from typing import Callable, Optional

import tfprotocol_client.connection.socks_prox as socks
from tfprotocol_client.connection.protocol_client import ProtocolClient
from tfprotocol_client.misc.build_utils import MessageUtils
from tfprotocol_client.misc.constants import BYTE_SIZE, EMPTY_HANDLER
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.keepalive_options import (
    KeepAliveMechanismType,
    KeepAliveOptions,
)
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.tfprotocol_keepalive import TfProtocolKeepAliveWrapper


class KeepAliveThread(Thread):
    """Keep Alive mechanism threaded."""

    def __init__(
        self,
        proto_client: ProtocolClient,
        options: KeepAliveOptions,
        proxy_options: ProxyOptions = None,
        on_connection_closed: Callable[[], None] = EMPTY_HANDLER,
    ) -> None:
        super().__init__(name='keepalive_t')
        self.is_active = False
        self._keepalive_mechanism: KeepAliveMechanismType = options.keepalive_mechanism
        self._proxy_options: ProxyOptions = proxy_options
        self._proto_client: ProtocolClient = proto_client
        self._idle: int = options.idle
        self._timeout: int = options.timeout
        self._max_tries: int = options.max_tries
        self._counter: int = 0
        self._prockey: str = ''
        self._on_connection_closed: Callable[[], None] = on_connection_closed

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
            self._datagram_socket.settimeout(options.timeout)
            success = False
            if options.keepalive_mechanism is KeepAliveMechanismType.TCP_NATIVE:
                if current_operating_system() == 'Windows':
                    set_keepalive_windows(
                        self._proto_client.socket,
                        self._idle,
                        self._timeout,
                        self._max_tries,
                    )
                elif current_operating_system() == 'Linux':
                    set_keepalive_linux(
                        self._proto_client.socket,
                        self._idle,
                        self._timeout,
                        self._max_tries,
                    )
                elif current_operating_system() == 'MacOS':
                    set_keepalive_linux(
                        self._proto_client.socket,
                        self._idle,
                        self._timeout,
                        self._max_tries,
                    )

            if options.keepalive_mechanism is KeepAliveMechanismType.UDP_PROCHECK:
                dflt_timout = self._proto_client.socket.gettimeout()
                self._proto_client.socket.settimeout(options.timeout)
                proto_wrapper = TfProtocolKeepAliveWrapper(self._proto_client)
                for _ in range(options.max_tries):
                    self._prockey = proto_wrapper.prockey_command()
                    self.is_active = proto_wrapper.keepalive_command(
                        True, 1, options.idle, options.max_tries
                    )
                    if not self._prockey or not self.is_active:
                        continue
                    self._proto_client.socket.settimeout(dflt_timout)
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
        if self._on_connection_closed:
            self._on_connection_closed()
        return self.client.is_connect()

    def _stop(self):
        self.stop_connection()
        super()._stop()

    def udp_hostcheck(self):
        print(f'KA: udp_hostcheck (tries: {self._counter})')
        try:
            data_to_send = bytes((0,))
            _ = self.udp_sock.sendto(data_to_send, self.addrs)
            data_recvd, _ = self.udp_sock.recvfrom(1)
            print(f'KA: udp_hostcheck (recv: {data_recvd})')
            if data_recvd[0] == 1:
                self._counter = 0
        except IOError as e:
            print('UDP_SOCKET-IOError: ', e.strerror, e.args)
        except Exception as e:  # pylint: disable=broad-except
            print('UDP_SOCKET-Error: ', e)
        finally:
            if self._counter == self._max_tries:
                self.stop_connection()
            else:
                try:
                    time.sleep(self._idle)
                except InterruptedError:
                    pass
            self._counter += 1

    def udp_procheck(self):
        print('KA: udp_procheck')
        try:
            payload = BytesIO()
            payload.write(MessageUtils.encode_value(1, size=BYTE_SIZE))
            payload.write(MessageUtils.encode_value(self._prockey))
            print('KA: udp_procheck - send', payload.getvalue())
            _ = self.udp_sock.sendto(payload.getvalue(), self.addrs)

            data_recvd, _ = self.udp_sock.recvfrom(1)
            print('KA: udp_procheck - recv', data_recvd)
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
        print('KA: run')
        self.is_active = True
        while self.is_active and self.client.is_connect():
            if self._keepalive_mechanism is KeepAliveMechanismType.UDP_HOSTCHECK:
                self.udp_hostcheck()
            elif self._keepalive_mechanism is KeepAliveMechanismType.UDP_PROCHECK:
                self.udp_procheck()
            elif self._keepalive_mechanism is KeepAliveMechanismType.TCP_NATIVE:
                break
            else:
                sys.stderr.write(
                    f'Unhandled exception: {self._keepalive_mechanism} implementation not found.'
                )
                sys.exit(1)


def set_keepalive_linux(sock, after_idle_sec=3600, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 3600 seconds (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


def set_keepalive_windows(sock, after_idle_sec=3600, interval_sec=3, _=None):
    """Set TCP keepalive on an open socket.

    It activates after 3600 seconds (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.ioctl(
        socket.SIO_KEEPALIVE_VALS,
        (1, after_idle_sec * 1000, interval_sec * 1000),
    )


def set_keepalive_mac(sock, after_idle_sec=3600, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 3600 seconds (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, max_fails)
