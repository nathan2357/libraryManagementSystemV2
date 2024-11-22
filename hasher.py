import bcrypt


def hash_str(string: str) -> str:
    byte_password = string.encode("utf-8")
    hashed_password = bcrypt.hashpw(byte_password, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def check_hash(string: str, hash_: str) -> bool:
    byte_password = string.encode("utf-8")
    byte_hash_ = hash_.encode("utf-8")
    return bcrypt.checkpw(byte_password, byte_hash_)


if __name__ == "__main__":
    pass
