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
        filestat_type: Union[str, FileStatTypeEnum],
        size: int,
        last_access: int,
        last_modification: int,
    ) -> None:
        _type = FileStatTypeEnum.UNKNOWN
        if isinstance(filestat_type, FileStatTypeEnum):
            _type = filestat_type
        elif isinstance(filestat_type, str) and len(filestat_type) == 1:
            _type = FileStatTypeEnum.from_char(
                filestat_type, dflt=FileStatTypeEnum.UNKNOWN,
            )
        self.type: Final[FileStatTypeEnum] = _type
        self.size: Final[int] = size
        self.last_access: Final[int] = last_access
        self.last_modification: Final[int] = last_modification

    def get_last_modification_date(self) -> datetime:
        return datetime.fromtimestamp(self.last_modification)

    def __str__(self) -> str:
        return (
            f'FileStat(type={self.type}, '
            f'size={self.size}, '
            f'last_access={self.last_access}, '
            f'last_mod={self.last_modification})'
        )
