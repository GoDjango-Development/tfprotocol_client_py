# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

import io
from typing import List, Tuple

import pytest
from tfprotocol_client.models.putget_commands import PutGetCommandEnum
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.models.transfer_state import TransferStatus
from tfprotocol_client.tfprotocol import TfProtocol

from .tfprotocol import tfprotocol_instance


@pytest.mark.run(order=50)
def test_sup_sdown_commands(tfprotocol_instance: TfProtocol):
    """Test for sup and sdown commands."""
    tfproto = tfprotocol_instance
    #
    # SUP
    success = tfproto.sup_command(
        'py_test/test_supdown.txt',
        io.BytesIO(b'Some random text'),
        5,
    )
    assert success, 'SUP command failed'
    #
    # SDOWN
    sink = io.BytesIO()
    success = tfproto.sdown_command(
        'py_test/test_supdown.txt',
        sink,
        5,
    )
    sink.seek(0)
    assert success, 'SDOWN command failed'
    assert (
        sink.getvalue() == b'Some random text'
    ), 'SDOWN command retrieve a corrupted file'
    #
    tfproto.del_command('py_test/test_supdown.txt')


def __rcvfile_handler(
    status: StatusInfo,
    sink: io.BytesIO = None,
    resps: List[StatusInfo] = None,
):
    if sink is not None and sink.writable() and status.payload:
        sink.write(status.payload)
    resps.append(status)


@pytest.mark.run(order=50)
def test_snd_rcv_commands(tfprotocol_instance: TfProtocol):
    """Test for sndfile and rcvfile commands."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    # SENDFILE
    tfproto.sndfile_command(
        True,
        'py_test/test_sendrcv.txt',
        io.BytesIO(b'Some random text'),
        lambda _, __, status, ___: resps.append(status),
    )
    assert all((r.status == StatusServerCode.CONT) for r in resps[:-1])
    assert resps[-1].status == StatusServerCode.OK
    resps.clear()
    #
    # RECVFILE
    sink = io.BytesIO()
    tfproto.rcvfile_command(
        True,
        'py_test/test_sendrcv.txt',
        sink,
        lambda _, __, status, sink: __rcvfile_handler(status, sink, resps),
    )
    assert sink.getvalue() == b'Some random text'
    assert all((r.status == StatusServerCode.CONT) for r in resps[:-1])
    assert resps[-1].status == StatusServerCode.OK
    #

