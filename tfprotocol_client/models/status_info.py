from email import message
from typing import List, Optional
from tfprotocol_client.misc.status_server_code import StatusServerCode


class StatusInfo:
    def __init__(
        self,
        status: StatusServerCode = None,
        opcode: int = None,
        sz: int = None,
        payload: bytes = None,
        code: int = 0,
        message: str = '',
    ):
        self.status: StatusServerCode = status
        self.opcode: int = opcode
        self.payload: bytes = payload
        self.code: int = code
        self.sz: int = sz
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
