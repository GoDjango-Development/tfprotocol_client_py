# coded by lagcleaner
# email: lagcleaner@gmail.com


import os

import pytest
from dotenv import load_dotenv
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol_super import TfProtocolSuper

load_dotenv()


def _assert_status_is_ok(status: StatusInfo):
    assert status.status is StatusServerCode.OK, status.message


@pytest.mark.run(order=8)
def test_tfprotocol_super_connection():
    """Test for tfprotocol_super"""
    PROTO_VERSION = os.environ.get('PROTO_VERSION', '0.0')
    PROTO_PUBLIC_KEY = os.environ.get('PROTO_PUBLIC_KEY')
    PROTO_CLIENT_HASH = os.environ.get('PROTO_CLIENT_HASH', 'testhash')
    PROTO_SERVER_ADDRESS = os.environ.get(
        'PROTO_SERVER_ADDRESS', ' tfproto.expresscuba.com'
    )
    PROTO_SERVER_PORT = int(os.environ.get('PROTO_SERVER_PORT', 10345))

    assert PROTO_PUBLIC_KEY is not None, 'PROTO_PUBLIC_KEY is not set'
    tfproto = TfProtocolSuper(
        protocol_version=PROTO_VERSION,
        public_key=PROTO_PUBLIC_KEY,
        client_hash=PROTO_CLIENT_HASH,
        address=PROTO_SERVER_ADDRESS,
        port=PROTO_SERVER_PORT,
    )
    try:
        tfproto.connect(on_response=_assert_status_is_ok)
        assert tfproto.client.is_connect(), 'Connection to server failed'
    except TfException as e:
        assert False, str(e)

    tfproto.disconnect()
    assert not tfproto.client.is_connect(), 'Connection with server stills open'
