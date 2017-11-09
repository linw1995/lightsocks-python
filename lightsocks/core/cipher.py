class Cipher:
    def __init__(self, encodePassword: bytearray, decodePassword: bytearray):
        self.encodePassword = encodePassword.copy()
        self.decodePassword = decodePassword.copy()

    def encode(self, bs: bytearray):
        for i, v in enumerate(bs):
            bs[i] = self.encodePassword[v]

    def decode(self, bs: bytearray):
        for i, v in enumerate(bs):
            bs[i] = self.decodePassword[v]

    @classmethod
    def NewCipher(cls, encodePassword: bytearray):
        decodePassword = encodePassword.copy()
        for i, v in enumerate(encodePassword):
            decodePassword[v] = i
        return cls(encodePassword, decodePassword)
