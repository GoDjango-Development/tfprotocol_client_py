""" Transfer Protocol API Base implementation. """
import datetime as dt
from typing import Union
from multipledispatch import dispatch
from tfprotocol_client.handlers.super_proto_handler import SuperProtoHandler
from tfprotocol_client.handlers.proto_handler import TfProtoHandler
from tfprotocol_client.misc.constants import DFLT_MAX_BUFFER_SIZE, KEY_LEN_INTERVAL
from tfprotocol_client.misc.file_stat import FileStat, FileStatTypeEnum
from tfprotocol_client.misc.status_server_code import StatusServerCode
from tfprotocol_client.models.exceptions import TfException
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.tfprotocol_super import TfProtocolSuper


class TfProtocol(TfProtocolSuper):
    """ Tranference Protocol API easy to use.
        `TfProtocolSuper`: The Abstract mother class of Tranference Protocol API.
    """

    # pylint: disable=super-init-not-called
    @dispatch(SuperProtoHandler, protocol_handler=SuperProtoHandler)
    def __init__(
        self, tfprotocol: SuperProtoHandler, protocol_handler: TfProtoHandler = None,
    ) -> None:
        """ Constructor for Transfer Protocol class.

        Args:
            `tfprotocol` (TfProtocol): A created transfer protocol instance.
            `protocol_handler` (SuperProtoHandler): The instance of
                the command handler which must extends from ISuperCallback.
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
        protocol_handler: TfProtoHandler,
        address: str,
        port: int,
        proxy: ProxyOptions = None,
        keylen: int = KEY_LEN_INTERVAL[0],
        channel_len: int = DFLT_MAX_BUFFER_SIZE,
    ) -> None:
        """ Constructor for Transfer Protocol class.

        Args:
            `protocol_handler` (SuperProtoHandler): The instance of
                the command handler which must extends from ISuperCallback.
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

    @property
    def protocol_handler(self) -> TfProtoHandler:
        """ Gets the protocol handler used.

        Returns:
            TfProtoHandler: `protocol_handler`.
        """
        return self._protocol_handler

    @protocol_handler.setter
    def set_protocol_handler(self, handler: TfProtoHandler):
        self._protocol_handler = handler

    def freesp_command(self):
        """Retrieves the available space in the partition where the protocol folder is located.
        This command should be used only after a failure to find out if such a failure is due
        to the lack of space. It should not be used to guess how much space remains, and then
        proceed with a writing operation. The described scenario could potentially lead to a race
        condition. If both clients at the same time retrieve the free space and then write
        according to that value, one of them will fail.
        """
        self.protocol_handler.freesp_callback(self.client.translate('FREESP'))

    def udate_command(self):
        """Returns the number of elapsed seconds and microseconds since the epoch -separated by
        dot-, and arbitrary point in the time continuum, which is the Gregorian calendar time
        Jan 1 1970 00:00 UTC.
        """
        self.protocol_handler.udate_callback(self.client.translate('UDATE'))

    def ndate_command(self):
        """Returns the number of elapsed seconds and nanoseconds since the epoch -separated by dot-,
        and arbitrary point in the time continuum, which is the Gregorian calendar time
        Jan 1 1970 00:00 UTC.
        """
        self.protocol_handler.ndate_callback(self.client.translate('NDATE'))

    def echo_command(self, value: str):
        """Command is for debug propose. Once sent the server replays back the exact same thing
        the client sent, including the ECHO word.

        Args:
            `value` (str): The string that is going to be echoed.
        """
        self.protocol_handler.echo_callback(
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
        self.protocol_handler.mkdir_callback(
            self.client.translate(TfProtocolMessage('MKDIR', path))
        )

    def del_command(self, path: str):
        """Command deletes the specified file. This is a special command because is the only
        one who can operate in a locked directory. If it is the case, then DEL can only delete
        exactly one file: The locking file.

        Args:
            `path` (str): The target file that is going to be deleted.
        """
        self.protocol_handler.del_callback(
            self.client.translate(TfProtocolMessage('DEL', path))
        )

    def rmdir_command(self, path: str):
        """Removes a specified directory recursively.

        Args:
            `path` (str): The path of the directory that is going to be deleted.
        """
        self.protocol_handler.rmdir_callback(
            self.client.translate(TfProtocolMessage('RMDIR', path))
        )

    def copy_command(self, path_from: str, path_to: str):
        """Copy the file indicated by the first parameter of the command to the file indicated
        by the second one.

        Args:
            `path_from` (str): The source file that is going to be copied.
            `path_to` (str): The destiny file where the file of "pathFrom" is going to be copied.
        """
        self.protocol_handler.copy_callback(
            self.client.translate(TfProtocolMessage('COPY', path_from, "|", path_to))
        )

    def touch_command(self, path: str):
        """Creates a new file in the specified directory.

        Args:
            `path` (str): The path to the file to be created.
        """
        self.protocol_handler.touch_callback(
            self.client.translate(TfProtocolMessage('TOUCH', path))
        )

    def date_command(self):
        """Returns the number of elapsed seconds since the epoch, and arbitrary point
        in the time continuum, which is the Gregorian calendar time Jan 1 1970 00:00 UTC.
        """
        response = self.client.translate(TfProtocolMessage('DATE'))
        self.protocol_handler.date_callback(int(response.message), response)

    def datef_command(self):
        """Returns the current date of the server in human-readable format
        “yyyy-mm-dd HH:MM:SS” UTC.
        """
        response = self.client.translate(TfProtocolMessage('DATEF'))
        try:
            date = dt.datetime.strptime(response.message, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            raise TfException(exception=e)
        self.protocol_handler.datef_callback(date, response)

    @dispatch((int, float))
    def dtof_command(self, timestamp: int):
        """Converts date in Unix timestamp format -seconds since the epoch-
        in human-readable format “yyyy-mm-dd HH:MM:SS” UTC.

        Args:
            `timestamp` (int,float): The timestamp to be converted to human-readable string.
        """
        response = self.client.translate(TfProtocolMessage('DTOF', str(int(timestamp))))
        try:
            date = dt.datetime.strptime(response.message, '%Y-%m-%d %H:%M:%S')
            self.protocol_handler.dtof_callback(date, response)
        except ValueError as e:
            raise TfException(exception=e)

    @dispatch(str)
    def dtof_command(self, timestamp: str):
        """Converts date in Unix timestamp format -seconds since the epoch-
        in human-readable format “yyyy-mm-dd HH:MM:SS” UTC.

        Args:
            `timestamp` (str): The timestamp to be converted to human-readable string.
        """
        try:
            self.dtof_command(int(float(timestamp)))
        except ValueError as e:
            raise TfException(exception=e)

    def ftod_command(self, formatter: str):
        """Converts date in human-readable format “ yyyy-mm-dd HH:MM:SS” to its Unix
        timestamp format.

        Args:
            `formatter` (str): The date in human-readable format.
        """

        get_time_value = dt.datetime.now() - dt.datetime(1970, 1, 1)
        timestamp = int(get_time_value.total_seconds() * 1000)

        self.protocol_handler.ftod_callback(
            timestamp, self.client.translate(TfProtocolMessage('FTOD', formatter)),
        )

    def fstat_command(self, path: str):
        """Returns statistics of a file or directory in the form "D | F | U FILE-SIZE
        LAST-ACCESS LAST-MODIFICATION" where D stands for directory; F stands for file;
        and U stands for unknown, only one of them is reported. The “FILE-SIZE” is
        reported in bytes in a integer of 64 bits and the number could be up to 20 digits
        long. The “LAST-ACCESS” and “LAST-MODIFICATION” are both timestamps.

        Args:
            `path` (str): The path to the target.
        """
        response = self.client.translate(TfProtocolMessage('FSTAT', path))
        if response.status is StatusServerCode.OK:
            raw_filestat = response.message.split(' ')
            self.protocol_handler.fstat_callback(
                FileStat(
                    raw_filestat[0][0],
                    int(raw_filestat[1]),
                    int(raw_filestat[2]),
                    int(raw_filestat[3]),
                    # TODO: Check if these integers come as strings or encoded in little-endian.
                ),
                response,
            )
        else:
            self.protocol_handler.fstat_callback(
                FileStat(FileStatTypeEnum.UNKNOWN, 0, 0, 0), response,
            )

    def fupb_command(self, path: str):
        """Update the timestamps of the file or directory to server current time.

        Args:
            `path` (str): The path to the target which timestamp is going to be updated.
        """
        self.protocol_handler.fupd_callback(
            self.client.translate(TfProtocolMessage('FUPB', path))
        )

    def cpdir_command(self, path_from: str, path_to: str):
        """Copy recursively the source directory into a new created directory specified in
        the second parameter of the command.

        Args:
            `path_from` (str): The source target directory.
            `path_to` (str): The destiny target directory.
        """
        self.protocol_handler.cpdir_callback(
            self.client.translate(TfProtocolMessage('CPDIR', path_from, '|', path_to))
        )

    def xcopy_command(self, new_name: str, path: str, pattern: str):
        """Copies the source file specified in the second parameter into every directory
        in the tree that matches “pattern” with the name “newname” specified in the first
        parameter. This is a best-effort command instead of super-reliable one. If any one of
        the destinations are locked or the file exists instead of return afailed status code,
        XCOPY skips it silently. The return status of this command are relative to the source
        file/directory.

        Args:
            `new_name` (str): The new name for the copied file.
            `path` (str): The target source file.
            `pattern` (str): The pattern that specified where to copy the target source file.
        """
        self.protocol_handler.xcopy_callback(
            self.client.translate(
                TfProtocolMessage('XCOPY', new_name, path, "|", pattern)
            )
        )

    def xdel_command(self, path: str, file_name: str):
        """Deletes all files that match “filename” in the specified path at first parameter,
        and it does recursively start at the specified directory. This is a best-effort
        command instead of super-reliable one. If any one of the path are locked or even
        and error occurs, instead of return a failure return status, XDEL skips it silently.
        The return status of this command are relative to the path specified

        Args:
            `path` (str): The parent folder where the protocol is going to search for the files.
            `file_name` (str): The file name that you want to erase.
        """
        self.protocol_handler.xdel_callback(
            self.client.translate(TfProtocolMessage('XDEL', path, file_name))
        )

    def xrmdir_command(self, path: str, directory_name: str):
        """Deletes all directories recursively that match “directory-name” starting at
        the specified path at first parameter. This is a best-effort command instead of
        super-reliable one. If any one of the path are locked or even an error occurs,
        instead of return a failure return status, XRMDIR skips it silently. The return
        status of this command are relative to the path specified.

        Args:
            `path` (str): The top parent path, the protocol is going to search inside it
                for directoryName.
            `directory_name` (str): The name of the directories to be deleted.
        """
        self.protocol_handler.xrmdir_callback(
            self.client.translate(TfProtocolMessage('XRMDIR', path, directory_name))
        )

    def xcpdir_command(self, new_directory: str, path: str, destination_pattern: str):
        """Copy recursively source directory specified in the second parameter to every directory
        in the tree that matches “destination-directory-pattern” with the name “new-directory-name”
        specified at first parameter. This is a best-effort command instead of super-reliable one.
        If any one of the destinations are locked or the directory or file exists, instead of
        return a failure return code, XCPDIR skips it silently. The return status of this command
        are relative to the source file/directory

        Args:
            `new_directory` (str): The new name of the directory that will be created at
                specified location which is going be really the folder target specified
                at the path with a new name.
            `path` (str): The target folder that is going to be copied.
            `destination_pattern` (str): The pattern that is going to be used for selecting
                the folders.
        """
        self.protocol_handler.xcpdir_callback(
            self.client.translate(
                TfProtocolMessage(
                    'XCPDIR', new_directory, path, '|', destination_pattern,
                )
            )
        )

    def lock_command(self, lock_filename: str):
        """Specifies a filename that when it exists in a directory no operation can be done on it,
        except to delete the lock file. This allows a temporary blocking of a directory for any
        sort of operations except the one eliminating the locking file which is the command DEL
        with the path to the locking file. The above statement does not apply for commands that
        do not specify “FAILED 30” as possible return status.

        Args:
            lock_filename (str): The name of the file who locks directories.
        """
        self.protocol_handler.lock_callback(
            self.client.translate(TfProtocolMessage('LOCK', lock_filename))
        )

    @dispatch(bool, str, StatusInfo, (bytes, bytearray))
    def sendfile_command(
        self,
        is_overriten: bool,
        path: str,
        _: StatusInfo,
        payload: Union[bytes, bytearray],
    ):
        """DEPRECATED
        """
        # pylint: disable=no-value-for-parameter
        self.sendfile_command(is_overriten, path, payload)

    @dispatch(bool, str, (bytes, bytearray))
    def sendfile_command(
        self, is_overriten: bool, path: str, payload: Union[bytes, bytearray],
    ):
        """Sends a file to the server.

        Args:
            `is_overriten` (bool):  The first parameter could be either “0” for false or “1”
                for true. If “/path/to/filename” it exists in the server, this flag indicates
                whether it should be overwritten or not.
            `path` (str): The path in the server where the file be stored.
            `payload` (Union[bytes, bytearray]): The data of the file to be sent.
        """

    def rcvfile_command(self):
        pass

    def ls_command(self):
        pass

    def renam_command(self):
        pass

    def keepalive_command(self):
        pass

    def login_command(self):
        pass

    def chmod_command(self):
        pass

    def chown_command(self):
        pass

    def getcan_command(self):
        pass

    def putcan_command(self):
        pass

    def sha256_command(self):
        pass

    def prockey_command(self):
        pass

    def freesp_command(self):
        pass

    def udate_command(self):
        pass

    def ndate_command(self):
        pass

    def getwrite_command(self):
        pass

    def getread_command(self):
        pass

    def put_command(self):
        pass

    def putstatus_command(self):
        pass

    def nigma_command(self):
        pass

    def rmsecuredirectory_command(self):
        pass

    def injail_command(self):
        pass

    def tlb_command(self):
        pass

    def sdown_command(self):
        pass

    def sup_command(self):
        pass

    def fsize_command(self):
        pass

    def fsizels_command(self):
        pass
