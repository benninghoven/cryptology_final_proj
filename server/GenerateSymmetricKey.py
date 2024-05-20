import secrets


def GenerateSymmetricKey():
    key_length = 32  # 32 bytes = 256 bits (for AES-256)
    return secrets.token_bytes(key_length).hex()
