from getpass import getpass
import rsa


class User:
    def __init__(self):
        self.username = None
        self.password = None
        self.friends = []
        self.status = "Offline"
        self.public_key, self.private_key = rsa.newkeys(512)

    def __str__(self):
        return f'{self.status} {self.username} {self.public_key}'

    def set_username(self):
        self.username = input('Enter your username: ')

    def set_password(self):
        self.password = getpass('Enter your password: ')
