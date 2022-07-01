# coded by lagcleaner
# email: lagcleaner@gmail.com

from io import BytesIO
from typing import Union
from multipledispatch import dispatch
from tfprotocol_client.misc.build_utils import MessageUtils
from tfprotocol_client.misc.constants import (
    DFLT_HEADER_SIZE,
    INT_SIZE,
)


class TfProtocolMessage:
    """Transfer Protocol Message object builder."""

    def __init__(
        self,
        *payloads,
        custom_header: Union[int, bytes, None] = None,
        header_signed: bool = True,
        trim_body: bool = False,
        separate_by_spaces: bool = True,
        header_size: int = DFLT_HEADER_SIZE,
    ) -> None:
        self.custom_header = MessageUtils.encode_value(
            custom_header, size=header_size, signed=header_signed
        )
        self.body_buffer = BytesIO()
        self.header_size = header_size if header_size else DFLT_HEADER_SIZE
        self.header_signed = header_signed
        for i, e in enumerate(payloads):
            if separate_by_spaces and i != 0:
                self.add(b' ')
            self.add(e)
        self.trim_body = trim_body

    @dispatch((str, bytes, bool))
    def add(self, payload: Union[str, bytes, bool], **_):
        self.body_buffer.write(MessageUtils.encode_value(payload))
        return self

    # pylint: disable=function-redefined
    @dispatch(int)
    def add(self, payload: int, size: int = INT_SIZE, signed=False, **_):
        self.body_buffer.write(
            MessageUtils.encode_value(payload, size=size, signed=signed)
        )
        return self

    @property
    def header(self) -> bytes:
        if self.custom_header is not None:
            header = MessageUtils.encode_value(self.custom_header)
        else:
            header = MessageUtils.encode_value(
                len(self.payload), size=self.header_size, signed=self.header_signed
            )
        return header

    @property
    def payload(self) -> bytes:
        if self.trim_body:
            return self.body_buffer.getvalue().strip(b' ')
        return self.body_buffer.getvalue()

    def __iter__(self):
        yield self.header
        yield self.payload
