from io import BytesIO
from typing import Any
import socket
import socks
from tfprotocol_client.misc.constants import DFLT_HEADER_SIZE, DFLT_MAX_BUFFER_SIZE
from tfprotocol_client.misc.guard_exception import (
    on_except,
    raise_from,
)
from tfprotocol_client.misc.timeout_func import TimeLimitExpired, timelimit
from tfprotocol_client.models.exceptions import ErrorCode, TfException

from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo


class SocketClient:
    """Socket Client, handles proxy and basic send and receive. """

    def __init__(
        self,
        address: str = 'localhost',
        port: int = 1234,
        proxy_options: ProxyOptions = None,
        max_buffer_size: int = DFLT_MAX_BUFFER_SIZE,
        header_size: int = DFLT_HEADER_SIZE,
    ) -> None:
        self._socket: socks.socksocket = socks.socksocket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        if proxy_options is not None:
            self._socket.set_proxy(
                proxy_options.proxy_type,
                proxy_options.address,
                proxy_options.port,
                username=proxy_options.username,
                password=proxy_options.password,
            )
        self._proxy_options = proxy_options
        self.address: str = address
        self.port: int = port
        self.header_size: int = header_size
        self.max_buffer_size: int = max_buffer_size
        self._is_connect: bool = False

    def is_connect(self):
        return self._is_connect

    @property
    def socket(self) -> socket.socket:
        return self._socket

    @socket.setter
    def set_socket(self, new_socket: socks.socksocket):
        self._socket = new_socket

    @on_except(
        dflt_handler=lambda _: StatusInfo.parse("DISCONNECTED 0 connection time out"),
        **{
            AttributeError.__name__: lambda _: StatusInfo.parse(
                "DISCONNECTED 0 null pointer exception"
            ),
            TimeLimitExpired.__name__: lambda _: StatusInfo.parse(
                "DISCONNECTED 0 time out dns"
            ),
        },
    )
    def start_connection(self, dns_resolution_timeout: int, timeout: int) -> Any:
        """Method to initiate the connection with the server via socket.

        Args:
            `dns_resolution_timeout` (int): dns timeout expressed in seconds
            `timeout` (int): timeout to connect expresed in seconds

        Returns:
            StatusInfo: status information resulting from connection attempt
        """
        ip = timelimit(
            dns_resolution_timeout,
            (lambda self: socket.gethostbyname(self.address)),
            args=(self,),
        )
        self._socket.settimeout(timeout)
        self._socket.connect((ip, self.port))
        self._is_connect = True
        return StatusInfo.parse("OK")

    @on_except(dflt_handler=raise_from)
    def stop_connection(self):
        """Close socket connection to the server"""
        if self._socket is not None:
            try:
                self._socket.close()
            except Exception:  # pylint: disable=broad-except
                pass
        self._is_connect = False

    def _send(self, rawmessage: bytes) -> int:
        """Send a bunch of bytes through the socket to the server.

        Args:
            `rawmessage` (bytes): Ready to send message bytes.

        Raises:
            TfException: Socket write failed.

        Returns:
            int: how many bytes has been sended.
        """
        try:
            if rawmessage:
                return self.socket.send(rawmessage)
            return 0
        except Exception as e:
            raise TfException(
                message='Cannot succesfully write to socket',
                code=ErrorCode.ON_WRITE_OR_RECEIVE_TO_SOCKET,
                exception=e,
            )

    def _recv(self, size: int) -> bytes:
        """Receive a bunch of bytes from the socket connection

        Args:
            `size` (int): The size of the message to read.

        Raises:
            TfException: Memory limit reached.
            TfException: Socket sudently closed.

        Returns:
            bytes: message received.
        """
        binary_message = BytesIO()
        bytes_received = 0
        raw_chunk = bytearray(min(self.max_buffer_size, size - bytes_received))
        while bytes_received < size:
            try:
                # read chunk
                read = 0
                read = self.socket.recv_into(raw_chunk, len(raw_chunk))
                
                # save chunk
                bytes_received += read
                binary_message.write(raw_chunk[:read])
                
                print('-readed: ', read, 'left: ', size - bytes_received)
            except OSError as e:
                raise TfException(exception=e, message="Cannot read from socket ...")
            except MemoryError as excpt:
                # header_size is not going to reach this line
                # cause is an integer of up to 8 bytes only
                raise TfException(
                    exception=excpt,
                    code=ErrorCode.ON_WRITE_OR_RECEIVE_TO_SOCKET,
                    message=f'Heap space not enough server answer with a very \
                        high header number\nheader:{size}',
                )
        return binary_message.getvalue()

    def exception_guard(self):
        if self.socket is None or not self.is_connect():
            raise TfException(
                message="Socket is closed or not connected",
                code=ErrorCode.ON_WRITE_OR_RECEIVE_TO_SOCKET,
            )

    def __del__(self):
        self.stop_connection()
