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
    assert resps[0].status == StatusServerCode.OK, resps[0]
    # assert resps[0].status in (StatusServerCode.OK, StatusServerCode.UNKNOWN), resps[0]


@pytest.mark.depends(on=['test_xssqlite_command'])
def test_xssqlite_open_close_commands(xssqlite_instance: XSSQLite):
    """Test for open and close commands."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # OPEN command
    tfproto.open_command('py_test.db', response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    db_id = resps[-1].message.split()[-1]
    # CLOSE command
    tfproto.close_command(db_id, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message not in (None, ''), resps[0]
