# coded by lagcleaner
# email: lagcleaner@gmail.com

from enum import Enum


class PutGetCommandEnum(Enum):
    """Commands used to put and get commands optimization."""

    HPFEND = 0
    HPFSTOP = -1
    HPFCANCEL = -2
    HPFCONT = -3
    HPFFIN = -127
