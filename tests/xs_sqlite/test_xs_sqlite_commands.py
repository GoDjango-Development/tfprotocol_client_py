# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name


from typing import List, Tuple

import pytest
from tfprotocol_client.extensions.xs_sqlite import XSSQLite
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol import Date, TfProtocol

# pylint: disable=unused-import
from .xs_sqlite import xssqlite_instance


@pytest.mark.depends(name='xssqlite')
def test_xssqlite_command(xssqlite_instance: XSSQLite):
    """Test for xs_sqlite command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # XS_SQLITE command
    tfproto.xssqlite_command(response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]
    # assert resps[0].status in (StatusServerCode.OK, StatusServerCode.UNKNOWN), resps[0]


@pytest.mark.depends(name='sqlite-open-close', on=['xssqlite'])
def test_xssqlite_open_close_commands(xssqlite_instance: XSSQLite):
    """Test for open and close commands."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # OPEN command
    tfproto.open_command('py_test.db', response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    db_id = resps[-1].message.split()[-1]
    # CLOSE command
    tfproto.close_command(db_id, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]


@pytest.mark.depends(name='sqlite-exec', on=['xssqlite', 'sqlite-open-close'])
def test_xssqlite_exec_command(xssqlite_instance: XSSQLite):
    """Test for exec command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    tfproto.open_command('py_test.db', response_handler=resps.append)
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
