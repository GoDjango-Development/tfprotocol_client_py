import struct
from typing import Final, Optional
from multipledispatch import dispatch
from tfprotocol_client.misc.constants import (
    DFLT_HEADER_SIZE,
    ENDIANESS,
    INT_SIZE,
    SHORT_SIZE,
    STRING_ENCODING,
)


class MessageUtils:
    """Message utils for comunication with transfer protocol"""

    def __init__(self, max_buffer_size: int) -> None:
        self.max_buffer_size: Final[int] = max_buffer_size

    @staticmethod
    @dispatch(str)
    def encode_value(value: str, **_) -> bytes:
        encoded_str = value.encode(STRING_ENCODING)
        return struct.pack(f'{ENDIANESS}{len(encoded_str)}s', encoded_str)

    @staticmethod
    @dispatch(int)
    # pylint: disable=function-redefined
    def encode_value(value: int, size: int = DFLT_HEADER_SIZE, **_,) -> bytes:
        value_size = value.bit_length() // 8 + (value.bit_length() % 8 != 0)
        if value_size <= SHORT_SIZE and size <= SHORT_SIZE:
            # 1-16 bit // 2 bytes
            return struct.pack(f'{ENDIANESS}h', value)
        if value_size <= INT_SIZE and size <= INT_SIZE:
            # 17-32 bit // 4 bytes
            return struct.pack(f'{ENDIANESS}i', value)
        # 33-64 bit // 8 bytes
        return struct.pack(f'{ENDIANESS}q', value)

    @staticmethod
    @dispatch(bytes)
    # pylint: disable=function-redefined
    def encode_value(value: bytes, **_) -> bytes:
        return struct.pack(f'{ENDIANESS}{len(value)}s', value)

    @staticmethod
    @dispatch(object)
    # pylint: disable=function-redefined
    def encode_value(_, **__) -> Optional[bytes]:
        return None

    @staticmethod
    @dispatch(bool)
    # pylint: disable=function-redefined
    def encode_value(value: bool, **_) -> bytes:
        return struct.pack(f'{ENDIANESS}?', value)

    @staticmethod
    def decode_str(value: bytes) -> str:
        return str(value, encoding=STRING_ENCODING)

    @staticmethod
    def decode_int(value: bytes) -> int:
        return int.from_bytes(value, byteorder='big')

