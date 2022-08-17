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

