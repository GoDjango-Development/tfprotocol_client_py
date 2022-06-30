from datetime import date as Date
from io import BytesIO
from typing import Callable
from tfprotocol_client.connection.codes_sender_recvr import CodesSenderRecvr
from tfprotocol_client.connection.protocol_client import ProtocolClient
from tfprotocol_client.handlers.super_proto_handler import SuperProtoHandler
from tfprotocol_client.misc.file_stat import FileStat
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.transfer_state import TransferStatus


class TfProtoHandler(SuperProtoHandler):
    '''The callback system where payload will be notified to be handled by the user.'''

    def echo_callback(self, value: str):
        raise NotImplementedError("Callback is not implemented: exception")

    def mkdir_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def del_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def rmdir_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def copy_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def touch_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def fupd_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def date_callback(self, timestamp: int, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def datef_callback(self, date: Date, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def dtof_callback(self, date: Date, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def ftod_callback(self, timestamp: int, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def fstat_callback(self, filestat: FileStat, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def cpdir_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def xcopy_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def xdel_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def xrmdir_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def xcpdir_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def lock_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def sendfile_callback(
        self, is_overriten: bool, path: str, status: StatusInfo, payload: bytes
    ):
        raise NotImplementedError("Callback is not implemented: exception")

    def rcvfile_callback(
        self, delete_after: bool, path: str, status: StatusInfo, sink: BytesIO=None
    ):
        raise NotImplementedError("Callback is not implemented: exception")

    def ls_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def lsr_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def renam_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def keepalive_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def login_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def chmod_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def chown_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def getcan_callback(
        self,
        status: StatusInfo,
        client: ProtocolClient,
        transfer_status: TransferStatus,
    ):
        raise NotImplementedError("Callback is not implemented: exception")

    def putcan_callback(
        self,
        status: StatusInfo,
        client: ProtocolClient,
        transfer_status: TransferStatus,
    ):
        raise NotImplementedError("Callback is not implemented: exception")

    def sha256_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def prockey_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def freesp_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def udate_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def ndate_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def getstatus_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def get_callback(self, codes: CodesSenderRecvr):
        raise NotImplementedError("Callback is not implemented: exception")

    def put_callback(self, codes: CodesSenderRecvr):
        raise NotImplementedError("Callback is not implemented: exception")

    def putstatus_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def nigma_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def rmsecuredirectory_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def injail_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def tlb_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def sdown_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def sup_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def fsize_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def fsizels_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def lsv2_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def lsrv2_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def ftype_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def ftypels_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def fstatls_callback(self, file_stat: FileStat):
        raise NotImplementedError("Callback is not implemented: exception")

    def addntfy_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    def notification_callback(
        self, status: StatusInfo, send_ok: Callable, send_del: Callable,
    ):
        raise NotImplementedError("Callback is not implemented: exception")
