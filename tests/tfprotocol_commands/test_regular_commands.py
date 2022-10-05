# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from datetime import datetime
from time import sleep
from typing import List, Tuple

import pytest
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import Date, TfProtocol

# pylint: disable=unused-import
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


@pytest.mark.run(order=38)
def test_ftod_command(tfprotocol_instance: TfProtocol):
    """Test for ftod command."""
    tfproto = tfprotocol_instance
    resps: List[Tuple(int, StatusInfo)] = []
    tfproto.ftod_command(
        '1999-12-10 12:12:0',
        response_handler=lambda i, s: resps.append((i, s)),
    )
    # FTOD command
    assert len(resps) == 1, resps[0]
    assert resps[0][0] > 1659536725466, resps[0]
    assert resps[0][1].status == StatusServerCode.OK, resps[0]
    assert resps[0][1].message == '944827920', resps[0]


@pytest.mark.run(order=38)
def test_udate_command(tfprotocol_instance: TfProtocol):
    """Test for udate command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.udate_command(response_handler=resps.append)
    # UDATE command
    assert len(resps) == 1, resps
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None and resps[0].message != '', resps[0]


# @pytest.mark.run(order=38)
# def test_nigma_command(tfprotocol_instance: TfProtocol):
#     """Test for nigma command."""
#     # NOTE: This test is not reliable, because the server is not working properly.
#     tfproto = tfprotocol_instance
#     resps: List[StatusInfo] = []
#     # NIGMA command - OK
#     old_key = tfproto.client.session_key
#     tfproto.nigma_command(KEY_LEN_INTERVAL[0], response_handler=resps.append)
#     assert old_key != tfproto.client.session_key, resps[0]

#     # Exception case
#     with pytest.raises(TfException):
#         tfproto.nigma_command(9, response_handler=resps.append)


@pytest.mark.run(order=39)
def test_freesp_command(tfprotocol_instance: TfProtocol):
    """Test for freesp command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.freesp_command(response_handler=resps.append)
    # FREESP command
    assert len(resps) == 1, resps
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None and resps[0].message != '', resps[0]


@pytest.mark.run(order=39)
def test_prockey_command(tfprotocol_instance: TfProtocol):
    """Test for prockey command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.prockey_command(response_handler=resps.append)
    # PROCKEY command
    assert len(resps) == 1, resps
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None, resps[0]


@pytest.mark.run(order=40)
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


@pytest.mark.run(order=41)
def test_sha256_command(tfprotocol_instance: TfProtocol):
    """Test for sha256 command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.touch_command('/py_test/file.txt')
    # SHA256 command
    tfproto.sha256_command('/py_test/file.txt', response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message == "0xe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", resps[-1] # pylint: disable=line-too-long
    #
    tfproto.del_command('/py_test/file.txt')

@pytest.mark.run(order=42)
def test_end_command(tfprotocol_instance: TfProtocol):
    """Test for end command."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    # END command
    tfproto.end_command()
    with pytest.raises(TfException):
        tfproto.echo_command('Hello', response_handler=resps.append)
    #
    tfproto.connect()
    tfproto.connect()
