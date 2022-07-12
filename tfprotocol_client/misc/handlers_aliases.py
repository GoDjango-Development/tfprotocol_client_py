# coded by lagcleaner
# email: lagcleaner@gmail.com

from io import BytesIO
from typing import Callable

from tfprotocol_client.connection.codes_sender_recvr import CodesSenderRecvr
from tfprotocol_client.connection.protocol_client import ProtocolClient
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.transfer_state import TransferStatus

ResponseHandler = Callable[[StatusInfo], None]
SendRecvFileHandler = Callable[[bool, str, StatusInfo, BytesIO], None]
TransferHandler = Callable[[ProtocolClient, TransferStatus], None]
TransferAsyncHandler = Callable[[CodesSenderRecvr], None]
