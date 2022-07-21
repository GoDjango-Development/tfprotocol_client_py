# coded by lagcleaner
# email: lagcleaner@gmail.com

from datetime import datetime
from enum import Enum
import struct
from typing import Final, Tuple, Union
from tfprotocol_client.misc.constants import ENDIANESS
from tfprotocol_client.models.exceptions import TfException


class FileStatTypeEnum(Enum):
    """Describes a type of File.
    """

    DIR = 0
    FILE = 1
    UNKNOWN = 2

    @staticmethod
    def from_char(bchar: str, dflt=None):
        try:
            for enum_v in FileStatTypeEnum:
                if enum_v.name.startswith(bchar):
                    return enum_v
            return dflt
        except (KeyError, ValueError):
            return dflt


class FileStat:
    """File Stat object, used to contain file info.
    """

    def __init__(
        self,
        filestat_type: Union[int, str, FileStatTypeEnum],
        size: int,
        last_access: int,
        last_modification: int,
    ) -> None:
        self.type: Final[Union[FileStatTypeEnum, int]] = filestat_type
        self.size: Final[int] = size
        self.last_access: Final[int] = last_access
        self.last_modification: Final[int] = last_modification

    @property
    def last_modification_date(self) -> datetime:
        if self.last_modification:
            return datetime.fromtimestamp(self.last_modification)
        return None

    @property
    def last_access_date(self) -> datetime:
        if self.last_access:
            return datetime.fromtimestamp(self.last_access)
        return None

    def __str__(self) -> str:
        return (
            f'FileStat(type={self.type}, '
            f'size={self.size}, '
            f'last_access={self.last_access}, '
            f'last_mod={self.last_modification})'
        )
    __repr__ = __str__

    @staticmethod
    def build_from_structure(fstatstruct: bytes) -> Tuple[int, 'FileStat']:
        """Build a FileStat object from fstatstruct structure."""
        if len(fstatstruct) != 26:
            raise TfException(message='Invalid format of `fstathdr`...')
        code, _type, size, atime, mtime = struct.unpack(
            f'{ENDIANESS}bbQQQ', fstatstruct
        )
        return code, FileStat(_type, size, atime, mtime)
