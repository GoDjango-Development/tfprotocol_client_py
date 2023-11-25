from typing import Union
from multipledispatch import dispatch
from tfprotocol_client.extensions.xs_sql_super import XSSQLSuper
from tfprotocol_client.models.status_server_code import StatusServerCode
from tfprotocol_client.tfprotocol_super import TfProtocolSuper
from tfprotocol_client.models.message import TfProtocolMessage
from tfprotocol_client.misc.handlers_aliases import (
    ResponseHandler,
)
from tfprotocol_client.misc.constants import (
    DFLT_MAX_BUFFER_SIZE,
    EMPTY_HANDLER,
    KEY_LEN_INTERVAL,
    LONG_SIZE,
    INT_SIZE
)
from tfprotocol_client.models.proxy_options import ProxyOptions
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.models.exceptions import ErrorCode, TfException

import traceback
from tfprotocol_client.misc.thread import TfThread
from typing import Callable
from threading import RLock,Condition


# ListenHandler = Callable[[StatusInfo], None]

def synchronized_with_attr(lock_name):
    
    def decorator(method):
			
        def synced_method(self, *args, **kws):
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)
                
        return synced_method
		
    return decorator

class XSIme(TfProtocolSuper):
    # pylint: disable=super-init-not-called
    @dispatch(TfProtocolSuper, verbosity_mode=False)
    def __init__(
        self,
        tfprotocol: TfProtocolSuper,
        verbosity_mode: bool = False,
        **_,
    ) -> None:
        """Constructor for Transfer Protocol extended subsystem.

        Args:
            `tfprotocol` (TfProtocolSuper): A created transfer protocol instance.
            `verbosity_mode` (bool): Debug mode enabled for verbosity.
        """
        if (not tfprotocol) or (not  tfprotocol._proto_client) or (not tfprotocol._proto_client.is_connect()):
            raise TfException("Invalid protocol or disconnected protocol... please call " +
                    "to connect function first..."
                    ,status_server_code=-1
                    )
        self._proto_client = tfprotocol._proto_client
        self.verbosity_mode = verbosity_mode
        self.__initialize_default_variables()
        
    
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
        self.__initialize_default_variables()
        
        
    def __initialize_default_variables(self):
        self.lock = RLock()
        self.mutex = Condition()
        self.bloqued=False
        self.tfThread=None
        

    @synchronized_with_attr("lock")
    def start_command(
            self,
            response_handler: ResponseHandler = EMPTY_HANDLER,
            listen_handler: ResponseHandler = EMPTY_HANDLER,
    ):
        #print("bloquedao:",self.bloqued)
        self.bloqued=False
        resp: StatusInfo = self._proto_client.translate('XSIME_START')
        response_handler(resp)
        if resp.status == StatusServerCode.OK:
            def call_listen_handler():
                if not self.bloqued:
                    try:
                        
                        #print("metodo en subproceso?")
                        client=self._proto_client
                        client.max_buffer_size=16*1024
                        resp2: StatusInfo =client.recv(header_size=5)
                        #print("va allamar a listen_handler")
                        listen_handler(resp2)
                        #print("termino metodo subproceso")
                    except:
                        #print("dio error en metodo subproces")
                        print(traceback.format_exc())
            self.tfThread=TfThread(
                target=call_listen_handler
                ,daemon=True
                ,args=[]
                ,cond_lock=self.mutex
                )
            self.tfThread.start()
            
            
    
    @synchronized_with_attr("lock")
    def setup_command(
            self,
            unique_user: bool,
            auto_delete: bool,
            timestamp: int,
    ):
        self.__check_open_connection()

        sz = (1 if unique_user else 0) | (2 if auto_delete else 0)
        value_in_bytes = bytes([4])
        pm=TfProtocolMessage(value_in_bytes)
        pm.add(sz)
        self._proto_client.just_send(pm)
        self._proto_client.just_send(TfProtocolMessage(timestamp))
    
    @synchronized_with_attr("lock")
    def set_path_command(
            self,
            path: str,
    ):
        self.__check_open_connection()

        value_in_bytes = bytes([1])
        pm=TfProtocolMessage(value_in_bytes)
        size_bytes_path=len(path.encode())
        pm.add(size_bytes_path)
        self._proto_client.just_send(pm)
        self._proto_client.just_send(TfProtocolMessage(path))
    
    @synchronized_with_attr("lock")
    def set_username_path_command(
            self,
            username_path: str,
    ):
        self.__check_open_connection()

        size_bytes_path=len(username_path.encode())
        if size_bytes_path> 128:
            raise TfException(status_info=StatusInfo(
                status=StatusServerCode.PAYLOAD_TOO_BIG
                ,code=128
                ,message="Username path shouldnt be greater than 128 bytes, current size is "+str(size_bytes_path)
            ))
            
        
        value_in_bytes = bytes([2])
        pm=TfProtocolMessage(value_in_bytes)
        pm.add(size_bytes_path)
        self._proto_client.just_send(pm)
        self._proto_client.just_send(TfProtocolMessage(username_path))

    @synchronized_with_attr("lock")
    def send_message_command(
            self,
            message: str,
            dest: str,
            *others: str,
    ):
        self.__check_open_connection()

        payload = []
        payload.append(dest.strip() + ":")
        for user in others:
            payload.append(user + ":")
        payload.append(" " + message)

        size_bytes_path = len(payload)
        to_string = "".join(payload)

        value_in_bytes = bytes([5])
        pm=TfProtocolMessage(value_in_bytes)
        pm.add(size_bytes_path)
        self._proto_client.just_send(pm)
        self._proto_client.just_send(TfProtocolMessage(to_string))


    @synchronized_with_attr("lock")
    def sleep_interval_command(
            self,
            interval: int,
    ):
        self.__check_open_connection()

        interval = max(interval, 0)

        value_in_bytes = bytes([7])
        pm=TfProtocolMessage(value_in_bytes)
        pm.add(0)
        self._proto_client.just_send(pm)
        self._proto_client.just_send(TfProtocolMessage(interval))
    
    @synchronized_with_attr("lock")
    def close_command(
            self,
            
    ):
        byte_array = bytes([b for b in bytearray(4)])

        value_in_bytes = bytes([0])
        pm=TfProtocolMessage(value_in_bytes)
        pm.add(0)
        self._proto_client.just_send(pm)
        self._proto_client.just_send(TfProtocolMessage(byte_array))

        self.bloqued=True
        if self.tfThread.is_alive():
            self.tfThread.interrupt()

        
        # with self.mutex:
        #     try:
        #         self.bloqued=True
        #         #print("CLOSED !!!!!!!!!!!!!!!!!")
        #         #self.mutex.wait()
        #     except:
        #         print(traceback.format_exc())
    
    def __check_open_connection(self):
        if self.bloqued:
            raise TfException("closed connection",status_server_code=-1)

        
        