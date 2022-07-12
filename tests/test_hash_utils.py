# coded by lagcleaner
# email: lagcleaner@gmail.com

from tfprotocol_client.security.hash_utils import sha256_for


def test_hash():
    """Test the hash utils"""
    assert (
        sha256_for('esto es probando')
        == b'\xbdB\xa31\x11\x94\x1bP\xbf\xc8r\xa4\xb7\xf7\x1f\xbee\xca\xf35\xcaj\xbd\x0c\xe0e\xf6\x83X\x87\xb3\x0f'
    )
    assert sha256_for('esto es probando') == sha256_for(b'esto es probando')
