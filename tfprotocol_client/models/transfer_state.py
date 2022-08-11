# coded by lagcleaner
# email: lagcleaner@gmail.com


class TransferStatus:
    """Transfer status"""

    def __init__(
        self,
        client_command: int = None,
        server_command: int = None,
        handling_canpt: bool = False,
        last_payload_size: int = 0,
    ) -> None:
        self.client_command = client_command
        self.server_command = server_command
        self.handling_canpt = handling_canpt
        self.last_payload_size = last_payload_size

    def copy(self):
        return TransferStatus(
            client_command=self.client_command,
            server_command=self.server_command,
            handling_canpt=self.handling_canpt,
            last_payload_size=self.last_payload_size,
        )

    def __str__(self) -> str:
        return f'TransferStatus<{self.client_command}, {self.server_command}, {self.handling_canpt}>'

    __repr__ = __str__
