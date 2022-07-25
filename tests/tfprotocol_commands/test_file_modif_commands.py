# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from time import sleep
from typing import List, Tuple

import pytest
from tfprotocol_client.models.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import TfProtocol

from .tfprotocol import tfprotocol_instance


@pytest.mark.run(order=30)
def test_chmod_command(tfprotocol_instance: TfProtocol):
    """Test for chmod command."""
    tfproto = tfprotocol_instance
    resps: List = []
    tfproto.touch_command('/py_test/file.txt')
    # CHMOD command
    tfproto.chmod_command('/py_test/file.txt', '777', response_handler=resps.append)
    assert resps[0] == StatusInfo(status=StatusServerCode.OK), resps[0]
    #
    tfproto.del_command('/py_test/file.txt')

@pytest.mark.run(order=30)
def test_chown_command(tfprotocol_instance: TfProtocol):
    """Test for chown command."""
    tfproto = tfprotocol_instance
    resps: List = []
    tfproto.touch_command('/py_test/file.txt',response_handler=resps.append)
    # CHOWN command
    # tfproto.chown_command('/py_test/file.txt', 'user', 'group', response_handler=resps.append)
    # assert resps[-1] == StatusInfo(status=StatusServerCode.OK), resps[-1]
    #
    tfproto.del_command('/py_test/file.txt')


@pytest.mark.run(order=31)
def test_fpub_command(tfprotocol_instance: TfProtocol):
    """Test for fpub command."""
    tfproto = tfprotocol_instance
    resps: List[Tuple(FileStat,StatusInfo)] = []
    tfproto.touch_command('/py_test/file.txt')
    # CHOWN command
    sleep(3)
    tfproto.fupd_command('/py_test/file.txt',response_handler=resps.append)
    assert resps[-1] == StatusInfo(status=StatusServerCode.OK), resps[-1]

    tfproto.fstat_command('/py_test/file.txt',response_handler=lambda s,r: resps.append((s,r)))
    assert resps[-1][1].status == StatusServerCode.OK
    # assert resps[-1][0].last_modification > resps[-1][0].last_access, resps[-1]
    #
    tfproto.del_command('/py_test/file.txt')

