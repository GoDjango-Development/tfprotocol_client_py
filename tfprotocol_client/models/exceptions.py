# coded by lagcleaner
# email: lagcleaner@gmail.com

from enum import Enum
from typing import Optional, Union
from tfprotocol_client.misc.constants import STRING_ENCODING
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.models.status_info import StatusInfo


class ErrorCode(Enum):
    """Error Code for `TfExceptions`"""

    ON_WRITE_OR_RECEIVE_TO_SOCKET = 0
    ILLEGAL_ARGUMENTS = 1
    UNHANDLED_EXCEPTION = 2
    CAN_PUT = 3


class TfException(Exception):
    """Transfer Protocol Exception"""

    def __init__(
        self,
        *args: tuple,
        exception: Optional[Exception] = None,
        message: Optional[str] = None,
        status_info: Optional[StatusInfo] = None,
        status_server_code: Optional[StatusServerCode] = None,
        code: Union[int, ErrorCode, None] = None,
    ) -> None:
        super().__init__(*args, message)
        if status_info:
            self.status_info: StatusInfo = status_info
        else:
            self.status_info = StatusInfo(status=StatusServerCode.FAILED)
        if exception:
            self.original_exception: Exception = exception
            self.status_info.code = hash(exception)
            self.status_info.message = str(exception)
        if status_server_code:
            self.status_info.status = status_server_code
        if message:
            self.status_info.message = message
        if code:
            self.status_info.code = code.value if isinstance(code, ErrorCode) else code

    @property
    def payload(self):
        return (
            self.status_info.payload
            if self.status_info.payload is not None
            else self.status_info.message.encode(STRING_ENCODING)
        )

    def __str__(self) -> str:
        return f'''\n--------------------------------------------------
{self.status_info.status}
{self.status_info.code}
{self.status_info.message}
--------------------------------------------------\n'''
