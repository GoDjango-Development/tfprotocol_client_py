from typing import Callable, Union
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


class XSSQLSuper(TfProtocolSuper):
    """Tranference Protocol API extension base class for SQL like extensions.
    `TfProtocolSuper`: The Abstract mother class of Tranference Protocol API.
    """

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
        """Constructor for XS_SQL like classes.

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

    def exit_command(self):
        """Exits the XS_SQL like module without freeing the previously allocated resources. This is,
        every opened database will remain as such and the returned handles, valid. However, you are
        now at the main command interface of the TF PROTOCOL.

        If you want enter again the SQLITE subsystem, you can use the XS_SQL like command again.
        """
        self.client.send(
            TfProtocolMessage('EXIT', header_size=LONG_SIZE),
        )

    def terminate_command(self):
        """Exits the XS_SQL like module, unlike EXIT command, freeing the previously allocated
        resources. This is, every opened database will be closed and every handle unallocated.

        Now you are in the main command interface of the TF PROTOCOL. You may enter the subsystem
        again by using the XS_SQL like command.
        """
        self.client.send('TERMINATE', header_size=LONG_SIZE)
