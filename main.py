from datetime import datetime
import os
from tfprotocol_client.handlers.proto_handler import TfProtoHandler
from tfprotocol_client.models.status_info import StatusInfo
from tfprotocol_client.tfprotocol import TfProtocol


def get_publickey():
    """[summary]

    Returns:
        [type]: [description]
    """
    with open('public.key', mode='r', encoding='utf8') as f:
        public_key = f.read()
    # public_key = public_key[26:]
    # public_key = public_key[:-25].strip('\n')
    return public_key


def get_random_bytes(lenght: int) -> bytes:
    return os.urandom(lenght)


class MyHandler(TfProtoHandler):
    """My handler

    Args:
        SuperProtoHandler ([type]): [description]
    """

    def echo_callback(self, value: str):
        """ echo <value>

        Args:
            value (str): String value.
        """
        print(f'Server: {value}')

    def mkdir_callback(self, status: StatusInfo):
        """ mkdir <value>

        Args:
            value (str): String value.
        """
        print(f'Server: {status}')

    def ftod_callback(self, timestamp, status):
        """ date <value>
        """
        print(f'Server: {status}; datetime:{timestamp}')

    def datef_callback(self, date: datetime, status: StatusInfo):
        """ datef <value>
        """
        print(f'Server: {status}; datetime:{date}')

    def status_server(self, status: StatusInfo):
        pass

    def response_server_callback(self, status: StatusInfo):
        pass

    def instance_tfprotocol(self, instance: any):
        pass


if __name__ == '__main__':
    ADDRESS = 'tfproto.expresscuba.com'
    PORT = 10345
    proto = TfProtocol('0.0', get_publickey(), 'testhash', MyHandler(), ADDRESS, PORT)

    proto.connect()
    # proto.echo_command('Hello_World.')
    proto.datef_command()
