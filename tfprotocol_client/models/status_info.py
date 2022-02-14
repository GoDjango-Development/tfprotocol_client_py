from typing import Optional
from tfprotocol_client.misc.status_server_code import StatusServerCode


class StatusInfo:
    """Status Info type from server responses."""

    def __init__(
        self,
        status: StatusServerCode = None,
        opcode: int = None,
        sz: int = None,  # pylint: disable=invalid-name
        payload: bytes = None,
        code: int = 0,
        message: str = '',
    ):
        self.status: StatusServerCode = status
        self.opcode: int = opcode
        self.payload: bytes = payload
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

    def __str__(self):
        return f'StatusInfo[{self.status.name}]<{self.code}, "{self.message}">'
