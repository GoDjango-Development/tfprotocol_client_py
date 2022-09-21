import os
from typing import Tuple
import pytest

from dotenv import load_dotenv
from tfprotocol_client.extensions.xs_postgresql import XSPostgreSQL

load_dotenv()


@pytest.fixture(scope='module')
def postgresql_ip_port() -> Tuple[str, int]:
    PROTO_SERVER_ADDRESS = os.environ.get(
        'PROTO_SERVER_ADDRESS',
        'tfproto.expresscuba.com',
    )
    PROTO_SERVER_ADDRESS_POSTGRESQL = os.getenv(
        'PROTO_SERVER_ADDRESS_POSTGRESQL',
        PROTO_SERVER_ADDRESS,
    )
    PROTO_SERVER_PORT_POSTGRESQL = int(
        os.getenv('PROTO_SERVER_PORT_POSTGRESQL', '5432')
    )
    #
    return PROTO_SERVER_ADDRESS_POSTGRESQL, PROTO_SERVER_PORT_POSTGRESQL


@pytest.fixture(scope='module')
def xspostgresql_instance():
    PROTO_VERSION = os.environ.get('PROTO_VERSION', '0.0')
    PROTO_PUBLIC_KEY = os.environ.get('PROTO_PUBLIC_KEY')
    PROTO_CLIENT_HASH = os.environ.get('PROTO_CLIENT_HASH', 'testhash')
    PROTO_SERVER_ADDRESS = os.environ.get(
        'PROTO_SERVER_ADDRESS', 'tfproto.expresscuba.com'
    )
    PROTO_SERVER_PORT = int(os.environ.get('PROTO_SERVER_PORT', 10345))

    tfproto = XSPostgreSQL(
        PROTO_VERSION,
        PROTO_PUBLIC_KEY,
        PROTO_CLIENT_HASH,
        PROTO_SERVER_ADDRESS,
        PROTO_SERVER_PORT,
    )
    tfproto.connect()
    yield tfproto
    try:
        tfproto.terminate_command()
    except:  # pylint: disable=bare-except
        pass
    tfproto.disconnect()
