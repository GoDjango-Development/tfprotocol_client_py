# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from typing import List, Tuple

import pytest
from tfprotocol_client.models.file_stat import FileStat, FileStatTypeEnum
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import TfProtocol

# pylint: disable=unused-import
from .tfprotocol import tfprotocol_instance


@pytest.mark.run(order=9)
def test_rmdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    #
    # RMDIR -> OK
    resps = []
    tfproto.rmdir_command('py_test', response_handler=resps.append)
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=10)
def test_mkdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # MKDIR -> OK
    tfproto.mkdir_command('py_test', response_handler=resps.append)
    tfproto.mkdir_command('py_test/test1', response_handler=resps.append)
    tfproto.mkdir_command('py_test/test2', response_handler=resps.append)
    tfproto.mkdir_command('py_test/test2/test21', response_handler=resps.append)
    tfproto.mkdir_command('py_test/test3', response_handler=resps.append)
    assert all(r == StatusInfo(StatusServerCode.OK) for r in resps)
    resps.clear()


@pytest.mark.run(order=11)
def test_touch_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # TOUCH -> OK
    tfproto.touch_command('py_test/test2/test.java', response_handler=resps.append)
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()
    # TOUCH -> FAILED 12
    tfproto.touch_command('py_test/test2/test.java', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.FAILED,
        code=12,
        payload=b'File already exist.',
        message='File already exist.',
    )
    resps.clear()


@pytest.mark.run(order=12)
def test_lsr_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # LSR -> OK
    tfproto.lsr_command(
        '/py_test',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test1/\nD: test3/\n",  # pylint: disable=line-too-long
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test1/\nD: test3/\n",  # pylint: disable=line-too-long
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()
    #
    tfproto.rmdir_command('/py_test/test1')


@pytest.mark.run(order=13)
def test_rename_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # RENAM -> OK
    tfproto.renam_command(
        '/py_test/test3',
        '/py_test/test3new',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.lsr_command(
        '/py_test',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test3new/\n",  # pylint: disable=line-too-long
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test3new/\n",  # pylint: disable=line-too-long
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()
    #
    tfproto.rmdir_command('/py_test/test3new')


@pytest.mark.run(order=14)
def test_cpdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # CPDIR -> OK
    tfproto.cpdir_command(
        '/py_test/test2',
        '/py_test/test2cpdir',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.lsr_command(
        '/py_test',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test2cpdir/\nF: test2cpdir/test.java\nD: test2cpdir/test21/\n",  # pylint: disable=line-too-long
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test2cpdir/\nF: test2cpdir/test.java\nD: test2cpdir/test21/\n",  # pylint: disable=line-too-long
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=15)
def test_xcpdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    #
    tfproto.mkdir_command('py_test/pattern')
    # XCPDIR -> OK
    tfproto.xcpdir_command(
        'testxcpdir',
        '/py_test/test2',
        'pattern',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK), resps[0]
    resps.clear()

    tfproto.lsr_command('/py_test', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test2cpdir/\nF: test2cpdir/test.java\nD: test2cpdir/test21/\nD: pattern/\nD: pattern/testxcpdir/\nF: pattern/testxcpdir/test.java\nD: pattern/testxcpdir/test21/\n",  # pylint: disable=line-too-long
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test2cpdir/\nF: test2cpdir/test.java\nD: test2cpdir/test21/\nD: pattern/\nD: pattern/testxcpdir/\nF: pattern/testxcpdir/test.java\nD: pattern/testxcpdir/test21/\n",  # pylint: disable=line-too-long
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=16)
def test_copy_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    tfproto.mkdir_command('/py_test/test2copy')
    #
    # COPY -> OK
    tfproto.copy_command(
        'py_test/test2/test.java',
        'py_test/test2copy/test.java',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.lsr_command('/py_test/test2copy/', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"F: test.java\n",
        message="F: test.java\n",
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.rmdir_command('/py_test/test2copy')


@pytest.mark.run(order=17)
def test_xcopy_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    #
    # XCOPY -> OK
    tfproto.xcopy_command(
        'test_xcopy.java',
        'py_test/test2/test.java',
        '/test21',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.lsr_command('/py_test', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nF: test2/test21/test_xcopy.java\nD: test2cpdir/\nF: test2cpdir/test.java\nD: test2cpdir/test21/\nF: test2cpdir/test21/test_xcopy.java\nD: pattern/\nD: pattern/testxcpdir/\nF: pattern/testxcpdir/test.java\nD: pattern/testxcpdir/test21/\nF: pattern/testxcpdir/test21/test_xcopy.java\n",  # pylint: disable=line-too-long
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nF: test2/test21/test_xcopy.java\nD: test2cpdir/\nF: test2cpdir/test.java\nD: test2cpdir/test21/\nF: test2cpdir/test21/test_xcopy.java\nD: pattern/\nD: pattern/testxcpdir/\nF: pattern/testxcpdir/test.java\nD: pattern/testxcpdir/test21/\nF: pattern/testxcpdir/test21/test_xcopy.java\n",  # pylint: disable=line-too-long
    )
    resps.clear()


@pytest.mark.run(order=18)
def test_xdel_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    #
    tfproto.rmdir_command('/py_test/pattern')
    # XDEL -> OK
    tfproto.xdel_command(
        '/py_test',
        'test.java',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.lsr_command('/py_test', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2/\nD: test2/test21/\nF: test2/test21/test_xcopy.java\nD: test2cpdir/\nD: test2cpdir/test21/\nF: test2cpdir/test21/test_xcopy.java\n",  # pylint: disable=line-too-long
        message="D: test2/\nD: test2/test21/\nF: test2/test21/test_xcopy.java\nD: test2cpdir/\nD: test2cpdir/test21/\nF: test2cpdir/test21/test_xcopy.java\n",  # pylint: disable=line-too-long
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=19)
def test_xrmdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    #
    # XRMDIR -> OK
    tfproto.xrmdir_command(
        '/py_test',
        'test2',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()

    tfproto.lsr_command('/py_test', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=3,
        payload=b"D: test2cpdir/\nD: test2cpdir/test21/\nF: test2cpdir/test21/test_xcopy.java\n",
        message="D: test2cpdir/\nD: test2cpdir/test21/\nF: test2cpdir/test21/test_xcopy.java\n",
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=20)
def test_lsrv2_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    #
    # LSRV2 -> OK
    tfproto.lsrv2_command(
        '/py_test',
        '/py_test/testrls.txt',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=21)
def test_lsv2_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    #
    # LSV2 -> OK
    tfproto.lsv2_command(
        '/py_test',
        '/py_test/testls.txt',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=22)
def test_fsize_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    # FSIZE -> OK
    tfproto.fsize_command('/py_test/testls.txt', response_handler=resps.append)
    assert resps[0] == StatusInfo(
        StatusServerCode.OK,
        code=59,
        payload=b'',
        message='59',
    )
    resps.clear()


@pytest.mark.run(order=22)
def test_fstat_command(tfprotocol_instance: TfProtocol):
    """Test for fstat command."""
    tfproto = tfprotocol_instance
    resps: List[Tuple(FileStat, StatusInfo)] = []
    # FSTAT command
    tfproto.fstat_command(
        '/py_test/testls.txt',
        response_handler=lambda stat, resp: resps.append((stat, resp)),
    )
    assert len(resps) == 1
    assert resps[0][1].status == StatusServerCode.OK
    assert resps[0][1].payload != b''  # b"F xxx xxxxxxxxx xxxxxxxxx",
    assert resps[0][0].type == FileStatTypeEnum.FILE
    assert resps[0][0].size == 59, 'File size is not 59'


@pytest.mark.run(order=23)
def test_fsizels_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    # FSIZELS -> OK
    tfproto.fsizels_command(
        '/py_test/testls.txt',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(
        StatusServerCode.CONT,
        code=109,
        payload=b'',
        message='109',
    )
    assert resps[1] == StatusInfo(
        StatusServerCode.CONT,
        code=-2,
        payload=b'',
        message='-2',
    )
    assert resps[2] == StatusInfo(
        StatusServerCode.CONT,
        code=59,
        payload=b'',
        message='59',
    )
    assert resps[3] == StatusInfo(
        StatusServerCode.CONT,
        code=-3,
        payload=b'',
        message='-3',
    )
    resps.clear()


@pytest.mark.run(order=23)
def test_fstatls_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps: List[FileStat] = []
    #
    # FSTATLS -> OK
    tfproto.fstatls_command('/py_test/testls.txt', response_handler=resps.append)
    assert len(resps) == 4, resps
    assert (
        resps[0].type == 3
        and resps[0].size == 109
        and resps[0].last_access != 0
        and resps[0].last_modification != 0
    )
    assert (
        resps[1].type == 0
        and resps[1].size == 4096
        and resps[1].last_access != 0
        and resps[1].last_modification != 0
    )
    assert (
        resps[2].type == 3
        and resps[2].size == 59
        and resps[2].last_access != 0
        and resps[2].last_modification != 0
    )
    assert (
        resps[3].type == 0
        and resps[3].size == 0
        and resps[3].last_access == 0
        and resps[3].last_modification == 0
    )
    resps.clear()


@pytest.mark.run(order=23)
def test_ftypels_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps: List[StatusInfo] = []
    #
    # FTYPELS -> OK
    tfproto.ftypels_command('/py_test/testls.txt', response_handler=resps.append)
    assert len(resps) == 4, resps
    assert resps[0] == StatusInfo(
        status=StatusServerCode.OK,
        code=3,
        payload=b'',
        message='3',
    )
    assert resps[1] == StatusInfo(
        status=StatusServerCode.OK,
        code=0,
        payload=b'',
        message='0',
    )
    assert resps[2] == StatusInfo(
        status=StatusServerCode.OK,
        code=3,
        payload=b'',
        message='3',
    )
    assert resps[3] == StatusInfo(
        status=StatusServerCode.OK,
        code=-2,
        payload=b'',
        message='-2',
    )
    resps.clear()
