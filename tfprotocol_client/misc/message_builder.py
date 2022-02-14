import struct
from typing import Final, Union
from multipledispatch import dispatch
from tfprotocol_client.misc.constants import ENDIANESS, STRING_ENCODING
from tfprotocol_client.misc.parse_utils import (
    separate_status_codenumber,
    separate_status_name,
)
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
        self, header: int, message: bytes, parse_code: bool = True
    ) -> StatusInfo:
        code: int = header
        msg_str: str = str(message, encoding='utf8')
        status_str, msg_str = separate_status_name(msg_str)
        status: StatusServerCode = StatusServerCode.from_str(status_str.upper())
        status: StatusServerCode = StatusServerCode.UNKNOWN if status is None else status

        if (status != StatusServerCode.FAILED) or not parse_code:
            # ? <status> [<msg_str>]
            msg_str = msg_str.replace(status.name, '', 1).strip()
            code = status.value
        else:
            # ? FAILED <str_code> : <msg_str>
            str_code, msg_str = separate_status_codenumber(msg_str)
            msg_str = msg_str.strip().replace(' : ', '', 1)
            code = int(str_code)
        return StatusInfo(status, code=code, message=msg_str)

    def build_recvd_header(self, encoded_header: bytes):
        return int.from_bytes(encoded_header, byteorder='big')

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
