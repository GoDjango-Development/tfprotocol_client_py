# coded by lagcleaner
# email: lagcleaner@gmail.com

from io import BytesIO
from struct import unpack
from typing import Union
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1


class CryptographyUtils:
    """Cryptography utils to handle public key and generate random bytes."""

    @staticmethod
    def rsa_encrypt(payload: bytes, public_key: str) -> bytes:
        recipient_key = RSA.import_key(public_key)
        # Encrypt payload with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key, hashAlgo=SHA1)
        enc_payload = cipher_rsa.encrypt(payload)
        return enc_payload

    get_random_bytes = staticmethod(get_random_bytes)


class Xor:
    """Xor class to en/decrypt messages."""

    SESSION_KEY = None

    def __init__(self, key: Union[bytes, bytearray] = None) -> None:
        if key is not None and (isinstance(key, bytes) or isinstance(key, bytearray)):
            Xor.SESSION_KEY = bytearray(key)
        self._session_key = Xor.SESSION_KEY[:]
        self._key = Xor.SESSION_KEY[:]
        self._seed = self._get_new_seed()

    def _get_new_seed(self) -> int:
        buff = BytesIO(self._key)
        (new_seed,) = unpack('<q', buff.read(8))
        return new_seed

    def get_seed(self) -> int:
        return self._seed

    def encrypt(self, payload: bytes) -> bytearray:
        mut_payload = bytearray(payload)
        for i, _ in enumerate(mut_payload):
            mut_payload[i] ^= self._key[i % len(self._key)]
            # Pack data to send
            mut_payload[i] = (mut_payload[i] + (self._seed >> 56 & 0xFF)) % 256
            # Change seed and encryption key
            self._seed = self._seed * (self._seed >> 8 & 0xFFFFFFFF) + (
                self._seed >> 40 & 0xFFFF
            )
            if self._seed == 0:
                self._seed = self._get_new_seed()
            self._key[i % len(self._key)] = self._seed % 256

        return mut_payload

    def decrypt(self, payload: bytes) -> bytearray:
        mut_payload = bytearray(payload)
        for i, _ in enumerate(mut_payload):
            # Unpack received data
            mut_payload[i] = (256 + mut_payload[i] - (self._seed >> 56 & 0xFF)) % 256
            # Decrypt received data
            mut_payload[i] ^= self._key[i % len(self._key)]
            self._seed = self._seed * (self._seed >> 8 & 0xFFFFFFFF) + (
                self._seed >> 40 & 0xFFFF
            )
            if self._seed == 0:
                self._seed = self._get_new_seed()

            self._key[i % len(self._key)] = self._seed % 256

        return mut_payload
