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

# Set identity and it's permissions for the directory.
SECFS_SETPERM = 1
# Remove identity and it’s permissions for the directory.
SECFS_REMPERM = 2
# Set Read permission for files in the directory.
SECFS_RFILE = 4
# Set Write -Create, Truncate, etc.- permission for files in the directory.
SECFS_WFILE = 8
# Set List permission for files in the directory.
SECFS_LDIR = 16
# Set Remove Directory permission for directories in the directory.
SECFS_RMDIR = 32
# Set Make Directory permission for directories in the directory.
SECFS_MKDIR = 64
# Set Delete permission for files in the directory.
SECFS_DFILE = 128
# Set STAT permission for files and directories in the directory
SECFS_STAT = 256
# Set File Updating Timestamps permission for files and directories in the directory.
SECFS_FDUPD = 512
# Set UNIX permission changing for files and directories in the directory.
SECFS_UXPERM = 1024
# Set List Directory Recursively permission for files and directories in the directory.
SECFS_LRDIR = 2048

# Set all permissions for files and folders
SECFS_ALL_PERMISSIONS = (
    SECFS_SETPERM
    | SECFS_REMPERM
    | SECFS_RFILE
    | SECFS_DFILE
    | SECFS_LDIR
    | SECFS_RMDIR
    | SECFS_MKDIR
    | SECFS_DFILE
    | SECFS_STAT
    | SECFS_FDUPD
    | SECFS_UXPERM
    | SECFS_LRDIR
)
