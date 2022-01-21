import binascii
from statistics import mode
from io import BytesIO
import socket
import struct
import sys
import ctypes


def get_key():
    with open('public.key', mode='r') as f:
        public_key = f.read()
    public_key = public_key[26:]
    public_key = public_key[:-25].strip('\n')
    return public_key


if __name__ == '__main__':
    BUFFER_SIZE = 512 * 1024
    print('Start Test')
    ADDRESS = 'tfproto.expresscuba.com'
    ENDIANESS = '>' if sys.byteorder == 'little' else '<'
    PORT = 10345

    # START CONNECTION
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = socket.gethostbyname(ADDRESS)
    result = sock.connect((ip, PORT))

    payload = b'0.0'

    header_buffer = ctypes.create_string_buffer(4).
    struct.pack_into(f'{ENDIANESS}i', header_buffer, 0, len(payload))
    sock.send(header_buffer)  # SEND HEADER
    sock.send(struct.pack(f'{ENDIANESS}{len(payload)}s', payload))  # SEND BODY

    a = sock.recv(4)  # RECIVE header
    print(a)
    (a,) = struct.unpack(f'{ENDIANESS}i', a)
    print(a)
    if a > 0:
        b = sock.recv(a)  # RECIVE body
        print(b)
        (b,) = struct.unpack(f'{ENDIANESS}{a}s', b)
        print(b)
    # ENCRYPT
    PUBLIC_KEY = get_key()
    print(bytes(PUBLIC_KEY.encode('utf-8')))
