# coded by lagcleaner
# email: lagcleaner@gmail.com

import re
from typing import Tuple, Union

from tfprotocol_client.misc.constants import STRING_ENCODING
from tfprotocol_client.models.status_server_code import StatusServerCode


def separate_status(string: str):
    res = re.split(r'\s+', string, maxsplit=1)
    # res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    status: StatusServerCode = StatusServerCode.from_str(res[0])
    if status is not None:
        return status, ''.join(res[1:]) if len(res) > 1 else ''
    return None, string


def separate_status_b(data: bytes) -> Tuple[StatusServerCode, bytes]:
    res = re.split(br'\s+', data, maxsplit=1)
    # res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    status: StatusServerCode = StatusServerCode.from_str(
        str(res[0], encoding=STRING_ENCODING).upper()
    )

    if status is not None:
        return status, b''.join(res[1:]) if len(res) > 1 else b''
    return None, data


def separate_status_codenumber(string: str) -> Tuple[str, str]:
    res = re.split(r'([-+]?\d+\.\d+)|([-+]?\d+)', string.strip(), maxsplit=1)
    res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    if len(res_f) > 1 and res_f[0].isdigit():
        return res_f[0], ''.join(res_f[1:])
    else:
        return '', ''.join(res_f)


def separate_status_codenumber_b(data: bytes):
    res = re.split(br'([-+]?\d+\.\d+)|([-+]?\d+)', data.lstrip(), maxsplit=1)
    res_f = [r for r in res if r is not None and r.strip() != b'']
    if len(res_f) > 1 and isnumber(res_f[0]):
        return res_f[0], b''.join(res_f[1:]).lstrip()
    return b'', b''.join(res_f)


def isnumber(data: bytes):
    if data.isdigit():
        return True
    numb = data.split(b'.', maxsplit=1)
    return all(part.isdigit() for part in numb)


def tryparse_int(
    str_value: Union[str, bytes, bytearray], base: int = 10, dflt_value: int = 0
) -> int:
    try:
        if isinstance(str_value, (bytes, bytearray)):
            str_value = str(str_value, encoding=STRING_ENCODING)
        return int(str_value, base=base)
    except ValueError:
        return dflt_value
