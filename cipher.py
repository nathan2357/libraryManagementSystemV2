import hashlib
import base64
from cryptography.fernet import Fernet


class Cipher:

    def __init__(self, secret_value):
        self.secret_value = secret_value
        self.key = base64.urlsafe_b64encode(hashlib.sha256(self.secret_value.encode()).digest())
        self.cipher = Fernet(self.key)

    def encrypt(self, message: str) -> str:
        return self.cipher.encrypt(message.encode()).decode()

    def decrypt(self, message: str) -> str:
        return self.cipher.decrypt(message.encode()).decode()


if __name__ == "__main__":
    c = Cipher("hello")
    m = c.encrypt("hll")
    print(c.decrypt(m))
