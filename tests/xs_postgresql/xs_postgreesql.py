import os
from collections import namedtuple

import pytest
from dotenv import load_dotenv
from tfprotocol_client.extensions.xs_postgresql import XSPostgreSQL

load_dotenv()

PostgreeSQLData = namedtuple('PostgreSQLData', 'host port user password database')


@pytest.fixture(scope='module')
def postgresql_info() -> PostgreeSQLData:
    addr = os.getenv('POSTGRE_HOST', 'localhost')
    port = int(os.getenv('POSTGRE_PORT', '5432'))
    database = os.getenv('POSTGRE_DATABASE', 'test')
    user = os.getenv('POSTGRE_USER', 'test')
    password = os.getenv('POSTGRE_PASSWORD', 'test')
    #
    return PostgreeSQLData(addr, port, user, password, database)


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
