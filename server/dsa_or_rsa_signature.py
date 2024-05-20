from Crypto.PublicKey import RSA, DSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15, DSS

rsa_key_pair = RSA.generate(bits=1024)
rsa_public_key_obj = rsa_key_pair.publickey()

dsa_key_pair = DSA.generate(bits=1024)

msg = b'hello'
msg1 = b'tempered'

hash_msg = SHA256.new(msg)
hash_msg1 = SHA256.new(msg1)

rsa_signer = pkcs1_15.new(rsa_key_pair)
rsa_signature = rsa_signer.sign(hash_msg)

rsa_verifier = pkcs1_15.new(rsa_public_key_obj)

dsa_signer = DSS.new(dsa_key_pair, 'fips-186-3')
dsa_signature = dsa_signer.sign(hash_msg)

dsa_verifier = DSS.new(dsa_key_pair.publickey(), 'fips-186-3')

try:
    rsa_verifier.verify(hash_msg, rsa_signature)
    print("The RSA signature is valid for the original message!")
except (ValueError, TypeError):
    print("The RSA signature is not valid for the original message!")

print("\nDSA Signature Verification:")

try:
    dsa_verifier.verify(hash_msg, dsa_signature)
    print("The DSA signature is valid for the original message!")
except (ValueError, TypeError):
    print("The DSA signature is not valid for the original message!")
