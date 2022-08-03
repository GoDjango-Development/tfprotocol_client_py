# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from datetime import datetime
from time import sleep
from typing import List, Tuple

import pytest
from tfprotocol_client.misc.constants import KEY_LEN_INTERVAL
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import Date, TfProtocol

from .tfprotocol import tfprotocol_instance


@pytest.mark.run(order=35)
def test_echo_command(tfprotocol_instance: TfProtocol):
    """Test for echo command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    # ECHO command
    tfproto.echo_command('Hello World', response_handler=resps.append)
    assert resps[0] == 'Hello World'


@pytest.mark.run(order=36)
def test_date_command(tfprotocol_instance: TfProtocol):
    """Test for date command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.date_command(response_handler=lambda _, s: resps.append(s))
    # DATE command
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None and len(resps[0].message) > 0, resps[0]


@pytest.mark.run(order=37)
def test_datef_command(tfprotocol_instance: TfProtocol):
    """Test for datef command."""
    tfproto = tfprotocol_instance
    resps: List[Tuple(Date, StatusInfo)] = []
    tfproto.datef_command(response_handler=lambda d, s: resps.append((d, s)))
    # DATEF command
    assert len(resps) == 1, resps[0]
    assert resps[0][0] is not None, resps[0]
    assert resps[0][1].status == StatusServerCode.OK, resps[0]
    assert resps[0][1].message is not None and len(resps[0][1].message) > 0, resps[0]


@pytest.mark.run(order=38)
def test_dtof_command(tfprotocol_instance: TfProtocol):
    """Test for dtof command."""
    tfproto = tfprotocol_instance
    resps: List[Tuple(Date, StatusInfo)] = []
    tfproto.dtof_command(
        datetime.timestamp(datetime.now()),
        response_handler=lambda d, s: resps.append((d, s)),
    )
    # DTOF command
    assert len(resps) == 1, resps[0]
    assert resps[0][0] is not None, resps[0]
    assert resps[0][1].status == StatusServerCode.OK, resps[0]
    assert resps[0][1].message is not None and len(resps[0][1].message) > 0, resps[0]
@pytest.mark.run(order=39)
def test_fpub_command(tfprotocol_instance: TfProtocol):
    """Test for fpub command."""
    tfproto = tfprotocol_instance
    resps: List[Tuple(FileStat, StatusInfo)] = []
    tfproto.touch_command('/py_test/file.txt')
    # FPUB command
    sleep(3)
    tfproto.fupd_command('/py_test/file.txt', response_handler=resps.append)
    assert resps[-1] == StatusInfo(status=StatusServerCode.OK), resps[-1]

    tfproto.fstat_command(
        '/py_test/file.txt', response_handler=lambda s, r: resps.append((s, r))
    )
    assert resps[-1][1].status == StatusServerCode.OK
    # assert resps[-1][0].last_modification > resps[-1][0].last_access, resps[-1]
    #
    tfproto.del_command('/py_test/file.txt')
