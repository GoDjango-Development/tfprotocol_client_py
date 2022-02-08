from datetime import datetime
from enum import Enum
from typing import Final, Union


class FileStatTypeEnum(Enum):
    DIR = 0
    FILE = 1
    UNKNOWN = 2


class FileStat:
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
            if filestat_type.capitalize() == 'F':
                _type = FileStatTypeEnum.FILE
            elif filestat_type.capitalize() == 'D':
                _type = FileStatTypeEnum.DIR
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
