import struct
import warnings
from pep272_encryption import PEP272Cipher

try:
    from _xtea import \
        encrypt_int as _encrypt_int, \
        decrypt_int as _decrypt_int

except ImportError:
    def _encrypt_int(k, v, n=32):
        v0, v1 = v

        sum, delta, mask = 0, 0x9e3779b9, 0xffffffff
        for _ in range(n):
            v0 = (v0 + (((v1 << 4 ^ v1 >> 5) + v1) ^
                        (sum + k[sum & 3]))) & mask
            sum = (sum + delta) & mask
            v1 = (v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^
                        (sum + k[sum >> 11 & 3]))) & mask

        return v0, v1

    def _decrypt_int(k, v, n=32):
        v0, v1 = v

        delta, mask = 0x9e3779b9, 0xffffffff
        sum = (delta * n) & mask
        for _ in range(n):
            v1 = (v1 - (((v0 << 4 ^ v0 >> 5) + v0) ^
                        (sum + k[sum >> 11 & 3]))) & mask
            sum = (sum - delta) & mask
            v0 = (v0 - (((v1 << 4 ^ v1 >> 5) + v1) ^
                        (sum + k[sum & 3]))) & mask

        return v0, v1


MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_PGP = 4
MODE_OFB = 5
MODE_CTR = 6
KEY = b" " * 16


block_size = 8
key_size = 16


def new(key, **kwargs):
    return XTEACipher(key, **kwargs)


class XTEACipher(PEP272Cipher):
    block_size = 8
    IV = None
    counter = None

    def __init__(self, key, mode=None, **kwargs):
        if mode is None:
            mode = MODE_ECB
            warnings.warn("Implicitly selecting ECB mode of operation. "
                          "The ECB mode is usually insecure to use.")

        super(XTEACipher, self).__init__(key, mode, **kwargs)

        self.rounds = int(kwargs.get("rounds", 64))
        self.cycles = self.rounds // 2
        self.endian = kwargs.get("endian", "!")

        self.__k = struct.unpack(self.endian + "4L", self.key)

    def encrypt_block(self, key, block, **kwargs):
        encrypted_block = _encrypt_int(
            self.__k,
            struct.unpack(self.endian + "2L", block),
            self.cycles
        )

        return struct.pack(
            self.endian + "2L",
            *encrypted_block
        )

    def decrypt_block(self, key, block, **kwargs):
        decrypted_block = _decrypt_int(
            self.__k,
            struct.unpack(self.endian + "2L", block),
            self.cycles
        )

        return struct.pack(
            self.endian + "2L",
            *decrypted_block
        )


def xtea_encode(txt):
    content = bytes(txt, encoding='utf-8')
    x = new(KEY, mode=MODE_OFB, IV=b"12345678")
    return x.encrypt(content)


def xtea_decode(txt):
    c = xtea_encode(txt)
    q = new(KEY, mode=MODE_OFB, IV=b"12345678").decrypt(c)
    return q.decode()
