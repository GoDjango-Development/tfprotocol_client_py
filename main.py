import os
from tfprotocol_client.handlers.super_proto_handler import SuperProtoHandler
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


# def encrypt_session_key(session_key: bytes, public_key: str) -> bytes:
#     pass
# cipher = c


# def test():
#     ADDRESS = 'tfproto.expresscuba.com'
#     PORT = 10345
#     BUFFER_SIZE = 512 * 1024
#     ENDIANESS = '>' if sys.byteorder == 'little' else '<'
#     print('Start Test')

#     # START CONNECTION
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     ip = socket.gethostbyname(ADDRESS)
#     result = sock.connect((ip, PORT))

#     payload = b'0.0'

#     header_buffer = ctypes.create_string_buffer(4)
#     struct.pack_into(f'{ENDIANESS}i', header_buffer, 0, len(payload))
#     sock.send(header_buffer)  # SEND HEADER
#     sock.send(struct.pack(f'{ENDIANESS}{len(payload)}s', payload))  # SEND BODY

#     a = sock.recv(4)  # RECIVE header
#     print(a)
#     (a,) = struct.unpack(f'{ENDIANESS}i', a)
#     print(a)
#     if a > 0:
#         b = sock.recv(a)  # RECIVE body
#         print(b)
#         (b,) = struct.unpack(f'{ENDIANESS}{a}s', b)
#         print(b)
#     # ENCRYPT
#     print('==Encrypt==')
#     enc_session_key = pyCryptodomeExample()
#     header_buffer = ctypes.create_string_buffer(4)
#     struct.pack_into(f'{ENDIANESS}i', header_buffer, 0, len(enc_session_key))
#     sock.send(header_buffer)  # SEND HEADER
#     sock.send(
#         struct.pack(f'{ENDIANESS}{len(enc_session_key)}s', enc_session_key)
#     )  # SEND BODY
#     a = sock.recv(4)  # RECIVE header
#     print(a)
#     (a,) = struct.unpack(f'{ENDIANESS}i', a)
#     print(a)
#     if a > 0:
#         b = sock.recv(a)  # RECIVE body
#         print(b)
#         (b,) = struct.unpack(f'{ENDIANESS}{a}s', b)
#         print(b)


class MyHandler(SuperProtoHandler):
    """My handler

    Args:
        SuperProtoHandler ([type]): [description]
    """

    def echoCallback(self, value: str):
        """ echo <value>

        Args:
            value (str): String value.
        """
        print(f'Server: {value}')

    def statusServer(self, status: StatusInfo):
        pass

    def responseServerCallback(self, status: StatusInfo):
        pass

    def instanceTfProtocol(self, instance: any):
        pass


if __name__ == '__main__':
    ADDRESS = 'tfproto.expresscuba.com'
    PORT = 10345
    proto = TfProtocol('0.0', get_publickey(), 'testhash', MyHandler(), ADDRESS, PORT)

    proto.connect()
    proto.echo_command('Hello_World.')
