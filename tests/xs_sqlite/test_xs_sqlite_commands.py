# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=redefined-outer-name


from typing import List

import pytest
from tfprotocol_client.extensions.xs_sqlite import XSSQLite
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode

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


@pytest.mark.depends(name='sqlite_execof', on=['sqlite-exec'])
def test_xssqlite_execof_command(xssqlite_instance: XSSQLite):
    """Test for execof command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    tfproto.open_command('py_test.db', response_handler=resps.append)
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


@pytest.mark.depends(on=['sqlite-exec'])
def test_xssqlite_lastrowid_command(xssqlite_instance: XSSQLite):
    """Test for lastrowid command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    tfproto.open_command('py_test.db', response_handler=resps.append)
    db_id = resps[-1].message.split()[-1]
    # LAST_ROWID command "Failed"
    tfproto.lastrowid_command(db_id, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.FAILED, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    # LAST_ROWID command "OK"
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
    )
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
    tfproto.exec_command(db_id, '''SELECT * FROM COMPANY;''')
    tfproto.lastrowid_command(db_id, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    lastrow_id = resps[-1].message.split()[-1]
    assert lastrow_id == '3', f'lastrowid: {lastrow_id} expected: 3'
    #
    tfproto.exec_command(db_id, '''DROP TABLE COMPANY;''')
    tfproto.close_command(db_id)


@pytest.mark.depends(on=['xssqlite'])
def test_xssqlite_heapsize_commands(xssqlite_instance: XSSQLite):
    """Test for softheap and hardheap commands."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # SOFT_HEAP command
    tfproto.softheap_command(70368744177664, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]
    # HARD_HEAP command
    tfproto.hardheap_command(1844674407370955161, response_handler=resps.append)
    assert resps[-1].status == StatusServerCode.OK, resps[-1]
    assert resps[-1].message not in (None, ''), resps[-1]


@pytest.mark.depends(name='sqlite-blob', on=['sqlite-exec'])
def test_xssqlite_blob_commands(xssqlite_instance: XSSQLite):
    """Test for blobin and blobout commands."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    tfproto.open_command('py_test.db', response_handler=resps.append)
    db_id = resps[-1].message.split()[-1]
    tfproto.exec_command(db_id, '''''')
    tfproto.exec_command(
        db_id,
        '''
        DROP TABLE IF EXISTS TEST;
        CREATE TABLE TEST(
            ID INT PRIMARY KEY    NOT NULL,
            NAME         TEXT,
            DATA         BLOB
        );
        INSERT INTO TEST (ID, NAME, DATA)
        VALUES (1, 'example.txt', 12345);

        INSERT INTO TEST (ID, NAME, DATA)
        VALUES (2, 'example2.txt', NULL);
        ''',
    )
    rows: List[List[bytes]] = []
    # BLOBIN command
    tfproto.blobout_command(
        db_id,
        'TEST',
        'example.txt',
        'example_file_sqlite.txt',
    )
    tfproto.exec_command(db_id, 'SELECT * FROM TEST;', rows_handler=rows.append)
    assert rows[1][2] == b'12345', rows[1]
    assert rows[2][2] == b'NULL', rows[2]
    rows.clear()
    # BLOBOUT command
    tfproto.blobin_command(
        db_id,
        'TEST',
        'example2.txt',
        'example_file_sqlite.txt',
    )
    tfproto.exec_command(db_id, 'SELECT * FROM TEST;', rows_handler=rows.append)
    assert rows[1][2] == b'12345', rows[1]
    # assert rows[2][2] == b'12345', rows[2] # FIXME: WHY DOES NOT WORK PROPERLY
    #
    tfproto.exec_command(db_id, '''DROP TABLE TEST;''')
    tfproto.close_command(db_id)


@pytest.mark.depends(on=['xssqlite'])
def test_xssqlite_exit_command(xssqlite_instance: XSSQLite):
    """Test for exit command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # EXIT command
    tfproto.exit_command()
    tfproto.xssqlite_command(response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]


@pytest.mark.depends(on=['xssqlite'])
def test_xssqlite_terminate_command(xssqlite_instance: XSSQLite):
    """Test for terminate command."""
    tfproto = xssqlite_instance
    resps: List[StatusInfo] = []
    # TERMINATE command
    tfproto.terminate_command()
    tfproto.xssqlite_command(response_handler=resps.append)
    assert resps[0].status == StatusServerCode.OK, resps[0]
