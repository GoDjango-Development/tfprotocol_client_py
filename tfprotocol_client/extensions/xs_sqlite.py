from typing import Callable, Union
from multipledispatch import dispatch
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol_super import TfProtocolSuper
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.misc.handlers_aliases import (
    ResponseHandler,
)
from tfprotocol_client.misc.constants import (
    DFLT_MAX_BUFFER_SIZE,
    EMPTY_HANDLER,
    KEY_LEN_INTERVAL,
    LONG_SIZE,
)
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo


class XSSQLite(TfProtocolSuper):
    """Tranference Protocol API extension for SQLite.
    `TfProtocolSuper`: The Abstract mother class of Tranference Protocol API.
    """

    # pylint: disable=super-init-not-called
    @dispatch(TfProtocolSuper, verbosity_mode=False)
    def __init__(
        self,
        tfprotocol: TfProtocolSuper,
        verbosity_mode: bool = False,
        **_,
    ) -> None:
        """Constructor for Transfer Protocol extended subsystem.

        Args:
            `tfprotocol` (TfProtocolSuper): A created transfer protocol instance.
            `verbosity_mode` (bool): Debug mode enabled for verbosity.
        """
        self._proto_client = tfprotocol._proto_client
        self.verbosity_mode = verbosity_mode

    # pylint: disable=function-redefined
    @dispatch(
        str,
        str,
        (str, bytes),
        str,
        int,
        proxy=ProxyOptions,
        keylen=int,
        channel_len=int,
        verbosity_mode=bool,
    )
    def __init__(
        self,
        protocol_version: str,
        public_key: str,
        client_hash: Union[str, bytes],
        address: str,
        port: int,
        proxy: ProxyOptions = None,
        keylen: int = KEY_LEN_INTERVAL[0],
        channel_len: int = DFLT_MAX_BUFFER_SIZE,
        verbosity_mode=False,
        **_,
    ) -> None:
        """Constructor for XSSQLite class.

        Args:
            `protocol_version` (str, optional): The desired version of the protocol.
            `public_key` (str, optional): The previous shared rsa public key for
                the initial encryptation of the communication.
            `client_hash` (Union[str, optional, bytes]): The hash to be used by
                the server in order to test the integrity of the communication.
            `address` (str, optional): The ip/address where the protocol server is running.
            `port` (int, optional): The TCP port where the protocol is listening.
            `proxy` (ProxyOptions, optional): The proxy address for
                connect through a proxy, proxy auth. Defaults to None.
            `keylen` (int, optional): The desired length for the session key
                used to encrypt communication whit the server. Defaults to KEY_LEN_INTERVAL[0].
            `channel_len` (int, optional): The length of the channel.
                Defaults to DFLT_MAX_BUFFER_SIZE.
            `verbosity_mode` (bool): Debug mode enabled for verbosity.
        """
        super().__init__(
            protocol_version,
            public_key,
            client_hash,
            address,
            port,
            proxy,
            keylen,
            channel_len,
            verbosity_mode=verbosity_mode,
        )

    def xssqlite_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Makes the server enter the subsystem. Once inside the subsystem, the server remains
        there until the client explicitly exits the module with the proper commands. If this
        module is not implemented by the server, it will return UNKNOWN. Otherwise the eXtended
        Subsystem SQLITE will start listening for commands.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        # FIXME: HEADER_SIZE NOT SPECIFIED IN DOCUMENTATION
        response_handler(self.client.translate('XS_SQLITE'))

    # TODO: implements `with tf.open_command():` sintax
    def open_command(
        self,
        path_to_db: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Opens a database in the path indicated by the first parameter. If the database
        already exist, then OPEN will open it. If the database does not exist, OPEN will
        create it. Note that there is a whitespace between OPEN and the first parameter.
        If the command succeeds the ID returned in “ID” will represent that particular
        opened/created database.

        If the first parameter instead of using a path, is set like :memory: the database
        will be created in memory. This kind of database is not persistent.

        Args:
            `path_to_db` (str): Path to the database.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('OPEN', path_to_db, header_size=LONG_SIZE),
                parse_front_code_response=True,
            )
        )

    def close_command(
        self,
        db_id: Union[int, str],
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Closes the database represented by the handle “DB-ID”. This frees that handle to be
        reused in next openings.

        Args:
            `db_id` (int,str): The ID of the database to be closed.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('CLOSE', str(db_id), header_size=LONG_SIZE),
                parse_front_code_response=True,
            )
        )

    def exec_command(
        self,
        db_id: Union[int, str],
        sql_query: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
        rows_handler: Callable[[list], None] = EMPTY_HANDLER,
    ):
        """Executes an SQL-Query in the database represented by the specified handle in “DB-ID”.

        Args:
            `db_id` (int, str): The ID of the database to execute the query.
            `sql_query` (str): The SQL query to be executed.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        resp: StatusInfo = self.client.translate(
            TfProtocolMessage('EXEC', str(db_id), sql_query, header_size=LONG_SIZE),
            parse_front_code_response=True,
        )
        response_handler(resp)
        if resp.status != StatusServerCode.OK:
            return
        header = -1
        while True:
            header = self.client.just_recv_int(size=LONG_SIZE)
            if header <= 0:
                break
            data = self.client.just_recv(size=header)
            rows_handler(data.split(b'@@'))

    def execof_command(
        self,
        path_to_file: str,
        db_id: Union[int, str],
        sql_query: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Executes an SQL-Query in the database represented by the specified handle in “DB-ID”.
        The result of the query is stored in the file indicated in the first parameter.

        Args:
            `path_to_file` (str): The file where result of query is stored.
            `db_id` (int, str): The ID of the database to execute the query.
            `sql_query` (str): The SQL query to be executed.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage(
                    'EXECOF', path_to_file, str(db_id), sql_query, header_size=LONG_SIZE
                ),
                parse_front_code_response=True,
            )
        )

    def lastrowid_command(
        self,
        db_id: Union[int, str],
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Returns the last row id of the actual queried table in the database represented by the
        handle “DB-ID”.

        Args:
            `db_id` (int, str): The ID of the database to execute the query.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('LASTROWID', str(db_id), header_size=LONG_SIZE),
                parse_front_code_response=True,
            )
        )

    def softheap_command(
        self, size: int, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Sets the soft heap limit for the SQLITE engine.

        Args:
            `size` (int): The size of the soft heap limit, a 64bit signed integer.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('SOFTHEAP', str(size), header_size=LONG_SIZE),
                parse_front_code_response=True,
            )
        )

    def hardheap_command(
        self, size: int, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Sets the hard heap limit for the SQLITE engine.

        Args:
            `size` (int): The size of the hard heap limit, a 64bit signed integer.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('HARDHEAP', str(size), header_size=LONG_SIZE),
                parse_front_code_response=True,
            )
        )

    def blobin_command(
        self, db_id: Union[int, str], bd_table: str, filename: str, filepath: str
    ):
        """Stores in the database represented by the handle “BD-ID” a file read from “FILEPATH”
        which name will be “FILENAME” the table “DB-TABLE”.

        Args:
            `db_id` (int, str): The ID of the database to execute the command.
            `bd_table` (str): The database table to store the file.
            `filename` (str): The name of the file to store.
            `filepath` (str): The path to the file to store.
        """
        self.client.translate(
            TfProtocolMessage(
                'BLOBIN',
                str(db_id),
                bd_table,
                filename,
                filepath,
                header_size=LONG_SIZE,
            ),
            parse_front_code_response=True,
        )

    def blobout_command(
        self, db_id: Union[int, str], bd_table: str, filename: str, filepath: str
    ):
        """Extracts from the database represented by the handle “BD-ID” a file which name is
        “FILENAME” from the table “DB-TABLE” to a file written to “FILEPATH”.

        Args:
            `db_id` (int, str): The ID of the database to execute the command.
            `bd_table` (str): The database table to extract the file.
            `filename` (str): The name of the file to extract.
            `filepath` (str): The path to the file to extract.
        """
        self.client.translate(
            TfProtocolMessage(
                'BLOBOUT',
                str(db_id),
                bd_table,
                filename,
                filepath,
                header_size=LONG_SIZE,
            ),
            parse_front_code_response=True,
        )

    def exit_command(self):
        """Exits the XS_SQLITE module without freeing the previously allocated resources. This is,
        every opened database will remain as such and the returned handles, valid. However, you are
        now at the main command interface of the TF PROTOCOL.

        If you want enter again the SQLITE subsystem, you can use the XS_SQLITE command again.
        """
        self.client.send(
            TfProtocolMessage('EXIT', header_size=LONG_SIZE),
        )

    def terminate_command(self):
        """Exits the XS_SQLITE module, unlike EXIT command, freeing the previously allocated
        resources. This is, every opened database will be closed and every handle unallocated.

        Now you are in the main command interface of the TF PROTOCOL. You may enter the subsystem
        again by using the XS_SQLITE command.
        """
        self.client.send('TERMINATE', header_size=LONG_SIZE)