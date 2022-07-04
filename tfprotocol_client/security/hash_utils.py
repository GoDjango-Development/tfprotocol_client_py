# coded by lagcleaner
# email: lagcleaner@gmail.com

import hashlib
from typing import Union


def sha256_for(payload: Union[bytes, str]):
    '''Extract a unique SHA256 hash from a payload'''
    binary_data = payload.encode("utf8") if isinstance(payload, str) else payload
    return hashlib.sha256(binary_data).digest()


def hexstr(data: bytes) -> str:
    return '0x' + data.hex()
