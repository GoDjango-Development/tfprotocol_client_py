# coded by lagcleaner
# email: lagcleaner@gmail.com

from tfprotocol_client.misc.parse_utils import (
    isnumber,
    separate_status,
    separate_status_b,
    separate_status_codenumber,
    separate_status_codenumber_b,
    tryparse_int,
)
from tfprotocol_client.models.status_server_code import StatusServerCode


def test_parse_utils():
    """Test for parse_utils"""
    assert (separate_status('FAILED 5: a lot of info before')) == (
        StatusServerCode.FAILED,
        '5: a lot of info before',
    )
    assert (separate_status('OK')) == (StatusServerCode.OK, '')

    assert (separate_status_b(b'FAILED 5: a lot of info before')) == (
        StatusServerCode.FAILED,
        b'5: a lot of info before',
    )
    assert (separate_status_b(b'OK')) == (StatusServerCode.OK, b'')

    assert (separate_status_codenumber('5: a lot of info before')) == (
        '5',
        ': a lot of info before',
    )
    assert (separate_status_codenumber('OK')) == ('', 'OK')

    assert (separate_status_codenumber_b(b'5: a lot of info before')) == (
        b'5',
        b': a lot of info before',
    )
    assert (separate_status_codenumber_b(b'OK')) == (b'', b'OK')

    assert tryparse_int('123') == 123
    assert tryparse_int(b'123') == 123
    assert tryparse_int(b'123d', dflt_value=2) == 2
    assert tryparse_int(bytearray(b'123')) == 123
    assert not isnumber(b'123s')
