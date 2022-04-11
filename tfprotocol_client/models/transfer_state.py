class TransferStatus:
    """Transfer status"""

    def __init__(self) -> None:
        self.dummy = None
        self.command = None
        self.dummy_state = None

    def __str__(self) -> str:
        return f'<{self.dummy}-{self.command}-{self.dummy_state}>'
