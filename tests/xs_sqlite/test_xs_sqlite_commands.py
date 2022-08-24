# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from datetime import datetime
from typing import List, Tuple

import pytest
from tfprotocol_client.extensions.xs_sqlite import XSSQLite
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import Date, TfProtocol

# pylint: disable=unused-import
from .xs_sqlite import xssqlite_instance


def test_xssqlite_command(xssqlite_instance: XSSQLite):
    """Test for xs_sqlite command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # XS_SQLITE command
    tfproto.xssqlite_command(response_handler=resps.append)
    assert resps[0].status in (StatusServerCode.OK, StatusServerCode.UNKNOWN), resps[0]


def test_xssqlite_open_command(xssqlite_instance: XSSQLite):
    """Test for open command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # OPEN command
    tfproto.open_command('py_test/db.db', response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message not in (None, ''), resps[0]
