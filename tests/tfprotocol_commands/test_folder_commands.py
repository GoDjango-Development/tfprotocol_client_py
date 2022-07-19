# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name

from functools import wraps
import os
from typing import Optional

import pytest
from dotenv import load_dotenv
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import TfProtocol

from .tfprotocol import tfprotocol_instance

load_dotenv()


@pytest.mark.run(order=9)
def test_tfprotocol_rmdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    #
    # RMDIR -> OK
    resps = []
    tfproto.rmdir_command(
        'py_test',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()


@pytest.mark.run(order=10)
def test_tfprotocol_mkdir_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # MKDIR -> OK
    tfproto.mkdir_command(
        'py_test',
        response_handler=resps.append,
    )
    tfproto.mkdir_command(
        'py_test/test1',
        response_handler=resps.append,
    )
    tfproto.mkdir_command(
        'py_test/test2',
        response_handler=resps.append,
    )
    tfproto.mkdir_command(
        'py_test/test2/test21',
        response_handler=resps.append,
    )
    tfproto.mkdir_command(
        'py_test/test3',
        response_handler=resps.append,
    )
    assert all(r == StatusInfo(StatusServerCode.OK) for r in resps)
    resps.clear()


@pytest.mark.run(order=11)
def test_tfprotocol_touch_command(tfprotocol_instance: TfProtocol):
    tfproto = tfprotocol_instance
    resps = []
    # TOUCH -> OK
    tfproto.touch_command(
        'py_test/test2/test.java',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(StatusServerCode.OK)
    resps.clear()
    # TOUCH -> FAILED 12
    tfproto.touch_command(
        'py_test/test2/test.java',
        response_handler=resps.append,
    )
    assert resps[0] == StatusInfo(
        StatusServerCode.FAILED,
        code=12,
        payload=b'File already exist.',
        message='File already exist.',
    )
    resps.clear()


@pytest.mark.run(order=12)
def test_tfprotocol_lsr_command(tfprotocol_instance: TfProtocol):
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
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test1/\nD: test3/\n",
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test1/\nD: test3/\n",
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()
    #
    tfproto.rmdir_command('/py_test/test1')


@pytest.mark.run(order=13)
def test_tfprotocol_rename_command(tfprotocol_instance: TfProtocol):
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
        payload=b"D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test3new/\n",
        message="D: test2/\nF: test2/test.java\nD: test2/test21/\nD: test3new/\n",
    )
    assert resps[1] == StatusInfo(StatusServerCode.OK)
    resps.clear()
    #
    tfproto.rmdir_command('/py_test/test3new')
