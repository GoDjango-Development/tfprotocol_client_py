# coded by lagcleaner
# email: lagcleaner@gmail.com

import pytest
from tfprotocol_client.misc.build_utils import MessageUtils


def test_encode_value():
    """Test encode_value"""
    assert MessageUtils.encode_value(1) == b'\x00\x00\x00\x01'
    assert MessageUtils.encode_value(1, signed=True) == b'\x00\x00\x00\x01'
    assert MessageUtils.encode_value(1, size=2) == b'\x00\x01'
    assert MessageUtils.encode_value(1, size=2, signed=True) == b'\x00\x01'
    with pytest.raises(Exception):
        # error: argument out of range
        MessageUtils.encode_value(-1, size=4)
    assert MessageUtils.encode_value(-1, size=4, signed=True) == b'\xff\xff\xff\xff'
    # bytes
    assert MessageUtils.encode_value(b'1') == b'1'
    # str
    assert MessageUtils.encode_value('1') == b'1'
    # object
    assert MessageUtils.encode_value(None) is None


def test_decode_value():
    """Test decode_value"""
    assert MessageUtils.decode_int(b'\x00\x00\x00\x01') == 1
    assert MessageUtils.decode_str(b'\x00\x00\x00\x01') == '\x00\x00\x00\x01'
    assert MessageUtils.decode_str(b'str', size=2) == 'str'
    assert MessageUtils.decode_int(b'\xff\xff\xff\xff', signed=True) == -1
