import re
from typing import Tuple


def separate_status_name(string: str):
    res = re.split(r'\s+', string.strip(), maxsplit=1)
    # res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    if len(res) > 1:
        return res[0], ''.join(res[1:])
    else:
        return res[0], ''


def separate_status_codenumber(string: str) -> Tuple[str, str]:
    res = re.split(r'([-+]?\d+\.\d+)|([-+]?\d+)', string.strip(), maxsplit=1)
    res_f = [r.strip() for r in res if r is not None and r.strip() != '']
    if len(res_f) > 1 and res_f[0].isdecimal():
        return res_f[0], ''.join(res_f[1:])
    else:
        return '', ''.join(res_f)


def tryparse_int(str_value: str, base: int = 10, dflt_value: int = 0) -> int:
    try:
        return int(str_value, base=base)
    except ValueError:
        return dflt_value
