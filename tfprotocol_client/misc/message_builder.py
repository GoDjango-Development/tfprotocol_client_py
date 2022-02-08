import struct
from typing import Any, Final, Union
from multipledispatch import dispatch
from tfprotocol_client.misc.constants import ENDIANESS, STRING_ENCODING
from tfprotocol_client.misc.status_server_code import StatusServerCode
from tfprotocol_client.models.status_info import StatusInfo


class MessageBuilder:
    """Message builder for comunication with transfer protocol"""

    def __init__(self, max_buffer_size: int) -> None:
        self.max_buffer_size: Final[int] = max_buffer_size

    def build_send_message(
        self,
        *messages: Union[str, bytes, int, bool, None],
        custom_header: Union[str, bytes, int, bool, None] = None,
        trim_body: bool = True,
    ) -> tuple[bytes, bytes]:
        body = b''
        header = None
        if len(messages) > 0:
            body = bytearray()
            for i, m in enumerate(messages):
                body.extend(self._encode_value(m))
                if i != len(messages) - 1 or not trim_body:
                    body.append(b' ')
        if custom_header is not None:
            header = self._encode_value(custom_header)
        else:
            header = self._encode_value(len(body))
        return header, body

    def build_receive_status(
        self, header: int, message: bytes, parse_code: bool = False
    ) -> StatusInfo:
        msg_str: str = str(message, encoding='utf8')
        early_ocurrence: int = len(msg_str)
        status: StatusServerCode = StatusServerCode.UNKNOWN
        code: int = header
        for status_code in StatusServerCode:
            index = msg_str.find(status_code.name)
            if 0 <= index < early_ocurrence:
                status = status_code
                early_ocurrence = index
                if index == 0:
                    break
        msg_str = msg_str.replace(status.name, '', 1).strip().replace(' : ', '', 1)
        if (status != StatusServerCode.FAILED and len(msg_str) == 0) or not parse_code:
            code = status.value
        else:
            strparts = msg_str.split('')
            # TODO: UNKNOWN CODE CALCULATION FROM MESSAGE
        return StatusInfo(status, code=code, message=msg_str)

    def build_recvd_header(self, encoded_header: bytes):
        return int.from_bytes(encoded_header, byteorder='big')

    # def _decode_int(self, encoded_value: bytes) -> int:

    @dispatch(str)
    def _encode_value(self, value: str) -> bytes:
        encoded_str = value.encode(STRING_ENCODING)
        return struct.pack(f'{ENDIANESS}{len(encoded_str)}s', encoded_str)

    @dispatch(int)
    def _encode_value(self, value: int) -> bytes:
        if value.bit_length() < 32:  # 32 bit // 4 bytes
            return struct.pack(f'{ENDIANESS}i', value)
        else:  # 64 bit // 8 bytes
            return struct.pack(f'{ENDIANESS}q', value)

    @dispatch(bytes)
    def _encode_value(self, value: bytes) -> bytes:
        return struct.pack(f'{ENDIANESS}{len(value)}s', value)

    @dispatch(object)
    def _encode_value(self, value) -> bytes:
        return b''

    @dispatch(bool)
    def _encode_value(self, value: bool) -> bytes:
        return struct.pack(f'{ENDIANESS}?', value)
