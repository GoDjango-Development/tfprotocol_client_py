from abc import ABC, abstractmethod

from tfprotocol_client.models.status_info import StatusInfo


class SuperProtoHandler(ABC):
    '''The callback system where payload will be notified to be handled by the user.'''

    @abstractmethod
    def status_server(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def response_server_callback(self, status: StatusInfo):
        raise NotImplementedError("Callback is not implemented: exception")

    @abstractmethod
    def instance_tfprotocol(self, instance: any):
        raise NotImplementedError("Callback is not implemented: exception")
