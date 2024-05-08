from Crypto.PublicKey import RSA


def GeneratePublicKey():
    key = RSA.generate(2048)

    with open('public.pem', 'wb') as f:
        f.write(key.publickey().exportKey('PEM'))

    with open('private.pem', 'wb') as f:
        f.write(key.exportKey('PEM'))
