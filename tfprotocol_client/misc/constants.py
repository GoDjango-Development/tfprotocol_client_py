# coded by lagcleaner
# email: lagcleaner@gmail.com

LONG_SIZE = 8
INT_SIZE = 4
SHORT_SIZE = 2
BYTE_SIZE = 1

DFLT_MAX_BUFFER_SIZE = 8 * 1024  # 512 * 1024
DFLT_HEADER_SIZE = INT_SIZE

# Key len interval in bytes
KEY_LEN_INTERVAL = (16, 40)


ENDIANESS = '>'
ENDIANESS_NAME = 'little' if ENDIANESS == '<' else 'big'
STRING_ENCODING = 'UTF-8'  # UTF-8,LATIN-1, ISO-8859-1

EMPTY_HANDLER = lambda *_: None
RESPONSE_LOGGER = lambda resp: print(f"RESPONSE: {resp}")
