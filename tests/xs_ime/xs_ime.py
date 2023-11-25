import os
from collections import namedtuple
from typing import Tuple

import pytest
from dotenv import load_dotenv
from tfprotocol_client.extensions.xs_ime import XSIme

load_dotenv()



#@pytest.fixture(scope='module')
def xsime_instance()->XSIme:
    PROTO_VERSION = os.environ.get('PROTO_VERSION', '2.4.1')
    PROTO_PUBLIC_KEY = os.environ.get('PROTO_PUBLIC_KEY',"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3B7iLfTJ/Lkfgz9/Mq6n
3tBWNaP/818mcEyA5phFv1wyBk9hkroXGX0/J/unxRGF1ax3etNEbN1RASTcZNKT
zeEcwC0yf5Mn+6hmZDOIiDqr1pSAPyNm1soiY3V27/bUhcX0rnCql5Mb7QlfkbK6
o4CddL8pOG99tlSFaTYoXWgUhK5DXF1xptlz0DHv9STuNkukuy+LmAHTJYks1B/w
BC7CZyTtg4VPbHJ11VYXWI6dLTmOuoaTDrJGc/mGOK86zPOchgnAeYekwtBWlk/N
59VtaAWcfgzYnDET45qidcQfF+TIXxjf386igq8rlWTI0+Rh0e/GlYEpRp2YJPMC
AwIDAQAB
-----END PUBLIC KEY-----""")
    PROTO_CLIENT_HASH = os.environ.get('PROTO_CLIENT_HASH', 'testhash')
    PROTO_SERVER_ADDRESS = os.environ.get(
        'PROTO_SERVER_ADDRESS', 'tfproto.expresscuba.com'
    )
    PROTO_SERVER_PORT = int(os.environ.get('PROTO_SERVER_PORT', 10345))

    tfproto = XSIme(
        PROTO_VERSION,
        PROTO_PUBLIC_KEY,
        PROTO_CLIENT_HASH,
        PROTO_SERVER_ADDRESS,
        PROTO_SERVER_PORT,
    )
    tfproto.connect()
    return tfproto
    # yield tfproto
    
    
    # tfproto.disconnect()
