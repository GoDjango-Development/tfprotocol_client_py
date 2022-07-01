# coded by lagcleaner
# email: lagcleaner@gmail.com

from enum import Enum


class StatusServerCode(Enum):
    """Status Server Code Enum."""
    OK = 0
    FAILED = 1
    UNKNOWN = 2
    CONT = 3
    BREAK = 4
    DISCONNECTED = 5
    PAYLOAD_TOO_BIG = 6

    @staticmethod
    def from_str(label):
        try:
            return StatusServerCode[label]
        except (KeyError, ValueError):
            return None
