from typing import Optional, Union
from multipledispatch import dispatch
from tfprotocol_client.connection.client import SocketClient
from tfprotocol_client.misc.constants import DFLT_MAX_BUFFER_SIZE, INT_SIZE
from tfprotocol_client.misc.build_utils import MessageUtils
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.security.cryptography import Xor

# DecryptFunc = Callable[[bytes], bytes]
# EncryptFunc = DecryptFunc


class ProtocolClient(SocketClient):
    """ Protocol Client to handle, connections and make the interface
    easy to use.

    SocketClient: Super class
    """

    def __init__(
        self,
        address: str = 'localhost',
        port: int = 1234,
        proxy_options: Optional[ProxyOptions] = None,
        max_buffer_size=DFLT_MAX_BUFFER_SIZE,
    ) -> None:
        super().__init__(
            address=address,
            port=port,
            proxy_options=proxy_options,
            max_buffer_size=max_buffer_size,
        )
        self.builder_utils: MessageUtils = MessageUtils(max_buffer_size=max_buffer_size)
        self.xor_input = None
        self.xor_output = None

    def set_sessionkey(self, session_key: bytes):
        self.xor_input = Xor(session_key)
        self.xor_output = Xor(session_key)

    def _decrypt(self, payload: bytes) -> bytes:
        if self.xor_input is not None:
            payload = self.xor_input.decrypt(payload)
        return payload

    def _encrypt(self, payload: bytes) -> bytes:
        if self.xor_output is not None:
            payload = self.xor_output.encrypt(payload)
        return payload

    def just_recv_int(self, size: int = INT_SIZE) -> int:
        # RECEIVE, DECRYPT AND DECODE INTEGER
        decrypted_data = self.just_recv(size)
        return MessageUtils.decode_int(decrypted_data)

    def just_recv_str(self, size: int) -> int:
        # RECEIVE, DECRYPT AND DECODE TEXT-STRING
        decrypted_data = self.just_recv(size)
        return MessageUtils.decode_str(decrypted_data)

    def just_recv(self, size: int = None) -> bytes:
        if size:
            raise TfException(message="Bytes to receive not specified ...")
        # RECEIVE AND DECRYPT CHUNK
        received_header = self._recv(size)
        decrypted_header = self._decrypt(received_header)
        return decrypted_header

    @dispatch(TfProtocolMessage)
    def send(self, message: TfProtocolMessage):
        self.exception_guard()
        # BUILD
        header, encoded_message = message

        # ENCRYPT
        encrypted_header: bytes = self._encrypt(header)
        encrypted_message: bytes = self._encrypt(encoded_message)

        # SEND
        self._send(encrypted_header)
        self._send(encrypted_message)

    @dispatch((str, bytes))
    def send(
        self,
        message: Union[str, bytes],
        custom_header: Union[str, bytes, int, bool, None] = None,
        header_size: int = None,
    ):
        self.send(
            TfProtocolMessage(
                message, custom_header=custom_header, header_size=header_size,
            )
        )

    @dispatch()
    def recv(self, header_size=None) -> StatusInfo:
        self.exception_guard()
        header_size = header_size if header_size > 0 else self.header_size
        # RECEIVE, DECRYPT AND DECODE HEADER
        received_header = self._recv(header_size)
        decrypted_header = self._decrypt(received_header)
        decoded_header = MessageUtils.decode_int(decrypted_header)

        # RECEIVE AND DECRYPT BODY
        received_body = self._recv(decoded_header)
        decrypted_body = self._decrypt(received_body)
        print(f'SERVER: {decoded_header} {decrypted_body}')
        status = StatusInfo.build_status(decoded_header, decrypted_body)
        return status

    @dispatch(TfProtocolMessage)
    def translate(self, message: TfProtocolMessage) -> StatusInfo:
        self.exception_guard()
        self.send(message)
        return self.recv(header_size=message.header_size)

    @dispatch((str, bytes))
    def translate(
        self,
        message: Union[str, bytes],
        custom_header: Union[str, bytes, int, bool, None] = None,
        header_size: int = None,
        **_,
    ) -> StatusInfo:
        return self.translate(
            TfProtocolMessage(
                message, custom_header=custom_header, header_size=header_size
            )
        )
