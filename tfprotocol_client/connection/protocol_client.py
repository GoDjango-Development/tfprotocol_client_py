# coded by lagcleaner
# email: lagcleaner@gmail.com

from typing import Optional, Union
from multipledispatch import dispatch
from tfprotocol_client.connection.client import SocketClient
from tfprotocol_client.misc.constants import (
    DFLT_MAX_BUFFER_SIZE,
    ENDIANESS_NAME,
    INT_SIZE,
)
from tfprotocol_client.misc.build_utils import MessageUtils
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.security.cryptography import Xor


class ProtocolClient(SocketClient):
    """Protocol Client to handle, connections and make the interface
    easy to use.

    SocketClient: Super class
    """

    def __init__(
        self,
        address: str = 'localhost',
        port: int = 1234,
        proxy_options: Optional[ProxyOptions] = None,
        max_buffer_size=DFLT_MAX_BUFFER_SIZE,
        verbosity_mode: bool = False,
    ) -> None:
        super().__init__(
            address=address,
            port=port,
            proxy_options=proxy_options,
            max_buffer_size=max_buffer_size,
            verbosity_mode=verbosity_mode,
        )
        self.builder_utils: MessageUtils = MessageUtils(max_buffer_size=max_buffer_size)
        self.xor_input = None
        self.xor_output = None
        self._session_key = None

    def get_sessionkey(self):
        return self._session_key

    def set_sessionkey(self, session_key: bytes):
        if session_key is not None:
            self.xor_input = Xor(session_key)
            self.xor_output = Xor(session_key)
        self._session_key = session_key

    session_key = property(fget=get_sessionkey, fset=set_sessionkey)

    def _decrypt(self, payload: bytes) -> bytes:
        if self.xor_input is not None:
            payload = self.xor_input.decrypt(payload)
        return payload

    def _encrypt(self, payload: bytes) -> bytes:
        if self.xor_output is not None:
            payload = self.xor_output.encrypt(payload)
        return payload

    def just_recv_int(self, size: int = INT_SIZE, signed=False) -> int:
        # RECEIVE, DECRYPT AND DECODE INTEGER
        decrypted_data = self.just_recv(size)
        return MessageUtils.decode_int(decrypted_data, signed=signed)

    def just_recv_str(self, size: int) -> str:
        # RECEIVE, DECRYPT AND DECODE TEXT-STRING
        decrypted_data = self.just_recv(size)
        return MessageUtils.decode_str(decrypted_data)

    def just_recv(self, size: int = None) -> bytes:
        if not size:
            raise TfException(message="Bytes to receive not specified ...")
        # RECEIVE AND DECRYPT CHUNK
        received_header = self._recv(size)
        decrypted_header = self._decrypt(received_header)
        return decrypted_header

    @dispatch((int, str, bytes, bool))
    def just_send(self, message: int, size=INT_SIZE, signed=False, **_):
        self.exception_guard()

        # BUILD
        encoded_message = MessageUtils.encode_value(message, size=size, signed=signed)

        # ENCRYPT
        encrypted_message: bytes = self._encrypt(encoded_message)

        # SEND
        self._send(encrypted_message)

    # pylint: disable=function-redefined
    @dispatch(TfProtocolMessage)
    def just_send(self, message: TfProtocolMessage, **_):
        self.exception_guard()

        # BUILD
        _, encoded_message = message

        # ENCRYPT
        encrypted_message: bytes = self._encrypt(encoded_message)

        # SEND
        self._send(encrypted_message)

    @dispatch(TfProtocolMessage)
    def send(self, message: TfProtocolMessage, **_):
        self.exception_guard()
        # BUILD
        header, encoded_message = message
        if self.verbosity_mode:
            print(
                f'CLIENT: {int.from_bytes(header, byteorder=ENDIANESS_NAME)} {encoded_message}'
            )

        # ENCRYPT
        encrypted_header: bytes = self._encrypt(header)
        encrypted_message: bytes = self._encrypt(encoded_message)

        # SEND
        self._send(encrypted_header)
        self._send(encrypted_message)

    # pylint: disable=function-redefined
    @dispatch((str, bytes))
    def send(
        self,
        message: Union[str, bytes],
        custom_header: Union[str, bytes, int, bool, None] = None,
        header_size: int = None,
        **_,
    ):
        self.send(
            TfProtocolMessage(
                message,
                custom_header=custom_header,
                header_size=header_size,
            )
        )

    @dispatch()
    def recv(
        self,
        header_size=None,
        header_signed=True,
        parse_front_code_response=False,
    ) -> StatusInfo:
        self.exception_guard()
        header_size = header_size if header_size > 0 else self.header_size
        # RECEIVE, DECRYPT AND DECODE HEADER
        received_header = self._recv(header_size)
        decrypted_header = self._decrypt(received_header)
        decoded_header = MessageUtils.decode_int(decrypted_header, signed=header_signed)
        # print(f'SERVER: Header({decoded_header})')

        # RECEIVE AND DECRYPT BODY
        received_body = self._recv(decoded_header)
        decrypted_body = self._decrypt(received_body)
        status = StatusInfo.build_status(
            decoded_header,
            decrypted_body,
            parse_code=parse_front_code_response,
        )
        if self.verbosity_mode:
            print(f'SERVER: {decoded_header} {status}')
        return status

    @dispatch(TfProtocolMessage)
    def translate(
        self,
        message: TfProtocolMessage,
        recv_header_signed=True,
        parse_front_code_response=False,
        **_,
    ) -> StatusInfo:
        self.exception_guard()
        self.send(message)
        return self.recv(
            header_size=message.header_size,
            header_signed=recv_header_signed,
            parse_front_code_response=parse_front_code_response,
        )

    # pylint: disable=function-redefined
    @dispatch((str, bytes))
    def translate(
        self,
        message: Union[str, bytes],
        custom_header: Union[str, bytes, int, bool, None] = None,
        header_size: int = None,
        recv_header_signed=True,
        parse_front_code_response=False,
        **_,
    ) -> StatusInfo:
        return self.translate(
            TfProtocolMessage(
                message, custom_header=custom_header, header_size=header_size
            ),
            recv_header_signed=recv_header_signed,
            parse_front_code_response=parse_front_code_response,
        )
