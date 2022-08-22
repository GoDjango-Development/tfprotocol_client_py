# coded by lagcleaner
# email: lagcleaner@gmail.com
import pytest
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode


@pytest.mark.run(order=5)
def test_status_info_build():
    """Test for status_info builder function"""
    # test OK
    status = StatusInfo.build_status(2, b'OK')
    assert status.status == StatusServerCode.OK
    assert status.code == 0
    assert status.payload == b''
    assert status.message == ''

    # test OK (with initial parse code)
    status = StatusInfo.build_status(
        29,
        b'1 BD OPENED OK WITH ID "2341"',
        parse_code=True,
    )
    assert status.status == StatusServerCode.OK
    assert status.code == 1
    assert status.payload == b'BD OPENED WITH ID "2341"'
    assert status.message == 'BD OPENED WITH ID "2341"'

    # test FAILED
    status = StatusInfo.build_status(30, b'FAILED 5: a lot of info before')
    assert status.status == StatusServerCode.FAILED
    assert status.message == 'a lot of info before'
    assert status.code == 5
    assert status.payload == b'a lot of info before'

    # test FAILED (with initial parse code)
    status = StatusInfo.build_status(
        33,
        b'4 FAILED CLOSE BD DOES NOT EXISTS',
        parse_code=True,
    )
    assert status.status == StatusServerCode.FAILED
    assert status.message == 'CLOSE BD DOES NOT EXISTS'
    assert status.code == 4
    assert status.payload == b'CLOSE BD DOES NOT EXISTS'

    # test RAW MESSAGE
    status = StatusInfo.build_status(38, b'A lot of info whitout header or status')
    assert status.status == StatusServerCode.UNKNOWN
    assert status.message == 'A lot of info whitout header or status'
    assert status.code == 38
    assert status.payload == b'A lot of info whitout header or status'


@pytest.mark.run(order=6)
def test_status_info_parse():
    """Test for status_info parse function"""

    # test OK
    status = StatusInfo.parse('OK')
    assert status.status == StatusServerCode.OK
    assert status.code == 0
    assert status.message == ''
    assert status.payload == b''
    # test FAILED
    status = StatusInfo.parse('FAILED 5: a lot of info before')
    assert status.status == StatusServerCode.FAILED
    assert status.message == 'a lot of info before'
    assert status.code == 5
    assert status.payload == b''

    # test RAW MESSAGE
    status = StatusInfo.parse(
        'A lot of info whitout header or status', payload=b'A payload'
    )
    assert status.status == StatusServerCode.UNKNOWN
    assert status.message == 'A lot of info whitout header or status'
    assert status.code == 38
    assert status.payload == b'A payload'
