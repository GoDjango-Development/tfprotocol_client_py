# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

import io
from typing import List

import pytest

from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import TfProtocol

# pylint: disable=unused-import
from .tfprotocol import tfprotocol_instance


@pytest.mark.run(order=60)
def test_integrity_rw_commands(tfprotocol_instance: TfProtocol):
    """Test for intread and intwrite commands."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    tfproto.sup_command(
        'py_test/test_integrity.txt',
        io.BytesIO(b'Some random text'),
        5,
    )
    #
    # INTREAD -> FAILED (file not found)
    sink = io.BytesIO()
    tfproto.intread_command(
        'py_test/test_integrity_NOT_EXISTING.txt', sink, response_handler=resps.append
    )
    assert sink.getvalue() == b''
    assert resps[-1] == StatusInfo(StatusServerCode.FAILED, code=-1)

    #
    # INTREAD -> OK
    sink = io.BytesIO()
    tfproto.intread_command(
        'py_test/test_integrity.txt', sink, response_handler=resps.append
    )
    assert sink.getvalue() == b'Some random text'
    assert resps[-1].status == StatusServerCode.OK and resps[-1].code == 16 and resps[-1].message != '',resps[-1]

    #
    # INTWRITE
    tfproto.intwrite_command(
        'py_test/test_integrity.txt',
        io.BytesIO(b'Some random text number 2'),
        resps[-1].message,
        response_handler=resps.append,
    )

    assert resps[-1].status == StatusServerCode.OK and resps[-1].code == 0 ,resps[-1]
    resps.clear()
    #
    tfproto.del_command('py_test/test_integrity.txt')
