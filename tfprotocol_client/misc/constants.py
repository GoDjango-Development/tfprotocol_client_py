import sys


DFLT_MAX_BUFFER_SIZE = 512 * 1024
DFLT_HEADER_SIZE = 4

# Key len interval in bytes
KEY_LEN_INTERVAL = (16, 42)


ENDIANESS = '>' if sys.byteorder == 'little' else '<'
STRING_ENCODING = 'utf-8'
