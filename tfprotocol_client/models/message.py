import struct
from io import BytesIO
from typing import Optional, Union
from multipledispatch import dispatch

from tfprotocol_client.misc.constants import ENDIANESS, STRING_ENCODING


class TfProtocolMessage:
    """Transfer Protocol Message object builder."""

    def __init__(
        self,
        *payloads,
        custom_header: Union[int, bytes, None] = None,
        trim_body: bool = True,
    ) -> None:
        self.custom_header = self._encode_value(custom_header)
        self.body_buffer = BytesIO()
        for e in payloads:
            self.add(b' ')
            self.add(e)
        self.trim_body = trim_body

    def add(self, payload: Union[str, bytes, int, bool]):
        self.body_buffer.write(self._encode_value(payload))

    @property
    def header(self) -> bytes:
        if self.custom_header is not None:
            header = self._encode_value(self.custom_header)
        else:
            header = self._encode_value(len(self.body_buffer.getvalue()))
        return header

    @property
    def payload(self) -> bytes:
        if self.trim_body:
            return self.body_buffer.getvalue().strip(b' ')
        return self.body_buffer.getvalue()

    def __iter__(self):
        yield self.header
        yield self.payload

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
    def _encode_value(self, _) -> Optional[bytes]:
        return None

    @dispatch(bool)
    def _encode_value(self, value: bool) -> bytes:
        return struct.pack(f'{ENDIANESS}?', value)
