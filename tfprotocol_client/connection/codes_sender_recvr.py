# coded by lagcleaner
# email: lagcleaner@gmail.com

from tfprotocol_client.connection.protocol_client import ProtocolClient
from tfprotocol_client.misc.constants import LONG_SIZE
from tfprotocol_client.models.putget_commands import PutGetCommandEnum


class CodesSenderRecvr:
    """Codes sender and receiver easy to use class. To handle signals of PUT and GET
    commands.
    """

    def __init__(self, client: ProtocolClient) -> None:
        """Codes utility initialization.

        Args:
            client (ProtocolClient): Protocol client.
        """
        self._client: ProtocolClient = client
        self.recveing_signal: bool = False
        self.sending_signal: bool = False
        self.block: bool = False
        self._last_command = PutGetCommandEnum.HPFEND.value
        self.last_header: int = 0

    def send_put(self, command: int):
        """Send a code to the server codes can only be codes described at XSAceConsts
        class.

        Args:
            command (int[64-bit]): The code to be send to server.
        """
        if not self.block:
            self.recveing_signal = True
            self._last_command = command
            self._client.just_send(command, size=LONG_SIZE, signed=True)

    def send_get(self, command: int):
        """Send a code to the server codes can only be codes described at XSAceConsts
        class.

        Args:
            command (int[64-bit]): The code to be send to server.
        """
        if not self.block:
            self.sending_signal = True
            self._last_command = command
            self._client.just_send(command, size=LONG_SIZE, signed=True)

    @property
    def last_command(self):
        """Return the last command sent."""
        return self._last_command
