from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import Crypto.Signature.pkcs1_15


# Now generate using DSA



# Generate 1024-bit RSA key pair (private + public key)
keyPair = RSA.generate(bits=1024)
server_public_key = keyPair.publickey().export_key()
server_private_key = keyPair.export_key()

print(f"Public key: {server_public_key.decode('utf-8')}")
print(f"Private key: {server_private_key.decode('utf-8')}")


# Get just the public key
justPubKey = keyPair.publickey()

# The good message
msg = b'hello'

# The tempered message
msg1 = b'tempered'

# Compute the hashes of both messages
hash = SHA256.new(msg)
hash1 = SHA256.new(msg1)

# Sign the hash
sig1 = Crypto.Signature.pkcs1_15.new(keyPair)
signature = sig1.sign(hash)

##################### On the arrival side #########################

# Note, we will have to take the decrypted message, hash it and then provide the hash and the signature to the
# verify function

verifier = Crypto.Signature.pkcs1_15.new(justPubKey)

# If the verification succeeds, nothing is returned.  Otherwise a ValueError exception is raised
# Let's try this with the valid message
try:
    verifier.verify(hash, signature)
    print("The signature is valid!")
except ValueError:
    print("The signature is not valid!")

hash = hash1

# Now with the invalid message
try:
    verifier.verify(hash1, signature)
    print("The signature is valid!")
except ValueError:
    print("The signature is not valid!")
