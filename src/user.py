from getpass import getpass


class User:
    def __init__(self):
        self.username = None
        self.password = None
        self.friends = []

    def __str__(self):
        return f'{self.name} password: {self.password}'

    def set_username(self):
        username = input('Enter your username: ')
        self.username = username

    def set_password(self):
        self.password = getpass('Enter your password: ')
