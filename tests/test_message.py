# coded by lagcleaner
# email: lagcleaner@gmail.com

from tfprotocol_client.misc.constants import LONG_SIZE
from tfprotocol_client.models.message import TfProtocolMessage


def test_message():
    """Test for message"""
    # test1
    msg = TfProtocolMessage(
        b'payload',
        'arg1',
        'arg2',
        3,
        custom_header=-1,
        header_signed=True,
    )
    header, payload = msg
    assert header == b'\xff\xff\xff\xff'
    assert payload == b'payload arg1 arg2 \x00\x00\x00\x03'

    # test2
    msg = (
        TfProtocolMessage('COMMAND', header_size=8)
        .add('_ARG1')
        .add('_ARG2_')
        .add(3, size=LONG_SIZE)
    )
    assert msg.payload == b'COMMAND_ARG1_ARG2_\x00\x00\x00\x00\x00\x00\x00\x03'
    assert msg.header == b'\x00\x00\x00\x00\x00\x00\x00\x1a'
