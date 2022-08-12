# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

import io
from time import sleep
from typing import Callable, List

import pytest
from tfprotocol_client.models.putget_commands import PutGetCommandEnum
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.models.transfer_state import TransferStatus
from tfprotocol_client.tfprotocol import TfProtocol

# pylint: disable=unused-import
from .tfprotocol import tfprotocol_instance


def __ntfy_handler(
    status: StatusInfo,
    send_ok: Callable,
    send_del: Callable,
    resps: List[StatusInfo] = None,
    callback: Callable = lambda: None,
) -> None:
    resps.append(status)
    sleep(5)
    callback()


@pytest.mark.run(order=50)
def test_ntfy_system_commands(tfprotocol_instance: TfProtocol):
    """Test for notify system commands."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    # ADDNTFY
    tfproto.addntfy_command(
        'test',
        'py_test/test_ntfy.txt',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, 'addntfy command failed'
    #
    # STARTNFY
    # tfproto.startnfy_command(
    #     3,
    #     response_handler=lambda status, send_ok, send_del: __ntfy_handler(
    #         status,
    #         send_ok,
    #         send_del,
    #         resps,
    #         lambda: tfproto.disconnect(),
    #     ),
    # )
    #
    tfproto.del_command('py_test/test_ntfy.txt')
