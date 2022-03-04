from typing import Optional
from tfprotocol_client.misc.parse_utils import (
    separate_status_codenumber,
    separate_status_name,
)
from tfprotocol_client.misc.constants import STRING_ENCODING
from tfprotocol_client.misc.status_server_code import StatusServerCode


class StatusInfo:
    """Status Info type from server responses."""

    def __init__(
        self,
        status: StatusServerCode = None,
        opcode: int = None,
        sz: int = None,  # pylint: disable=invalid-name
        payload: bytes = b'',
        code: int = 0,
        message: str = '',
    ):
        self.status: StatusServerCode = status
        self.opcode: int = opcode
        self.payload: bytes = payload if payload else b''
        self.code: int = code
        self.sz: int = sz  # pylint: disable=invalid-name
        self.message: str = message

    @staticmethod
    def parse(
        rawmessage: Optional[str] = None, payload: Optional[bytes] = None
    ) -> 'StatusInfo':
        status_info = None
        if rawmessage is not None:
            values = rawmessage.split(' ')
            if len(values) == 1:
                status_info = StatusInfo(StatusServerCode.from_str(values[0]), 0, '')
            else:
                status_info = StatusInfo(
                    StatusServerCode.from_str(values[0]),
                    int(values[1]) if values[1].isdigit() else None,
                    ' '.join(values[2:]),
                )
        if payload is not None:
            status_info.payload = payload
        return status_info if status_info else StatusInfo()

    @staticmethod
    def build_status(
        header: int, message: bytes, parse_code: bool = True
    ) -> 'StatusInfo':
        code: int = header
        msg_str: str = str(message, encoding=STRING_ENCODING)
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
        return StatusInfo(status, code=code, message=msg_str, payload=message)

    def __str__(self):
        return f'StatusInfo[{self.status.name}]<{self.code}, "{self.message[:1000]}">'
