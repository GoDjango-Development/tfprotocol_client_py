from typing import Union
from multipledispatch import dispatch
from tfprotocol_client.extensions.xs_sql_super import XSSQLSuper
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


class XSPostgreSQL(XSSQLSuper):
    """Tranference Protocol API extension for POSTGRESQL.
    `XSSQLSuper`: The Abstract mother class of XS SQL like modules.
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
        """Constructor for POSTGRESQL class.

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

    def xspostgresql_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Makes the server enter the subsystem. Once inside the subsystem, the server remains
        there until the client explicitly exits the module with the proper commands. If this
        module is not implemented by the server, it will return UNKNOWN. Otherwise the eXtended
        Subsystem POSTGRESQL will start listening for commands.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate('XS_POSTGRESQL'))

    def open_command(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        db_name: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Opens a database in the host indicated by the first parameter. The “port” parameter is
        the port in which the mysql server is listening. The “user” “password” parameters are
        used to authenticate the user in the server database. The “db_name” parameter is used to
        identify the desired database among all others. If the command succeeds the ID returned in
        “ID” will represent that particular opened/created database.

        Args:
            `host` (str): The host where to opens the database.
            `port` (int): The port in which mysql server is listening.
            `user` (str): The user to authenticate in the server database.
            `password` (str): The password to authenticate in the server database.
            `db_name` (str): The name used to identify the desired database amon all others.
            `response_handler` (ResponseHandler): The function to handle the command response.

        Returns:
            Optional[str]: The ID of the opened database.
        """
        resp: StatusInfo = self.client.translate(
            TfProtocolMessage(
                'OPEN',
                host,
                str(port),
                user,
                password,
                db_name,
                header_size=LONG_SIZE,
            ),
            parse_front_code_response=True,
        )
        response_handler(resp)
        if resp.status == StatusServerCode.OK:
            return resp.message.split()[-1]
