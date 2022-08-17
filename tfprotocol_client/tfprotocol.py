# coded by lagcleaner
# email: lagcleaner@gmail.com

# pylint: disable=too-many-lines
""" Transfer Protocol API Base implementation. """

import datetime as dt
import socket
from io import BytesIO
from multiprocessing import Condition
from typing import Callable, Union

from multipledispatch import dispatch

from tfprotocol_client.connection.codes_sender_recvr import CodesSenderRecvr
from tfprotocol_client.misc.build_utils import MessageUtils
from tfprotocol_client.misc.constants import (
    BYTE_SIZE,
    DFLT_MAX_BUFFER_SIZE,
    EMPTY_HANDLER,
    INT_SIZE,
    KEY_LEN_INTERVAL,
    LONG_SIZE,
)
from tfprotocol_client.misc.handlers_aliases import (
    ResponseHandler,
    SendRecvFileHandler,
    TransferAsyncHandler,
    TransferHandler,
)
from tfprotocol_client.misc.thread import TfThread
from tfprotocol_client.models.exceptions import ErrorCode, TfException
from tfprotocol_client.models.file_stat import FileStat, FileStatTypeEnum
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.putget_commands import PutGetCommandEnum
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.models.transfer_state import TransferStatus
from tfprotocol_client.tfprotocol_super import TfProtocolSuper

Date = dt.date


class TfProtocol(TfProtocolSuper):
    """Tranference Protocol API easy to use.
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
        """Constructor for Transfer Protocol class.

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
        """Constructor for Transfer Protocol class.

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

    def freesp_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Retrieves the available space in the partition where the protocol folder is located.
        This command should be used only after a failure to find out if such a failure is due
        to the lack of space. It should not be used to guess how much space remains, and then
        proceed with a writing operation. The described scenario could potentially lead to a race
        condition. If both clients at the same time retrieve the free space and then write
        according to that value, one of them will fail.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate('FREESP'))

    def udate_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Returns the number of elapsed seconds and microseconds since the epoch -separated by
        dot-, and arbitrary point in the time continuum, which is the Gregorian calendar time
        Jan 1 1970 00:00 UTC.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate('UDATE'))

    def ndate_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Returns the number of elapsed seconds and nanoseconds since the epoch -separated by dot-,
        and arbitrary point in the time continuum, which is the Gregorian calendar time
        Jan 1 1970 00:00 UTC.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate('NDATE'))

    def echo_command(
        self, value: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Command is for debug propose. Once sent the server replays back the exact same thing
        the client sent, including the ECHO word.

        Args:
            `value` (str): The string that is going to be echoed.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('ECHO', value)).message
        )

    def mkdir_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
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
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('MKDIR', path)))

    def del_command(self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Command deletes the specified file. This is a special command because is the only
        one who can operate in a locked directory. If it is the case, then DEL can only delete
        exactly one file: The locking file.

        Args:
            `path` (str): The target file that is going to be deleted.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('DEL', path)))

    def rmdir_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Removes a specified directory recursively.

        Args:
            `path` (str): The path of the directory that is going to be deleted.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('RMDIR', path)))

    def copy_command(
        self,
        path_from: str,
        path_to: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Copy the file indicated by the first parameter of the command to the file indicated
        by the second one.

        Args:
            `path_from` (str): The source file that is going to be copied.
            `path_to` (str): The destiny file where the file of "pathFrom" is going to be copied.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('COPY', path_from, "|", path_to))
        )

    def touch_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Creates a new file in the specified directory.

        Args:
            `path` (str): The path to the file to be created.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('TOUCH', path)))

    def date_command(
        self, response_handler: Callable[[int, StatusInfo], None] = EMPTY_HANDLER
    ):
        """Returns the number of elapsed seconds since the epoch, and arbitrary point
        in the time continuum, which is the Gregorian calendar time Jan 1 1970 00:00 UTC.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response = self.client.translate(TfProtocolMessage('DATE'))
        response_handler(int(response.message), response)

    def datef_command(
        self, response_handler: Callable[[Date, StatusInfo], None] = EMPTY_HANDLER
    ):
        """Returns the current date of the server in human-readable format
        “yyyy-mm-dd HH:MM:SS” UTC.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response = self.client.translate(TfProtocolMessage('DATEF'))
        try:
            date = dt.datetime.strptime(response.message, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            raise TfException(exception=e)
        response_handler(date, response)

    def dtof_command(
        self,
        timestamp: Union[int, float, str],
        response_handler: Callable[[Date, StatusInfo], None] = EMPTY_HANDLER,
    ):
        """Converts date in Unix timestamp format -seconds since the epoch-
        in human-readable format “yyyy-mm-dd HH:MM:SS” UTC.

        Args:
            `timestamp` (int,float): The timestamp to be converted to human-readable string.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        if isinstance(timestamp, (int, float)):
            timestamp = str(timestamp)

        response = self.client.translate(TfProtocolMessage('DTOF', timestamp))
        try:
            date = dt.datetime.strptime(response.message, '%Y-%m-%d %H:%M:%S')
            response_handler(date, response)
        except ValueError as e:
            raise TfException(exception=e)

    def ftod_command(
        self,
        formatted_date: str,
        response_handler: Callable[[int, StatusInfo], None] = EMPTY_HANDLER,
    ):
        """Converts date in human-readable format “ yyyy-mm-dd HH:MM:SS” to its Unix
        timestamp format.

        Args:
            `formatter` (str): The date in human-readable format.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        get_time_value = dt.datetime.now() - dt.datetime(1970, 1, 1)
        timestamp = int(get_time_value.total_seconds() * 1000)

        response_handler(
            timestamp,
            self.client.translate(TfProtocolMessage('FTOD', formatted_date)),
        )

    def fstat_command(
        self,
        path: str,
        response_handler: Callable[[FileStat, StatusInfo], None] = EMPTY_HANDLER,
    ):
        """Returns statistics of a file or directory in the form "D | F | U FILE-SIZE
        LAST-ACCESS LAST-MODIFICATION" where D stands for directory; F stands for file;
        and U stands for unknown, only one of them is reported. The “FILE-SIZE” is
        reported in bytes in a integer of 64 bits and the number could be up to 20 digits
        long. The “LAST-ACCESS” and “LAST-MODIFICATION” are both timestamps.

        Args:
            `path` (str): The path to the target.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response = self.client.translate(TfProtocolMessage('FSTAT', path))
        if response.status is StatusServerCode.OK:
            raw_filestat = response.message.split(' ')
            response_handler(
                FileStat(
                    FileStatTypeEnum.from_char(
                        raw_filestat[0][0],
                        dflt=FileStatTypeEnum.UNKNOWN,
                    ),
                    int(raw_filestat[1]),
                    int(raw_filestat[2]),
                    int(raw_filestat[3]),
                )
                if raw_filestat
                else None,
                response,
            )
        else:
            response_handler(
                FileStat(FileStatTypeEnum.UNKNOWN, 0, 0, 0),
                response,
            )

    def fupd_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Update the timestamps of the file or directory to server current time.

        Args:
            `path` (str): The path to the target which timestamp is going to be updated.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('FUPD', path)))

    def cpdir_command(
        self,
        path_from: str,
        path_to: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Copy recursively the source directory into a new created directory specified in
        the second parameter of the command.

        Args:
            `path_from` (str): The source target directory.
            `path_to` (str): The destiny target directory.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('CPDIR', path_from, '|', path_to))
        )

    def xcopy_command(
        self,
        new_name: str,
        path: str,
        pattern: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
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
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('XCOPY', new_name, path, "|", pattern)
            )
        )

    def xdel_command(
        self,
        path: str,
        file_name: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Deletes all files that match “filename” in the specified path at first parameter,
        and it does recursively start at the specified directory. This is a best-effort
        command instead of super-reliable one. If any one of the path are locked or even
        and error occurs, instead of return a failure return status, XDEL skips it silently.
        The return status of this command are relative to the path specified

        Args:
            `path` (str): The parent folder where the protocol is going to search for the files.
            `file_name` (str): The file name that you want to erase.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('XDEL', path, file_name))
        )

    def xrmdir_command(
        self,
        path: str,
        directory_name: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Deletes all directories recursively that match “directory-name” starting at
        the specified path at first parameter. This is a best-effort command instead of
        super-reliable one. If any one of the path are locked or even an error occurs,
        instead of return a failure return status, XRMDIR skips it silently. The return
        status of this command are relative to the path specified.

        Args:
            `path` (str): The top parent path, the protocol is going to search inside it
                for directoryName.
            `directory_name` (str): The name of the directories to be deleted.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('XRMDIR', path, directory_name))
        )

    def xcpdir_command(
        self,
        new_directory: str,
        path: str,
        destination_pattern: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
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
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage(
                    'XCPDIR',
                    new_directory,
                    path,
                    '|',
                    destination_pattern,
                )
            )
        )

    def lock_command(
        self,
        lock_filename: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Specifies a filename that when it exists in a directory no operation can be done on it,
        except to delete the lock file. This allows a temporary blocking of a directory for any
        sort of operations except the one eliminating the locking file which is the command DEL
        with the path to the locking file. The above statement does not apply for commands that
        do not specify “FAILED 30” as possible return status.

        Args:
            `lock_filename` (str): The name of the file who locks directories.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('LOCK', lock_filename))
        )

    def sndfile_command(
        self,
        is_overriten: bool,
        path: str,
        stream: BytesIO,
        handler: SendRecvFileHandler = EMPTY_HANDLER,
    ):
        """Sends a file to the server.

        Args:
            `is_overriten` (bool):  The first parameter could be either “0” for false or “1”
                for true. If “/path/to/filename” it exists in the server, this flag indicates
                whether it should be overwritten or not.
            `path` (str): The path in the server where the file be stored.
            `stream` (BytesIO): The data of the file to be sent.
            `handler` (SendRecvFileHandler): The function to handle receiving states.
        """
        response = self.client.translate(
            TfProtocolMessage('SNDFILE', '1' if (is_overriten) else '0', path),
        )
        handler(
            is_overriten,
            path,
            response,
            stream,
        )
        while True:
            payload = stream.read(
                self.len_channel - len(StatusServerCode.CONT.name) - 1
            )
            if (
                payload
                and len(payload) - len(StatusServerCode.CONT.name) - 1
                > self.len_channel
            ):
                # PAYLOAD_TOO_BIG [CASE]
                handler(is_overriten, path, StatusInfo.parse('PAYLOAD_TOO_BIG'), stream)
                break

            # SEND DATA IF EXIST
            if payload:
                # CONNECTION BLOCKED WHEN THE PAYLOAD SENT IS THE MAXIMUM POSSIBLE,
                # USED FOR TINY FILES ONLY
                response = self.client.translate(TfProtocolMessage('CONT', payload))
                handler(is_overriten, path, response, stream)
            else:
                break

            # BREAK IF BAD RESPONSE RECEIVED
            if response.status != StatusServerCode.CONT:
                break
        handler(is_overriten, path, self.client.translate('OK'), stream)

    def rcvfile_command(
        self,
        delete_after: bool,
        path: str,
        sink: BytesIO = None,
        handler: SendRecvFileHandler = EMPTY_HANDLER,
    ):
        """Receives a file from the server.

        Args:
            `delete_after` (bool): The first parameter could be either “0” for false or “1” for
                true and tells the server whether the file must be deleted after successfully
                received by the client.
            `path` (str): The path to the file in the server to be retrieved.
            `sink` (BytesIO): The sink to receive data in byte mode.
            `handler` (SendRecvFileHandler): The function to handle receiving states.
        """
        response = self.client.translate(
            TfProtocolMessage('RCVFILE', '1' if delete_after else '0', path)
        )
        handler(delete_after, path, response, sink)

        while True:
            response = self.client.translate(TfProtocolMessage('CONT'))
            handler(delete_after, path, response, sink)
            if response.status != StatusServerCode.CONT:
                break

    def ls_command(self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Command list the directory entries for the indicated path, if the argument is missing,
        it lists the root directory of the protocol daemon. The return value of this command
        is a file with the listed content. In fact, it is like issuing the command RCVFILE to
        a temporary file with the listed content of the directory.The file returned by LS has
        the following syntax.

        F | D | U /path/to/file-or-directory
        The F stands for “file”; the
        D for “directory” and the U for “unknown”.

        Args:
            `path` (str): The path to the folder to be listed.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response: StatusInfo = self.client.translate(TfProtocolMessage('LS', path))
        response_handler(response)

        while True:
            response = self.client.translate(TfProtocolMessage('CONT'))
            response_handler(response)
            if response.status != StatusServerCode.CONT:
                break

    def lsr_command(self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Command list the directory entries for the indicated path, if the argument is missing,
        it lists the root directory of the protocol daemon. The return value of this command
        is a file with the listed content. In fact, it is like issuing the command RCVFILE to
        a temporary file with the listed content of the directory.The file returned by LS has
        the following syntax.F | D | U /path/to/file-or-directoryThe F stands for “file”; the
        D for “directory” and the U for “unknown”.

        Args:
            `path` (str): The path to the folder to be listed.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response: StatusInfo = self.client.translate(TfProtocolMessage('LSR', path))
        response_handler(response)

        while True:
            response = self.client.translate(TfProtocolMessage('CONT'))
            response_handler(response)
            if response.status != StatusServerCode.CONT:
                break

    def renam_command(
        self,
        path_dir: str,
        dir_newname: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Renames the file or directory specified at first parameter into the name specified at
        second parameter. RENAM operates atomically; there is no instant at which “newname” is
        non-existent between the operation's steps if “newname” already exists. If a system
        crash occurs, it is possible for both names “oldname” and “newname” to still exist,
        but “newname” will be intact.RENAM has some restrictions to operate.1) “oldname” it
        must exist.2) If “newname” is a directory must be empty.3) If “oldname” is a directory
        then “newname” must not exist or it has to be an empty directory.4) The “newname”
        must not specify a subdirectory of the directory “oldname” which is being renamed.

        Args:
            `path_dir` (str): The target to be renamed.
            `dir_newname` (str): The new name for this target directory.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('RENAM', path_dir, '|', dir_newname)
            )
        )

    def keepalive_command(
        self,
        is_on: bool,
        time_connection: int,
        interval: int,
        count: int,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Sets the configuration parameters for the TCP keepalive feature. This is especially
        useful for clients behind NAT boxes. If there is some idle time in the established
        connection -no data transmission- the NAT box could close or unset the connection
        without the peers knowing it. In contexts where it is predictable that an established
        connection could be 'in silent' for long periods of time, and it is possible that
        clients are behind NAT boxes, it is necessary to set the TCP keepalive packets.

        Args:
            `is_on` (bool): The first parameter of the command could be 0 or 1, meaning on or off.
            `time_connection` (int): The second parameter is the time (in seconds) the connection
                needs to remain idle before TCP starts sending keepalive probes.
            `interval` (int): The third parameter is the time (in seconds) between individual
                keepalive probes.
            `count` (int): The fourth parameter is the maximum number of keepalive probes TCP
                should send before dropping the connection.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage(
                    'KEEPALIVE',
                    '1' if is_on else '0',
                    time_connection,
                    '|',
                    interval,
                    '|',
                    count,
                )
            )
        )

    def login_command(
        self, user: str, passw: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Login into system this is required for many others commands.

        Args:
            `user` (str): The username for the login action.
            `passw` (str): The password for the login action.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('LOGIN', user, passw)))

    def chmod_command(
        self,
        path_file: str,
        octal_mode: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Change the access modifier to a new one.

        Args:
            `path_file` (str): The location to the file to be modified.
            `octal_mode` (str): The octal modes stands for 000 or 777 etc in octal representation
                000 means not permission for owner not permission for user and nor for group
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('CHMOD', path_file, octal_mode))
        )

    def chown_command(
        self,
        path_file: str,
        user: str,
        group: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Change the owner of a file to a new one .This commands is similar to chown command
        at unix systems.

        Args:
            `path_file` (str): The location to the file.
            `user` (str): The new username who is going to owns the file.
            `group` (str): The new group for the file.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('CHOWN', path_file, user, group))
        )

    def putcan_command(
        self,
        data_stream: BytesIO,
        path_file: str,
        offset: int,
        buffer_size: int,
        canpt: int,
        response_handler: ResponseHandler = EMPTY_HANDLER,
        transfer_handler: TransferHandler = EMPTY_HANDLER,
    ):
        """Upload a file to the server.

        Args:
            `data_stream` (BytesIO): Input stream where you can read the information to
                be uploaded. Can be any object that inherits from BinaryIO in read mode.
            `path_file` (str): Path to server file to upload, if not exists creates it.
            `offset` (int): The pointer position from where to start writing to the
                server file.
            `buffer_size` (int): The size proposed by the client for the buffer, the buffer
                definitive will be sent by the server in case of OK.
            `canpt` (int): Cancellation Points, determines the cancellation points where the
                user, it will have to read from the server to know if it continues or not.
            `response_handler` (ResponseHandler): The function to handle the command response.
            `transference_handler` (TransferenceHandler): The function to handle the transference
                cancelations.
        """
        offset, canpt = max(0, offset), max(0, canpt)

        # SEND INITIAL OPTIONS
        response = self.client.translate(
            TfProtocolMessage('PUTCAN ', path_file, separate_by_spaces=False)
            .add(' ')
            .add(offset, size=LONG_SIZE, signed=False)
            .add(buffer_size, size=LONG_SIZE, signed=True)
            .add(canpt, size=LONG_SIZE, signed=False)
        )

        # INITIALIZE TRANSFER VARIABLES
        transfer_status = TransferStatus()
        header_size = LONG_SIZE
        server_buffer_size = buffer_size
        transfer_status.server_command = PutGetCommandEnum.HPFCONT.value
        if response is None or response.code != 0:
            return
        server_buffer_size = MessageUtils.decode_int(response.payload, signed=True)

        response.code = server_buffer_size
        response_handler(response)
        i = 0
        while True:
            if canpt > 0 and i == canpt:
                i = 0
                cur_header = self.client.just_recv_int(size=header_size, signed=True)
                transfer_status.server_command = None
                transfer_status.handling_canpt = True
                if cur_header == PutGetCommandEnum.HPFCANCEL.value:
                    transfer_status.server_command = PutGetCommandEnum.HPFCANCEL.value
                    transfer_handler(self.client, transfer_status)
                    break
                elif cur_header == PutGetCommandEnum.HPFCONT.value:
                    transfer_status.server_command = PutGetCommandEnum.HPFCONT.value
                    transfer_handler(self.client, transfer_status)
                else:
                    transfer_handler(self.client, transfer_status)
                    raise TfException(
                        status_server_code=StatusServerCode.FAILED,
                        code=ErrorCode.CAN_PUT,
                        message="Some error ocurred while trying to handle canpt",
                    )
                transfer_status.handling_canpt = False
                continue
            i += 1
            # LOAD DATA TO BE SENT
            payl: bytearray = None
            try:
                payl = data_stream.read(server_buffer_size)
            except Exception as e:
                raise TfException(exception=e)

            # SEND DATA CHUNK
            if payl:
                self.client.send(payl, header_size=LONG_SIZE)
            transfer_status.last_payload_size = len(payl)
            transfer_handler(self.client, transfer_status)

            # HANDLER SIGNAL (SEND HPFCANCEL or HPFSTOP)
            if transfer_status.client_command in (
                PutGetCommandEnum.HPFCANCEL.value,
                PutGetCommandEnum.HPFSTOP.value,
            ):
                self.client.just_send(
                    transfer_status.client_command, size=header_size, signed=True
                )

            # BREAK STOP THE CYCLE IF THERE IS NO DATA LEFT IN THE 'data_stream'
            try:
                if (
                    not payl
                    or transfer_status.client_command == PutGetCommandEnum.HPFEND.value
                ):
                    self.client.just_send(
                        PutGetCommandEnum.HPFEND.value,
                        size=header_size,
                        signed=True,
                    )
                    transfer_status.client_command = PutGetCommandEnum.HPFEND.value
                    transfer_handler(self.client, transfer_status)
                    break
            except IOError as e:
                raise TfException(exception=e)

    def getcan_command(
        self,
        data_sink: BytesIO,
        path_file: str,
        offset: int,
        buffer_size: int,
        canpt: int,
        response_handler: ResponseHandler = EMPTY_HANDLER,
        transfer_handler: TransferHandler = EMPTY_HANDLER,
    ):
        """Download a file from the server.

        Args:
            `data_sink` (BytesIO): Output sink where you can write the downloaded information.
                Can be any object that inherits from BinaryIO in write mode.
            `path_file` (str): Path to server file to be download.
            `offset` (int): The pointer position from where to start reading to the server file.
            `buffer_size` (int): The size proposed by the client for the buffer, the buffer
                definitive will be sent by the server in case of OK.
            `canpt` (int): Cancellation Points, determines the cancellation points where the
                user, it will have to read from the server to know if it continues or not.
            `response_handler` (ResponseHandler): The function to handle the command response.
            `transference_handler` (TransferenceHandler): The function to handle the transference
                cancelations.
        """
        offset, canpt = max(offset, 0), max(canpt, 0)
        # SEND INITIAL OPTIONS
        response = self.client.translate(
            TfProtocolMessage('GETCAN', path_file)
            .add(' ')
            .add(offset, size=LONG_SIZE, signed=False)
            .add(buffer_size, size=LONG_SIZE, signed=True)
            .add(canpt, size=LONG_SIZE, signed=False)
        )

        # INITIALIZE TRANSFER VARIABLES
        transfer_status = TransferStatus()
        header_size = LONG_SIZE
        if response is None or response.code != 0:
            return
        response.code = MessageUtils.decode_int(response.payload, signed=True)

        response_handler(response)
        i = 0
        while True:
            if canpt > 0 and i == canpt:
                i = 0
                transfer_status.client_command = PutGetCommandEnum.HPFCONT.value
                transfer_status.handling_canpt = True

                transfer_handler(self.client, transfer_status)
                if not transfer_status.client_command:
                    transfer_status.client_command = PutGetCommandEnum.HPFCONT.value
                self.client.just_send(
                    transfer_status.client_command,
                    size=header_size,
                    signed=True,
                )

                if transfer_status.client_command == PutGetCommandEnum.HPFCANCEL.value:
                    break
                transfer_status.handling_canpt = False
                continue
            i += 1

            cur_header = self.client.just_recv_int(size=header_size, signed=True)
            if cur_header in (
                PutGetCommandEnum.HPFCANCEL.value,
                PutGetCommandEnum.HPFEND.value,
            ):
                # CANCELATION FROM SERVER OR END OF FILE REACHED
                transfer_status.server_command = cur_header

                # handle hpffin command exchange at the end of getcan command
                transfer_handler(self.client, transfer_status)
                break

            pyld = self.client.just_recv(size=cur_header)
            try:
                data_sink.write(pyld)
            except IOError as e:
                raise TfException(exception=e)
            transfer_status.last_payload_size = len(pyld)
            transfer_handler(self.client, transfer_status)

    def end_command(self):
        """Command is sent by the client to the server in order to terminate the TCP connection."""
        self.client.send('END')
        self.disconnect()

    def sha256_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Makes a sha256 hash of a file indicated by 'path'. This command is intended to apply
        a hash to a file before downloading it in order to guarantee its integrity. Be aware
        that on very large files the time to resolve the digest function could be potentially long.

        Args:
            `path` (str): The path to the target file.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('SHA256', path)))

    def prockey_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Retrieves a unique key generated by the server's instance that communicates with the
        client. This unique key could be used later to identify that instance. One of these
        uses, but not the only one, is to test whether the server or even the socket communication
        line is still opened, in other words: the keepalive mechanism from the client side
        perspective.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate('PROCKEY'))

    def injail_command(
        self,
        secure_token: str,
        pathtojail_directory: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """In-jails the TFProtocol daemon in the directory specified by the second parameter.
        This is achieved only if “secure_token”, specified as first parameter, is permitted
        for that directory.

        Args:
            `secure_token` (str): This token allows you to change the jail folder to isolate your
                tfprotocol instance
            `pathtojail_directory` (str): The jail folder where tfprotocol will be executing
                (Use only if your secure token has access to it).
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('INJAIL', secure_token, '|', pathtojail_directory)
            )
        )

    def get_command(
        self,
        data_sink: BytesIO,
        path_file: str,
        offset: int,
        buffer_size: int,
        response_handler: ResponseHandler = EMPTY_HANDLER,
        transfer_handler: TransferAsyncHandler = EMPTY_HANDLER,
    ):
        """Get Command download data from server asynchronously to any OutputStream the
        user wants...

        Args:
            `data_sink` (BytesIO): It is the stream where data will resides after downloading,
                could be in memory or in disk etc.
            `path_file` (str): The path IN THE SERVER where the data is located at.
            `offset` (int): The offset is used for when we are reading the data start reading
                since the offset position for example if the data is 100 bytes long then if offset
                is 20 I will read since 20 to 100 skiping first 20 bytes. This is useful for when
                we stop an operation and wanted to restart it again later.
            `buffer_size` (int): Is the size of the buffer, while bigger faster will be the
                communication, of course server wont give you always the amount you request,
                because may be that server's bandwidth is getting filled.
            `response_handler` (ResponseHandler): The function to handle the command response.
            `transfer_handler` (TransferAsyncHandler): The function to handle the
                transference cancelations from both client and server asynchronously.
        """
        response = self.client.translate(
            TfProtocolMessage('GET', path_file)
            .add(' ')
            .add(offset, size=LONG_SIZE, signed=False)
            .add(buffer_size, size=LONG_SIZE, signed=True)
        )
        if response.status is not StatusServerCode.OK:
            response_handler(response)
            return
        response.code = MessageUtils.decode_int(response.payload, signed=True)
        response_handler(response)

        # SEEK TO THE OFFSET POSX
        try:
            data_sink.seek(offset)
        except IOError as e:
            raise TfException(exception=e)

        # SET UP SHARED VARIABLES
        cond_lock = Condition()
        code_sr = CodesSenderRecvr(self.client)
        t_handler: TfThread
        t_command: TfThread
        try:
            t_handler = TfThread(
                transfer_handler,
                cond_lock=Condition(),
                args=(code_sr,),
            )
            t_command = TfThread(
                self.__get_command_t,
                cond_lock=cond_lock,
                args=(data_sink, code_sr, response_handler),
            )
        except Exception as e:
            raise TfException(
                exception=e,
                message='FATAL ERROR!!! incorrect callback found, reinstall module...',
            )
        t_handler.start()
        t_command.start()

        with cond_lock:
            while t_command.is_alive() or t_handler.is_alive():
                cond_lock.wait(0.5)
                try:
                    if not t_handler.is_alive() and code_sr.sending_signal:
                        code_sr.send_get(PutGetCommandEnum.HPFFIN.value)
                except InterruptedError as e:
                    raise TfException(exception=e)

        t_command.join()
        t_handler.join()

        # FINAL HANDSHAKE
        if code_sr.last_command is not PutGetCommandEnum.HPFFIN.value:
            self.client.just_send(
                PutGetCommandEnum.HPFFIN.value, size=LONG_SIZE, signed=True
            )
        if code_sr.last_header is not PutGetCommandEnum.HPFFIN.value:
            self.client.just_recv_int(size=LONG_SIZE, signed=True)
        response_handler(
            StatusInfo(status=StatusServerCode.OK, code=PutGetCommandEnum.HPFFIN.value)
        )

    def __get_command_t(
        self,
        data_sink: BytesIO,
        code_sr: CodesSenderRecvr,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """This command is intended to be used ONLY by the getCommand function not by
        user DO NOT CALL THIS METHOD DIRECTLY.

        Args:
            `data_sink` (BytesIO): It is the sink where data will resides after downloading,
                could be in memory or in disk etc.
            `code_sr` (CodesSenderRecvr): Stateful codes sender and receiver helper.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        header_size = LONG_SIZE
        while True:
            try:
                header = self.client.just_recv_int(size=header_size, signed=True)
                if (
                    not code_sr.sending_signal
                    or header <= PutGetCommandEnum.HPFEND.value
                ):
                    status = StatusInfo(StatusServerCode.OK)
                    status.code = header
                    response_handler(status)
                if header <= PutGetCommandEnum.HPFEND.value:
                    code_sr.sending_signal = False
                    return
                chunk = self.client.just_recv(size=header)
                if not code_sr.sending_signal:
                    data_sink.write(chunk)
            except IOError as e:
                raise TfException(exception=e)

    def put_command(
        self,
        data_stream: BytesIO,
        path_file: str,
        offset: int,
        buffer_size: int,
        response_handler: ResponseHandler = EMPTY_HANDLER,
        transfer_handler: TransferAsyncHandler = EMPTY_HANDLER,
    ):
        """Upload a stream of data allowing to cancel at any moment. Asynchronously

        Args:
            `data_stream` (BytesIO): It is the stream where data resides in disk or memory,
                to be sent.
            `path_file` (str): The path IN THE SERVER where the data is located at.
            `offset` (int): The offset is used for when we are reading the data start reading
                since the offset position for example if the data is 100 bytes long then if
                offset is 20 I will read since 20 to 100 skiping first 20 bytes. This is useful
                for when we stop an operation and wanted to restart it again later.
            `buff_size` (int): Is the size of the buffer, while bigger faster will be the
                communication, of course server wont give you always the amount you request,
                because may be that server's bandwidth is getting filled.
            `response_handler` (ResponseHandler): The function to handle the command response.
            `transfer_handler` (TransferAsyncHandler): The function to handle the
                transference cancelations from both client and server asynchronously.
        """
        response = self.client.translate(
            TfProtocolMessage('PUT', path_file)
            .add(' ')
            .add(offset, size=LONG_SIZE, signed=False)
            .add(buffer_size, size=LONG_SIZE, signed=True)
        )
        if response.status is not StatusServerCode.OK:
            response_handler(response)
            return
        response.code = MessageUtils.decode_int(response.payload, signed=True)
        response_handler(response)

        # SEEK TO THE OFFSET POSX
        try:
            data_stream.seek(offset)
        except IOError as e:
            raise TfException(exception=e)

        # SET UP SHARED VARIABLES
        cond_lock = Condition()
        code_sr = CodesSenderRecvr(self.client)
        t_command: TfThread
        try:
            t_command = TfThread(
                self.__put_command_t,
                cond_lock=cond_lock,
                args=(
                    data_stream,
                    response.code,
                    code_sr,
                    response_handler,
                    transfer_handler,
                ),
            )
        except Exception as e:
            raise TfException(
                exception=e,
                message='FATAL ERROR!!! incorrect callback found, reinstall module...',
            )
        # RUN THREAD
        t_command.start()
        # WHILE HEADERS NOT AN END-OF-FILE OR AN ERROR CONTINUES

        while True:
            code_sr.last_header = self.client.just_recv_int(size=LONG_SIZE, signed=True)
            if self.verbosity_mode:
                print('SERVER-HEADER:-', code_sr.last_header)
            if code_sr.last_header <= 0:
                code_sr.recveing_signal = True
                break

        t_command.join()

        # FINAL HANDSHAKE
        if code_sr.last_header != PutGetCommandEnum.HPFFIN.value:
            self.client.just_recv_int(size=LONG_SIZE, signed=True)
        code_sr.send_put(PutGetCommandEnum.HPFFIN.value)
        code_sr.block = True
        transfer_handler(code_sr)

    def __put_command_t(
        self,
        data_stream: BytesIO,
        buffer_size: int,
        code_sr: CodesSenderRecvr,
        response_handler: ResponseHandler = EMPTY_HANDLER,
        transfer_handler: TransferAsyncHandler = EMPTY_HANDLER,
    ):
        """This command is intended to be used ONLY by the put_command function not by
        user DO NOT CALL THIS METHOD DIRECTLY.

        Args:
            `data_stream` (BytesIO): It is the stream where data will take to be upload.
            `buffer_size` (int): Max buffer size of the payloads sended to the server.
            `code_sr` (CodesSenderRecvr): Stateful codes sender and receiver helper.
            `response_handler` (ResponseHandler): The function to handle the command response.
            `transfer_handler` (TransferAsyncHandler): The function to handle the
                transference cancelations from both client and server asynchronously.
        """
        while True:
            try:
                if code_sr.recveing_signal:
                    return

                readed = data_stream.read(buffer_size)
                if not readed:
                    self.client.just_send(
                        PutGetCommandEnum.HPFEND.value, size=LONG_SIZE, signed=True
                    )
                    return
                self.client.send(readed, header_size=LONG_SIZE)

                transfer_handler(code_sr)
                response_handler(StatusInfo(StatusServerCode.OK, code=len(readed)))
            except IOError as e:
                raise TfException(
                    exception=e,
                    message='Some error ocurred while trying to upload data... retry again later',
                )

    def nigma_command(
        self, keylen: int, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Change the current session key to another session key with any arbitrary size. This
        length should be a number equal or greater than 8 and multiple of 4.

        Args:
            `keylen` (int): Is the new session key length
            `response_handler` (ResponseHandler): The function to handle the command response.

        Raises:
            TfException: In case of invalid keylen.
        """
        if keylen % 4 != 0 or keylen < 8:
            raise TfException(
                code=-1,
                message='Invalid key length,'
                ' key length must be multiple of 4'
                ' and greater or equals than 8...',
            )
        response = self.client.translate(TfProtocolMessage('NIGMA', str(keylen)))
        if response.status is StatusServerCode.OK:
            hdr = self.client.just_recv_int(signed=True)
            self.client.session_key = bytes(self.client.just_recv(size=hdr))
            response_handler(
                StatusInfo(
                    status=StatusServerCode.OK,
                    message=str(bytes(self.client.session_key)),
                    payload=self.client.session_key,
                )
            )
        else:
            response_handler(response)

    def rmsd_command(
        self,
        secure_token: str,
        path_dir: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Removes a specified secure directory recursively. The first parameter is the secure
        token that allows to remove the directory specified in the second parameter. The secure
        token could be either a file or a directory named as the first parameter, inside the
        directory specified as the second parameter.

        Args:
            `secure_token` (str): This token allows you to remove the secure folder
            `path_dir` (str): The target folder to be deleted.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('RMSECDIR', secure_token, '|', path_dir)
            )
        )

    def tlb_command(self, response_handler: ResponseHandler = EMPTY_HANDLER):
        """Requests a tuple 2 ip/port from the Transfer Load Balancer pool. The clients can use
        this command -in 'advisory' way- to retrieve other servers in order to balance the
        overall traffic. By 'advisory' we mean that it's up to the clients to agree in asking for
        a server from the pool before start any further interaction.

        Args:
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate('TLB'))

    def sdown_command(self, path: str, data_sink: BytesIO, timeout: float):
        """Downloads the specified file in the command argument.

        Args:
            `path` (str): File path to the server file to be download.
            `data_sink` (BytesIO): Data sink open in write/append mode.
            `timeout` (float): Time out (in seconds) used to shutdown pending connection.
        """
        socket_timeout = self.client.socket.timeout
        self.client.socket.settimeout(timeout if timeout > 0 else socket_timeout)

        # SEND: SDOWN 'path/to/file'
        self.client.send(TfProtocolMessage('SDOWN', path))
        has_error = False
        header = None
        while True:
            try:
                header = self.client.just_recv_int(signed=True)
                if header > 0:
                    try:
                        data = self.client.just_recv(size=header)
                        data_sink.write(data)
                    except IOError:
                        has_error = True
                else:
                    break
            except TfException as e:
                if isinstance(e.original_exception, socket.timeout):
                    if self.verbosity_mode:
                        print('Connection timeout...')
                    break
                else:
                    raise e

        if socket_timeout > 0:
            self.client.socket.settimeout(socket_timeout)

        return header == 0 and not has_error

    def sup_command(self, path: str, data_stream: BytesIO, timeout: float):
        """Uploads the specified file in the command argument.

        Args:
            `path` (str): Path to store uploaded file.
            `data_stream` (BytesIO): Data stream open in read mode.
            `timeout` (float): Time out (in seconds) used to shutdown pending connection.
        """
        socket_timeout = self.client.socket.timeout
        self.client.socket.settimeout(timeout if timeout > 0 else socket_timeout)

        # SEND: SUP 'path/to/store/uploaded/file'
        self.client.send(TfProtocolMessage('SUP', path))
        buffer_size = self.client.max_buffer_size
        readed = b''
        header = 0
        try:
            while True:
                readed = data_stream.read(buffer_size)
                if readed:
                    self.client.send(readed, header_size=INT_SIZE)
                else:
                    break
            self.client.just_send(0, size=INT_SIZE, signed=True)
            header = self.client.just_recv_int(signed=True)
        except TfException as e:
            self.client.stop_connection()
            raise TfException(
                code=ErrorCode.ON_WRITE_OR_RECEIVE_TO_SOCKET,
                exception=e.original_exception,
                message='Socket exception',
            )
        except:  # pylint: disable=bare-except
            self.client.just_send(-1, size=INT_SIZE, signed=True)
            return False
        try:
            self.client.socket.settimeout(socket_timeout)
        except:  # pylint: disable=bare-except
            pass
        return header == 0

    def fsize_command(
        self, path_file: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Gets the file size -in bytes- of the specified file in the parameter.

        Args:
            `path_file` (str): Path to server file.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('FSIZE', path_file))
        size = self.client.just_recv_int(size=LONG_SIZE, signed=True)
        response_handler(
            StatusInfo(
                status=StatusServerCode.OK if size >= 0 else StatusServerCode.FAILED,
                code=size,
                message=str(size),
            )
        )

    def fsizels_command(
        self, path_file: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Each line in the specified file as parameter represents a path to a file. Gets the
        file size -in bytes- of each path.

        Args:
            `path_file` (str): Path to a server file with paths.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('FSIZELS', path_file))
        size: int = None
        while size != -3:
            size = self.client.just_recv_int(size=LONG_SIZE, signed=True)
            response_handler(
                StatusInfo(
                    status=StatusServerCode.CONT
                    if size != -1
                    else StatusServerCode.FAILED,
                    code=size,
                    message=str(size),
                )
            )

    def lsv2_command(
        self,
        path: str,
        path_file_to_store: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Lists the directory indicated by the first parameter. It stores all listed files in
        the file indicated by the second parameter, one file per line.

        Args:
            `path` (str): Path to be list in the server.
            `path_file_to_store` (str): Path to store the 'ls' output list.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('LSV2')
                .add(' ')
                .add(path)
                .add('@||@')
                .add(path_file_to_store),
            )
        )

    def lsrv2_command(
        self,
        path: str,
        path_file_to_store: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Lists (recursively) the directory indicated by the first parameter. It stores all
        listed files in the file indicated by the second parameter, one file per line.

        Args:
            `path` (str): Path to be list in the server.
            `path_file_to_store` (str): Path to store the 'ls' output list.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('LSRV2')
                .add(' ')
                .add(path)
                .add('@||@')
                .add(path_file_to_store),
            )
        )

    def ftype_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Returns a byte indicating the type of the file that the first parameter points to.

        Args:
            `path` (str): Path to file to get type.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('FTYPE', path))
        f_type = self.client.just_recv_int(size=BYTE_SIZE, signed=True)
        response_handler(
            StatusInfo(
                status=StatusServerCode.OK if f_type > -1 else StatusServerCode.FAILED,
                code=f_type,
                message=str(f_type),
            )
        )

    def ftypels_command(
        self, path: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Works pretty much like FTYPE except it return a byte with the type per each line in
        the file indicated by the first parameter.

        Args:
            `path` (str): Path to file containing the paths to files to get type.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('FTYPELS', path))
        f_type = 0
        while f_type != -2:
            f_type = self.client.just_recv_int(size=BYTE_SIZE, signed=True)
            response_handler(
                StatusInfo(
                    status=StatusServerCode.OK
                    if f_type != -1
                    else StatusServerCode.FAILED,
                    code=f_type,
                    message=str(f_type),
                )
            )

    def fstatls_command(
        self, path: str, response_handler: Callable[[FileStat], None] = EMPTY_HANDLER
    ):
        """Returns a special structure per each line in the file indicated by the first parameter.

        Args:
            `path` (str): Path to file containing the paths to files to get stats.
            `response_handler` (Callable[[FileStat], None]): The function to handle the command
                response.
        """
        self.client.send(TfProtocolMessage('FSTATLS', path))
        _code = 0
        while _code != -2:
            fraw_stats = self.client.just_recv(size=26)
            _code, file_stat = FileStat.build_from_structure(fraw_stats)
            response_handler(file_stat)

    # Notify system
    def addntfy_command(
        self,
        token: str,
        path_file_to_listen: str = '',
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Sets a new notification wich starts name is `token`, and the directory is specified
        in the second parameter.

        Args:
            `token` (str): Start name for the notification.
            `path_file_to_listen` (str): Path to set notifications. If it is specified by an
                empty string  then the root directory of the protocol daemon is used.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('ADDNTFY')
                .add(' ')
                .add(token)
                .add(' ')
                .add(path_file_to_listen),
            )
        )

    def startnfy_command(
        self,
        interval: Union[float, str, int],
        response_handler: Callable[[StatusInfo, Callable, Callable], None] = EMPTY_HANDLER,
    ):
        """Starts the notification system. Starts the watchdog to the list of directory specified
        by the ADDNTFY command. Once STARTNTFY is issued there is no way back to the standard mode.

        Args:
            `interval` (float, str, int): Interval to check the directories. If present,
                it's a decimal number expressed in seconds as 3.3 which means 3 seconds and
                300 miliseconds.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('STARTNTFY', str(interval)))

        while True:
            size_ms = self.client.just_recv_int(size=INT_SIZE, signed=False)
            file_notif_b = self.client.just_recv(size=size_ms)
            file_notif = None
            try:
                file_notif = MessageUtils.decode_str(file_notif_b)
            except UnicodeDecodeError:
                pass

            # Clients handles when to send back an OK or DEL response.
            response_handler(
                StatusInfo(
                    payload=file_notif_b,
                    message=file_notif,
                    status=StatusServerCode.OK,
                    code=size_ms,
                    sz=size_ms,
                ),
                send_ok=lambda: self.client.send(TfProtocolMessage('OK')),
                send_del=lambda: self.client.send(TfProtocolMessage('DEL')),
            )

    def intread_command(
        self,
        path: str,
        data_sink: BytesIO,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Integrity Read. It is intended to atomically download a file with its integrity
        checksum, for the case SHA256.

        Args:
            `path` (str): Path to file to read.
            `data_sink` (BytesIO): FileInput in write mode.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('INTREAD', path))
        ms_header = self.client.just_recv_int(size=INT_SIZE, signed=True)
        if ms_header == -1:
            # File not found or some error occurs
            response_handler(StatusInfo(status=StatusServerCode.FAILED, code=ms_header))
            return

        checksum = self.client.just_recv_str(size=66)
        file_payload = self.client.just_recv(size=ms_header)

        data_sink.write(file_payload)
        response_handler(
            StatusInfo(status=StatusServerCode.OK, code=ms_header, message=checksum)
        )

    def intwrite_command(
        self,
        path: str,
        data_stream: BytesIO,
        checksum: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Integrity Write. It is intended to atomically upload a file with its integrity
        checksum, for the case SHA256.

        Args:
            `path` (str): Path to file to write.
            `data_stream` (BytesIO): FileInput in read mode.
            `checksum` (str): Checksum of the file.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        self.client.send(TfProtocolMessage('INTWRITE', path))

        # Send 66 bytes of file hash
        self.client.just_send(checksum)

        # Send the file payload
        payload = data_stream.read()
        self.client.send(payload, header_size=INT_SIZE)

        resp_code = self.client.just_recv_int(size=INT_SIZE, signed=True)

        response_handler(
            StatusInfo(
                status=StatusServerCode.OK
                if resp_code == 0
                else StatusServerCode.FAILED,
                code=resp_code,
            )
        )

    def netlock_command(
        self,
        timeout: Union[float, str, int],
        path_lock: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Creates an advisory record lock in the file specified by the second parameter with a
        timeout in seconds indicated in the first parameter. The system guarantee that each time
        the network detects activity, the timeout will be reset.

        Args:
            `timeout` (float, str, int): Timeout to lock the network. If present, it is a
            decimal number expressed in seconds as 3.3 which means 3 seconds and 300 miliseconds.
            `path_lock` (str): Path to file to lock.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('NETLOCK', str(timeout), path_lock))
        )

    def netlocktry_command(
        self,
        timeout: Union[float, str, int],
        path_lock: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Creates an advisory record lock in the file specified by the second parameter with a
        timeout in seconds indicated in the first parameter. The system guarantee that each time
        the network detects activity, the timeout will be reset. (Works exactly like NETLOCK but
        instead of blocking until obtain the lock, it will return the error FAILED 54.)

        Args:
            `timeout` (float, str, int): Timeout to lock the network. If present, it is a
            decimal number expressed in seconds as 3.3 which means 3 seconds and 300 miliseconds.
            `path_lock` (str): Path to file to lock.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('NETLOCK_TRY', str(timeout), path_lock)
            )
        )

    def netunlock_command(
        self, lock_id: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Removes the advisory record lock in the file specified by the second parameter.

        Args:
            `path_lock` (str): Path to file to unlock.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(self.client.translate(TfProtocolMessage('NETUNLOCK', lock_id)))

    def netmutacqtry_command(
        self,
        path_mutex: str,
        token: Union[bytes, str],
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Tries to acquire the ownership of a synchronization object to enter a critical section.
        Who acquires the mutex 'token' must release it explicitly by calling NETMUTREL command,
        otherwise the mutex will be considered as acquire forever.

        Args:
            `path_mutex` (str): Path to mutex.
            `token` (bytes,str): Token to acquire the mutex.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('NETMUTACQ_TRY', path_mutex, token))
        )

    def netmutrel_command(
        self,
        path_mutex: str,
        token: Union[bytes, str],
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Releases the ownership of a synchronization object to enter a critical section.

        Args:
            `path_mutex` (str): Path to mutex.
            `token` (bytes,str): Token to release the mutex.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('NETMUTREL', path_mutex, token))
        )

    def setfsid_command(
        self,
        secure_file_sys_identity: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """sets the process identity that will be used in any operations that involves the
        TFProtocol Secure Filesystem.

        Args:
            `secure_file_sys_identity` (str): File system identity.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('SETFSID', secure_file_sys_identity)
            )
        )

    def setfsperm_command(
        self,
        secid: str,
        permission_mask: int,
        path_secref_dir: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """sets the permissions of a file or directory.

        Args:
            `secid` (str): Security file system identity, can be '' to set "other's" permissions
                (last resort resource).
            `permission_mask` (int): Permission mask.
            `path_secref_dir` (str): Path to directory.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage(
                    'SETFSPERM', f'{secid}:{permission_mask}', path_secref_dir
                )
            )
        )

    def remfsperm_command(
        self,
        secid: str,
        path_secref_dir: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Removes the secID indicated by the first parameter from the secure filesystem
        directory indicated by the second parameter.

        Args:
            `secid` (str): Security file system identity, can be '' to remove the "other's"
                permissions.
            `path_secref_dir` (str): Path to directory.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('REMFSPERM', secid, path_secref_dir)
            )
        )

    def getfsperm_command(
        self,
        secid: str,
        path_secref_dir: str,
        response_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        """Gets the secID's permissions of the specified directory in the second parameter.


        Args:
            `secid` (str): Security file system identity.
            `path_secref_dir` (str): Path to directory.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(
                TfProtocolMessage('GETFSPERM', secid, path_secref_dir)
            )
        )

    def issecfs_command(
        self, path_to_dir: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Checks if 'path/to/directory' belongs to the TFProtocol Secure Filesystem domain.

        Args:
            `path_to_dir` (str): Path to directory.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('ISSECFS', path_to_dir))
        )

    def locksys_command(
        self, path_in_lock: str, response_handler: ResponseHandler = EMPTY_HANDLER
    ):
        """Locks TFProtocol in the specified directory. Once the daemon is locked in a directory,
        there isn't way back.

        Args:
            `path_in_lock` (str): Path to lock.
            `response_handler` (ResponseHandler): The function to handle the command response.
        """
        response_handler(
            self.client.translate(TfProtocolMessage('LOCKSYS', path_in_lock))
        )
