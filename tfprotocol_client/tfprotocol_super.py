# coded by lagcleaner
# email: lagcleaner@gmail.com

from abc import ABC
from typing import Callable, Optional, Tuple, Union

from tfprotocol_client.connection.keep_alive_thread import KeepAliveThread
from tfprotocol_client.connection.protocol_client import ProtocolClient
from tfprotocol_client.misc.constants import (
    DFLT_MAX_BUFFER_SIZE,
    EMPTY_HANDLER,
    KEY_LEN_INTERVAL,
)
from tfprotocol_client.misc.handlers_aliases import ResponseHandler
from tfprotocol_client.models.exceptions import ErrorCode, TfException
from tfprotocol_client.models.keepalive_options import KeepAliveOptions
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.models.tcptimeout_options import TCPTimeoutOptions
from tfprotocol_client.security.cryptography import CryptographyUtils


class TfProtocolSuper(ABC):
    """The top tfprotocol class, all other classes of tfprotocol extends
    from this one, callbacks extends from ISuperCallback, all classes
    which extends from this one must have in order to be used another
    class who extends from ISuperCallback, if doesn't then the user won't
    be able to instantiate the extended subclass.
    """

    def __init__(
        self,
        protocol_version: str,
        public_key: str,
        client_hash: Union[str, bytes],
        address: str,
        port: int,
        proxy: ProxyOptions = None,
        keylen: int = KEY_LEN_INTERVAL[0],
        channel_len: int = DFLT_MAX_BUFFER_SIZE,
        verbosity_mode: bool = False,
    ) -> None:
        """Constructor for Transfer Protocol super class.

        Args:
            `protocol_version` (str): The desired version of the protocol.
            `public_key` (str): The previous shared rsa public key for
                the initial encryptation of the communication.
            `client_hash` (Union[str, bytes]): The hash to be used by
                the server in order to test the integrity of the communication.
            `address` (str): The ip/address where the protocol server is running.
            `port` (int): The TCP port where the protocol is listening.
            `proxy` (ProxyOptions, optional): The proxy address for
                connect through a proxy, proxy auth. Defaults to None.
            `keylen` (int, optional): The desired length for the session key
                used to encrypt communication whit the server. Defaults to KEY_LEN_INTERVAL[0].
            `channel_len` (int, optional): The length of the channel.
                Defaults to DFLT_MAX_BUFFER_SIZE.
            `verbosity_mode` (bool): Debug mode enabled for verbosity.
        """
        assert isinstance(port, int), f'Port argument must be an integer: {port} given'
        assert isinstance(
            protocol_version, str
        ), f'Protocol Version argument must be an float as string: {protocol_version} given'
        self.verbosity_mode = verbosity_mode
        self._protocol_version = protocol_version
        self._public_key = public_key
        self._client_hash = client_hash
        self._proto_client: ProtocolClient = None
        self.__proto_client_args = {
            'address': address,
            'port': port,
            'proxy_options': proxy,
            'max_buffer_size': channel_len,
            'verbosity_mode': verbosity_mode,
        }
        self._sleep_time_milisec = 3000
        self._len_channel = channel_len if channel_len is not None else 512 * 1024
        self._keybyteslen = (
            keylen
            if KEY_LEN_INTERVAL[0] <= keylen <= KEY_LEN_INTERVAL[1]
            else KEY_LEN_INTERVAL[0]
        )
        self._address: Tuple[str, int] = address
        #
        self.__call_kwargs = None
        self._tcp_timeout_options: Optional[TCPTimeoutOptions] = None

    def connect(
        self,
        keepalive_options: Optional[KeepAliveOptions] = None,
        on_response: ResponseHandler = EMPTY_HANDLER,
        on_connect: Callable[['TfProtocolSuper'], None] = EMPTY_HANDLER,
    ):
        """Connect to the server with keep-alive mechanism enabled or disabled

        Args:
            `keepalive_options` (KeepAliveOptions): Keep alive options.
            `on_response` (ResponseHandler): The callback for the server responses in the
                connection process.
            `on_connect` ((TfProtocolSuper) -> None): The callback to retrieve the connected
                instance of tfprotocol after stablishing connection.
        """
        # TRY TO INITIATE CONNECTION
        final_status: StatusInfo = self._connect()
        if final_status.status is StatusServerCode.OK:
            if keepalive_options:
                # START KEEP ALIVE MECHANISM
                udp_keep_alive = KeepAliveThread(self.client, keepalive_options)
                udp_keep_alive.setDaemon(True)
                udp_keep_alive.start()
            on_connect(self)
            return True
        else:
            on_response(final_status)
            try:
                self._proto_client.stop_connection()
                raise TfException(
                    status_server_code=StatusServerCode.DISCONNECTED,
                    code=ErrorCode.ON_WRITE_OR_RECEIVE_TO_SOCKET,
                    message=f'Cannot successfully connect to the server {final_status}',
                )
            except IOError as ex:
                raise TfException(exception=ex)

    def _connect(
        self,
        on_response: ResponseHandler = EMPTY_HANDLER,
    ) -> StatusInfo:
        self._proto_client = ProtocolClient(**self.__proto_client_args)
        self._tcp_timeout_options = TCPTimeoutOptions(
            status_server_callback=on_response,
        )
        count = 0
        status: StatusInfo = None
        while count < self.tcp_timeout_options.connect_retry:
            count += 1
            # TRY TO STABLISH TCP CONNECTION
            status: StatusInfo = self._proto_client.start_connection(
                self.tcp_timeout_options.dns_resolution_timeout,
                self.tcp_timeout_options.connect_timeout,
            )
            if status.status == StatusServerCode.OK:
                break
        if status.status is not StatusServerCode.OK:
            # FAIL TO STABLISH CONNECTION
            return status

        # SEND PROTOCOL TO BE USED
        status: StatusInfo = self._proto_client.translate(self._protocol_version)
        if status.status is not StatusServerCode.OK:
            # INCOMPATIBLE PROTOCOLS
            return status

        # GENERATE AND SEND THE SESSION KEY
        session_key = CryptographyUtils.get_random_bytes(self._keybyteslen)
        enc_session_key = CryptographyUtils.rsa_encrypt(session_key, self._public_key)
        status: StatusInfo = self._proto_client.translate(enc_session_key)
        if status.status is not StatusServerCode.OK:
            return status

        # SAVE SESSION KEY
        self._proto_client.session_key = session_key

        # SEND CLIENT HASH
        status: StatusInfo = self._proto_client.translate(self._client_hash)
        if status.status is not StatusServerCode.OK:
            return status
        return StatusInfo(StatusServerCode.OK)

    def disconnect(self):
        """Disconect the protocol client from the server."""
        self.client.stop_connection()

    def get_len_channel(self) -> int:
        """Gets the len of the channel

        Returns:
            int: `len_channel`
        """
        return self._len_channel

    def set_len_channel(self, value: int):
        self._len_channel = value

    len_channel = property(fget=get_len_channel, fset=set_len_channel)

    @property
    def tcp_timeout_options(self) -> TCPTimeoutOptions:
        """Gets options for connection attempts.

        Returns:
            TCPTimeoutOptions: `tcp_timeout_options`
        """
        return self._tcp_timeout_options

    @tcp_timeout_options.setter
    def set_tcp_timeout_options(self, value: TCPTimeoutOptions):
        self._tcp_timeout_options = value

    @property
    def client(self) -> ProtocolClient:
        return self._proto_client

    # sintax - with tfopen()
    def __call__(self, **kwargs):
        """Connect to the server with keep-alive mechanism enabled or disabled

        Args:
            `keepalive_options` (KeepAliveOptions): Keep alive options.
            `on_response` (ResponseHandler): The callback for the server responses in the
                connection process.
            `on_connect` ((TfProtocolSuper) -> None): The callback to retrieve the connected
                instance of tfprotocol after stablishing connection.
        """
        self.__call_kwargs = kwargs
        return self

    def __enter__(self):
        if self.__call_kwargs is not None:
            keepAlOpt: KeepAliveOptions = self.__call_kwargs.get('keepalive_options')
            on_resp: ResponseHandler = self.__call_kwargs.get('on_response')
            on_conct: Callable[['TfProtocolSuper'], None] = self.__call_kwargs.get(
                'on_connect'
            )
        self.connect(
            keepalive_options=keepAlOpt,
            on_response=on_resp if on_resp is not None else EMPTY_HANDLER,
            on_connect=on_conct if on_conct is not None else EMPTY_HANDLER,
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()
