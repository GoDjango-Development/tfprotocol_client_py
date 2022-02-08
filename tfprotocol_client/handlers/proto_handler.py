from abc import abstractmethod
from datetime import date as Date
from tfprotocol_client.handlers.super_proto_handler import SuperProtoHandler
from tfprotocol_client.models.status_info import StatusInfo


class TfProtoHandler(SuperProtoHandler):
    '''The callback system where payload will be notified to be handled by the user.'''

    @abstractmethod
    def echoCallback(self, value: str):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def mkdirCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def delCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def rmdirCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def copyCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def touchCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def fupdCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def dateCallback(self, timestamp: int, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def datefCallback(self, date: Date, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def dtofCallback(self, date: Date, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def ftodCallback(self, timestamp: int, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def fstatCallback(self, timestamp: int, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def cpdirCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def xcopyCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def xdelCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def xrmdirCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def xcpdirCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def lockCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def sendFileCallback(
        self, is_overriten: bool, path: str, send_to_server: StatusInfo, payload: bytes
    ):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def rcvFileCallback(
        self, delete_after: bool, path: str, send_to_server: StatusInfo
    ):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def lsCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def renamCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def keepAliveCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def loginCallback(self, login_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def chmodCallback(self, chmod_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def chownCallback(self, chown_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def getCanCallback(self, pcan_status: StatusInfo, other: any):
        # FIX: this other is temporal here goes easy_reum
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def putCanCallback(self, status: StatusInfo, other: any):
        # FIX: this other is temporal here goes easy_reum
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def sha256Callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def prockeyCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def freespCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def udateCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def ndateCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def getWriteCallback(self, codes: any):
        # FIX: CODES HAVE TO BE A SPECIFIC TYPE
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def getReadCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def putCallback(self, codes: any):
        # FIX: CODES HAVE TO BE A SPECIFIC TYPE
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def putStatusCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def nigmaCallback(self, bld_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def rmSecureDirectoryCallback(self, bld_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def injailCallback(self, injail_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def tlbCallback(self, tlb_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def sdownCallback(self, sdown_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def supCallback(self, sup_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def fsizeCallback(self, fsize_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def fsizelsCallback(self, fsizels_status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

