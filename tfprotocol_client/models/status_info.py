# coded by lagcleaner
# email: lagcleaner@gmail.com

from typing import Optional
from tfprotocol_client.misc.parse_utils import (
    separate_status,
    separate_status_b,
    separate_status_codenumber,
    separate_status_codenumber_b,
    tryparse_int,
)
from tfprotocol_client.misc.constants import STRING_ENCODING
from tfprotocol_client.models.status_server_code import StatusServerCode


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
        """Parse raw string message to build an instance of StatusInfo.

        Args:
            `rawmessage`: raw string message from server.
            `payload`: payload of the message.
        """
        if rawmessage is not None:
            try:
                status, msg = separate_status(rawmessage)
                code = len(rawmessage)
                if status is None:
                    # ? <msg>
                    status, msg = StatusServerCode.UNKNOWN, rawmessage
                elif status is not StatusServerCode.FAILED:
                    # ? <status> [<msg>]
                    code = status.value
                else:
                    # ? FAILED <str_code> : <msg>
                    str_code, msg = separate_status_codenumber(msg)
                    msg = msg.strip().replace(': ', '', 1)
                    code = tryparse_int(str_code, dflt_value=status.value)

                return StatusInfo(
                    status,
                    code=code,
                    message=msg,
                    payload=payload,
                )
            except:  # pylint: disable=bare-except
                pass
        return StatusInfo()

    @staticmethod
    def build_status(
        header: int,
        message: bytes,
        parse_code: bool = False,
    ) -> 'StatusInfo':
        """Build status from header and message received from the server.

        Args:
            `header`: header of the message.
            `message`: message received from the server.
            `parse_code`: if True, parse the code from the message.
        """
        code: int = header
        status: StatusServerCode = StatusServerCode.UNKNOWN
        msg: bytes = message

        if parse_code:
            str_code, msg = separate_status_codenumber_b(message)
            code = tryparse_int(str_code, dflt_value=code)

            min_index = len(msg)
            for sc in StatusServerCode:
                index = msg.find(sc.name.encode(STRING_ENCODING))
                if index >= 0 and index < min_index:
                    status = sc
                    if index == 0:
                        break
            status_name = status.name.encode(STRING_ENCODING)
            if index == 0:
                msg = msg.replace(status_name + b' ', b'', 1).lstrip()
            elif msg[-len(status_name):] == status_name:
                msg = msg.replace(b' ' + status_name, b'', 1).rstrip()
            else:
                msg = msg.replace(b' ' + status_name + b' ', b' ', 1).lstrip()
        else:
            status, msg = separate_status_b(message)

            if status is None:
                # ? <msg>
                status, msg = StatusServerCode.UNKNOWN, message
            elif status is not StatusServerCode.FAILED:
                # ? <status> [<msg>]
                code = status.value
            else:
                # ? FAILED <str_code> : <msg>
                str_code, msg = separate_status_codenumber_b(msg)
                msg = msg.strip().replace(b': ', b'', 1)
                code = tryparse_int(str_code, dflt_value=status.value)

        return StatusInfo(
            status,
            code=code,
            message=str(
                msg[:1024] + b'...' if len(msg) > 1024 else msg,
                encoding=STRING_ENCODING,
            ),
            payload=msg,
        )

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False
        __o: StatusInfo
        if (
            __o.message == self.message
            and __o.code == self.code
            and __o.status == self.status
            and __o.sz == self.sz
            and self.payload == __o.payload
        ):
            return True
        return False

    def __str__(self):
        return f'StatusInfo[{self.status.name}]<{self.code}, "{self.message}">'

    __repr__ = __str__
