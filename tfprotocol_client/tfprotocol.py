from typing import Any, Optional, Tuple, Union
from multipledispatch import dispatch
from tfprotocol_client.handlers.super_proto_handler import SuperProtoHandler
from tfprotocol_client.handlers.proto_handler import TfProtoHandler
from tfprotocol_client.misc.constants import DFLT_MAX_BUFFER_SIZE, KEY_LEN_INTERVAL
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.tfprotocol_super import TfProtocolSuper


class TfProtocol(TfProtocolSuper):
    """ Tranference Protocol API easy to use.
        `TfProtocolSuper`: The Abstract mother class of Tranference Protocol API.
    """

    @dispatch(SuperProtoHandler, protocol_handler=SuperProtoHandler)
    def __init__(
        self, tfprotocol: SuperProtoHandler, protocol_handler: TfProtoHandler = None,
    ) -> None:
        """ Constructor for Transfer Protocol class.

        Args:
            `tfprotocol` (TfProtocol): A created transfer protocol instance.
            `protocol_handler` (SuperProtoHandler): The instance of
                the callback handler which must extends from ISuperCallback.
        """
        self.protocol_handler = (
            protocol_handler if protocol_handler else tfprotocol.protocol_handler
        )
        self._proto_client = tfprotocol._proto_client

    @dispatch(
        str,
        str,
        (str, bytes),
        SuperProtoHandler,
        str,
        int,
        proxy=ProxyOptions,
        keylen=int,
        channel_len=int,
    )
    def __init__(
        self,
        protocol_version: str,
        public_key: str,
        client_hash: Union[str, bytes],
        protocol_handler: SuperProtoHandler,
        address: str,
        port: int,
        proxy: ProxyOptions = None,
        keylen: int = KEY_LEN_INTERVAL[0],
        channel_len: int = DFLT_MAX_BUFFER_SIZE,
    ) -> None:
        """ Constructor for Transfer Protocol class.

        Args:
            `protocol_handler` (SuperProtoHandler): The instance of
                the callback handler which must extends from ISuperCallback.
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
        """
        super().__init__(
            protocol_version,
            public_key,
            client_hash,
            protocol_handler,
            address,
            port,
            proxy,
            keylen,
            channel_len,
        )

    def freesp_command(self):
        """Retrieves the available space in the partition where the protocol folder is located.
        This command should be used only after a failure to find out if such a failure is due
        to the lack of space. It should not be used to guess how much space remains, and then
        proceed with a writing operation. The described scenario could potentially lead to a race
        condition. If both clients at the same time retrieve the free space and then write
        according to that value, one of them will fail.
        """
        self.protocol_handler.freespCallback(self.client.translate('FREESP'))

    def udate_command(self):
        """Returns the number of elapsed seconds and microseconds since the epoch -separated by
        dot-, and arbitrary point in the time continuum, which is the Gregorian calendar time
        Jan 1 1970 00:00 UTC.
        """
        self.protocol_handler.udateCallback(self.client.translate('UDATE'))

    def ndate_command(self):
        """Returns the number of elapsed seconds and nanoseconds since the epoch -separated by dot-,
        and arbitrary point in the time continuum, which is the Gregorian calendar time
        Jan 1 1970 00:00 UTC.
        """
        self.protocol_handler.ndateCallback(self.client.translate('NDATE'))

    def echo_command(self, value: str):
        """Command is for debug propose. Once sent the server replays back the exact same thing
        the client sent, including the ECHO word.

        Args:
            `value` (str): The string that is going to be echoed.
        """
        self.protocol_handler.echoCallback(
            self.client.translate(TfProtocolMessage('ECHO', value)).message
        )

    def mkdir_command(self, path: str):
        """Command creates a directory at the specified path.
        This feature allows the creation of a kind of directory that cannot be listed with
        any command. In order to access it, the name must be known in advance. The directory
        name may contain any character, except the decimal zero “0” and the path separator
        "/", and must end with an “.sd” extension. The length of the directory name must not
        exceed 255 characters including the extension. In order to create strong secured
        directories, the following technique could be used: Combine a user ́s name with a very
        strong password and apply to them the SHA256 or any other secure hash function.
        The resulting hash must be scanned to remove or change from it any occurrence of the
        decimal zero '0' -the null character- or the path separator '/'. If the hash is converted
        to hexadecimal format -which is usual- , it is guaranteed that the resulting string
        will contain only numbers and letters. If more security is needed, this process can be
        repeated recursively.

        Args:
            `path` (str): The path to the directory that is going to be created.
        """
        self.protocol_handler.mkdirCallback(
            self.client.translate(TfProtocolMessage('MKDIR', path))
        )

    def del_command(self, path: str):
        """Command deletes the specified file. This is a special command because is the only
        one who can operate in a locked directory. If it is the case, then DEL can only delete
        exactly one file: The locking file.

        Args:
            `path` (str): The target file that is going to be deleted.
        """
        self.protocol_handler.delCallback(
            self.client.translate(TfProtocolMessage('DEL', path))
        )

    def rmdir_command(self, path: str):
        """Removes a specified directory recursively.

        Args:
            path (str): The path of the directory that is going to be deleted.
        """
