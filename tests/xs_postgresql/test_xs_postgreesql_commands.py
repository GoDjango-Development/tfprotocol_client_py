# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name


from typing import List, Tuple

import pytest
from tfprotocol_client.extensions.xs_postgresql import XSPostgreSQL
from tfprotocol_client.misc.timeout_func import TimeLimitExpired, timelimit
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode

# pylint: disable=unused-import
from .xs_postgreesql import xspostgresql_instance, postgresql_ip_port


@pytest.mark.depends(name='xspostgresql')
def test_xspostgresql_command(xspostgresql_instance: XSPostgreSQL):
    """Test for xs_sqlite command."""
    tfproto = xspostgresql_instance
    resps: List[StatusInfo] = []
    # XS_POSTGRESQL command
    tfproto.xspostgresql_command(response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]
    # assert resps[0].status in (StatusServerCode.OK, StatusServerCode.UNKNOWN), resps[0]


@pytest.mark.depends(name='postgresql-open-close', on=['xspostgresql'])
def test_xspostgresql_open_close_commands(
    xspostgresql_instance: XSPostgreSQL,
    postgresql_ip_port: Tuple[str, int],
):
    """Test for open and close commands."""
    tfproto = xspostgresql_instance
    resps: List[StatusInfo] = []
    # OPEN command
    try:
        timelimit(
            6,
            lambda *_, **__: tfproto.open_command(
                postgresql_ip_port[0],
                postgresql_ip_port[1],
                'user-pytest',
                'password-pytest',
                'pytest-db',
                response_handler=resps.append,
            ),
        )
    except TimeLimitExpired:
        assert False, 'open_command timeout, try with another (address, port) configuration.'

    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    db_id = resps[-1].message.split()[-1]
    # CLOSE command
    tfproto.close_command(db_id, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]


@pytest.mark.depends(
    name='postgresql-exec', on=['xspostgresql', 'postgresql-open-close']
)
def test_xspostgresql_exec_command(
    xspostgresql_instance: XSPostgreSQL,
    postgresql_ip_port: Tuple[str, int],
):
    """Test for exec command."""
    tfproto = xspostgresql_instance
    resps: List[StatusInfo] = []
    tfproto.open_command(
        postgresql_ip_port[0],
        postgresql_ip_port[1],
        'user-pytest',
        'password-pytest',
        'pytest-db',
        response_handler=resps.append,
    )
    db_id = resps[-1].message.split()[-1]
    # EXEC command (With no data)
    tfproto.exec_command(
        db_id,
        '''
        DROP TABLE IF EXISTS COMPANY;
        CREATE TABLE COMPANY(
            ID INT PRIMARY KEY     NOT NULL,
            NAME           TEXT    NOT NULL,
            AGE            INT     NOT NULL,
            ADDRESS        CHAR(50),
            SALARY         REAL
        );
        ''',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    tfproto.exec_command(
        db_id,
        '''
        INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
        VALUES (1, 'Paul', 32, 'California', 20000.00 );

        INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
        VALUES (2, 'Allen', 25, 'Texas', 15000.00 );

        INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
        VALUES (3, 'Teddy', 23, 'Norway', 20000.00 );
        ''',
    )
    rows: List[list] = []
    # EXEC command (With data)
    tfproto.exec_command(
        db_id,
        '''SELECT * FROM COMPANY;''',
        response_handler=resps.append,
        rows_handler=rows.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    assert len(rows) == 4, rows
    assert rows[0][0] == b'ID', rows[0]
    assert rows[1][0] == b'1', rows[1]
    #
    tfproto.exec_command(db_id, '''DROP TABLE COMPANY;''')
    tfproto.close_command(db_id)


@pytest.mark.depends(name='postgresql_execof', on=['postgresql-exec'])
def test_xspostgresql_execof_command(
    xspostgresql_instance: XSPostgreSQL,
    postgresql_ip_port: Tuple[str, int],
):
    """Test for execof command."""
    tfproto = xspostgresql_instance
    resps: List[StatusInfo] = []
    tfproto.open_command(
        postgresql_ip_port[0],
        postgresql_ip_port[1],
        'user-pytest',
        'password-pytest',
        'pytest-db',
        response_handler=resps.append,
    )
    db_id = resps[-1].message.split()[-1]
    # EXECOF command (With no data)
    tfproto.execof_command(
        'py_test_execof.output',
        db_id,
        '''
        DROP TABLE IF EXISTS COMPANY;
        CREATE TABLE COMPANY(
            ID INT PRIMARY KEY     NOT NULL,
            NAME           TEXT    NOT NULL,
            AGE            INT     NOT NULL,
            ADDRESS        CHAR(50),
            SALARY         REAL
        );
        ''',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    tfproto.execof_command(
        'py_test_execof.output',
        db_id,
        '''
        INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
        VALUES (1, 'Paul', 32, 'California', 20000.00 );

        INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
        VALUES (2, 'Allen', 25, 'Texas', 15000.00 );

        INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY)
        VALUES (3, 'Teddy', 23, 'Norway', 20000.00 );
        ''',
    )
    # EXECOF command (With data)
    tfproto.execof_command(
        'py_test_execof.output',
        db_id,
        '''SELECT * FROM COMPANY;''',
        response_handler=resps.append,
    )
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    #
    tfproto.exec_command(db_id, '''DROP TABLE COMPANY;''')
    tfproto.close_command(db_id)


@pytest.mark.depends(on=['xspostgresql'])
def test_xspostgresql_exit_command(xspostgresql_instance: XSPostgreSQL):
    """Test for exit command."""
    tfproto = xspostgresql_instance
    resps: List[StatusInfo] = []
    # EXIT command
    tfproto.exit_command()
    tfproto.xspostgresql_command(response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]


@pytest.mark.depends(on=['xspostgresql'])
def test_xspostgresql_terminate_command(xspostgresql_instance: XSPostgreSQL):
    """Test for terminate command."""
    tfproto = xspostgresql_instance
    resps: List[StatusInfo] = []
    # TERMINATE command
    tfproto.terminate_command()
    tfproto.xspostgresql_command(response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]