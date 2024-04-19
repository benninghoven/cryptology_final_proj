from cryptography.fernet import Fernet


key = Fernet.generate_key()
f = Fernet(key)

print(f"KEY: {key}")

cipher_text = f.encrypt(b"Secret message")

print(cipher_text)

print(f.decrypt(cipher_text))
