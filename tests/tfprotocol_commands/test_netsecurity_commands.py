# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from typing import List, Optional

import pytest
from tfprotocol_client.misc.constants import SECFS_ALL_PERMISSIONS
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import TfProtocol

# pylint: disable=unused-import
from .tfprotocol import tfprotocol_instance

__LOCK_ID: Optional[str] = None


@pytest.mark.run(order=70)
def test_netlock_command(tfprotocol_instance: TfProtocol):
    """Test for netlock command."""
    # pylint: disable=global-statement
    global __LOCK_ID
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.touch_command('/py_test/test.lock')
    # NETLOCK command
    tfproto.netlock_command(
        5,
        '/py_test/test.lock',
        response_handler=resps.append,
    )
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None, resps[0]
    #
    __LOCK_ID = resps[0].message
    #
    # tfproto.del_command('/py_test/test.lock')


@pytest.mark.run(order=71)
def test_netlocktry_command(tfprotocol_instance: TfProtocol):
    """Test for netlocktry command."""
    # pylint: disable=global-statement
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.touch_command('/py_test/testtry.lock')
    # NETLOCKTRY command
    tfproto.netlocktry_command(
        5,
        '/py_test/testtry.lock',
        response_handler=resps.append,
    )
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None, resps[0]
    #
    #
    # tfproto.del_command('/py_test/testtry.lock')


@pytest.mark.run(order=72)
def test_netunlock_command(tfprotocol_instance: TfProtocol):
    """Test for netunlock command."""
    # pylint: disable=global-statement
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    # NETUNLOCK command
    tfproto.netunlock_command(
        __LOCK_ID,
        response_handler=resps.append,
    )
    assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].message is not None, resps[0]
    #
    tfproto.del_command('/py_test/test.lock')


@pytest.mark.run(order=73)
def test_netmut_command(tfprotocol_instance: TfProtocol):
    """Test for netmutacqtry and netmutrel command."""
    # pylint: disable=global-statement
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.touch_command('/py_test/test.mut')
    # NETMUTACQTRY command
    tfproto.netmutacqtry_command(
        '/py_test/test.mut',
        'testtoken',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    # NETMUTREL command
    tfproto.netmutrel_command(
        '/py_test/test.mut',
        'testtoken',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    #
    # tfproto.del_command('/py_test/test.mut')


@pytest.mark.run(order=74)
def test_sec_file_system_commands(tfprotocol_instance: TfProtocol):
    """Test for security file system commands."""
    # pylint: disable=global-statement
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.mkdir_command('/py_test/test_secfsys/')
    # SETFSID command
    tfproto.setfsid_command(
        'secid',
        response_handler=resps.append,
    )
    assert resps[0].status == StatusServerCode.OK, resps[0]
    # SETFSPERM command
    tfproto.setfsperm_command(
        'secid',
        SECFS_ALL_PERMISSIONS,
        '/py_test/test_secfsys/',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    # ISSECFS command
    tfproto.issecfs_command(
        '/py_test/test_secfsys/',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    # GETFSPERM command
    tfproto.getfsperm_command(
        'secid',
        '/py_test/test_secfsys/',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message is not None and resps[-1].message != '', resps[-1]
    # REMFSPERM command
    tfproto.remfsperm_command(
        'secid',
        '/py_test/test_secfsys/',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    #
    # tfproto.del_command('/py_test/test.mut')


@pytest.mark.run(order=75)
def test_locksys_command(tfprotocol_instance: TfProtocol):
    """Test for locksys command."""
    # pylint: disable=global-statement
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    tfproto.mkdir_command('/py_test/test_locksys/')
    # LOCKSYS command (NOT WORKING PROPERLY YET)
    tfproto.locksys_command(
        'secid',
        response_handler=resps.append,
    )
    # assert resps[0].status == StatusServerCode.OK, resps[0]
    assert resps[0].status == StatusServerCode.UNKNOWN, resps[0]

    tfproto.touch_command(
        '/py_test/test_locksys/testfile',
        response_handler=resps.append,
    )
    # assert resps[-1].status == StatusServerCode.FAILED, resps[-1]
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
