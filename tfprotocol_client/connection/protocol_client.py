from typing import Any, Optional, Union
from multipledispatch import dispatch
from tfprotocol_client.connection.client import SocketClient
from tfprotocol_client.misc.constants import DFLT_MAX_BUFFER_SIZE
from tfprotocol_client.misc.message_builder import MessageBuilder
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
        self.message_builder: MessageBuilder = MessageBuilder(
            max_buffer_size=max_buffer_size
        )
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

    @dispatch((str, bytes), custom_header=Any)
    def send(
        self,
        message: Union[str, bytes],
        custom_header: Union[str, bytes, int, bool, None] = None,
    ):
        self.exception_guard()
        # BUILD
        header, encoded_message = self.message_builder.build_send_message(
            message, custom_header=custom_header,
        )

        # ENCRYPT
        encrypted_header: bytes = self._encrypt(header)
        encrypted_message: bytes = self._encrypt(encoded_message)

        # SEND
        self._send(encrypted_header)
        self._send(encrypted_message)

    @dispatch()
    def recv(self) -> StatusInfo:
        self.exception_guard()
        # RECEIVE, DECRYPT AND DECODE HEADER
        received_header = self._recv(self.header_size)
        decrypted_header = self._decrypt(received_header)
        decoded_header = self.message_builder.build_recvd_header(decrypted_header)

        # RECEIVE AND DECRYPT BODY
        received_body = self._recv(decoded_header)
        decrypted_body = self._decrypt(received_body)

        status = self.message_builder.build_receive_status(
            decoded_header, decrypted_body
        )
        return status

    @dispatch(str)
    def translate(self, message: str) -> StatusInfo:
        self.exception_guard()
        self.send(message)
        return self.recv()

    @dispatch(TfProtocolMessage)
    def translate(self, message: TfProtocolMessage) -> StatusInfo:
        self.exception_guard()
        self.send(message.payload, custom_header=message.custom_header)
        return self.recv()

    @dispatch(bytes)
    def translate(self, message: bytes) -> StatusInfo:
        self.exception_guard()
        self.send(message)
        return self.recv()
