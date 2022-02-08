from abc import ABC, abstractmethod

from tfprotocol_client.models.status_info import StatusInfo


class SuperProtoHandler(ABC):
    '''The callback system where payload will be notified to be handled by the user.'''

    @abstractmethod
    def statusServer(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def responseServerCallback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def instanceTfProtocol(self, instance: any):
        raise NotImplementedError("Callback is not implemented: exception")
