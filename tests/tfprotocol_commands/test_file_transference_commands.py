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


@pytest.mark.run(order=50)
def test_put_get_commands(tfprotocol_instance: TfProtocol):
    """Test for put and get commands."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    # PUT
    tfproto.put_command(
        io.BytesIO(b'Some random text'),
        'py_test/test_putget.txt',
        0,
        1024,
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(
        status=StatusServerCode.OK,
        payload=b'\x00\x00\x00\x00\x00\x00\x04\x00',
        message='\x00\x00\x00\x00\x00\x00\x04\x00',
        code=1024,
    ), resps[0]
    assert all((r.status == StatusServerCode.OK) for r in resps)
    resps.clear()
    #
    # GET
    sink = io.BytesIO()
    tfproto.get_command(
        sink,
        'py_test/test_putget.txt',
        0,
        1024,
        response_handler=resps.append,
    )
    assert sink.getvalue() == b'Some random text'
    assert resps[0] == StatusInfo(
        status=StatusServerCode.OK,
        payload=b'\x00\x00\x00\x00\x00\x00\x04\x00',
        message='\x00\x00\x00\x00\x00\x00\x04\x00',
        code=1024,
    ), resps[0]
    assert all((r.status == StatusServerCode.OK) for r in resps)
    assert resps[-1] == StatusInfo(
        status=StatusServerCode.OK,
        code=PutGetCommandEnum.HPFFIN.value,
    ), resps[-1]
    assert resps[-2] == StatusInfo(StatusServerCode.OK), resps[-2]
    #
    tfproto.del_command('py_test/test_putget.txt')


@pytest.mark.run(order=50)
def test_putcan_getcan_commands(tfprotocol_instance: TfProtocol):
    """Test for putcan and getcan commands."""
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    transf_s: List[TransferStatus] = []
    #
    # PUTCAN
    tfproto.putcan_command(
        io.BytesIO(b'Some random text'),
        'py_test/test_putcangetcan.txt',
        0,
        8,
        1,
        response_handler=resps.append,
        transfer_handler=lambda _, trnsf_status: transf_s.append(trnsf_status.copy()),
    )
    assert resps[0] == StatusInfo(
        status=StatusServerCode.OK,
        payload=b'\x00\x00\x00\x00\x00\x00\x00\x08',
        message='\x00\x00\x00\x00\x00\x00\x00\x08',
        code=8,
    ), resps[0]
    assert all(ts.server_command == PutGetCommandEnum.HPFCONT.value for ts in transf_s)
    assert all((ts.last_payload_size == 8) for ts in transf_s[:-2]), transf_s[:-2]
    assert (
        all((ts.client_command is None) for ts in transf_s[:-1])
        and transf_s[-1].client_command == 0
    ), transf_s
    resps.clear()
    transf_s.clear()
    #
    # GETCAN
    sink = io.BytesIO()
    tfproto.getcan_command(
        sink,
        'py_test/test_putcangetcan.txt',
        0,
        8,
        1,
        response_handler=resps.append,
        transfer_handler=lambda _, trnsf_status: transf_s.append(trnsf_status.copy()),
    )
    assert sink.getvalue() == b'Some random text'
    assert resps[0] == StatusInfo(
        status=StatusServerCode.OK,
        payload=b'\x00\x00\x00\x00\x00\x00\x00\x08',
        message='\x00\x00\x00\x00\x00\x00\x00\x08',
        code=8,
    ), resps[0]
    assert all((ts.last_payload_size == 8) for ts in transf_s), transf_s
    assert all(
        ts.client_command == PutGetCommandEnum.HPFCONT.value for ts in transf_s[1:]
    )
    assert (
        all(ts.server_command is None for ts in transf_s[:-1])
        and transf_s[-1].server_command == 0
    )
    #
    tfproto.del_command('py_test/test_putcangetcan.txt')
