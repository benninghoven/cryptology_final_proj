from getpass import getpass
from enum import Enum


class UserState(Enum):
    MAINMENU = 1
    CLIENTMENU = 2
    INCHAT = 3


class User:
    def __init__(self):
        self.username = None
        self.password = None
        self.state = UserState.MAINMENU

        self.status = "Offline"
        self.signed_in = False
        self.friends = []

    def __str__(self):
        return f'{self.status} {self.username}'

    def set_username(self):
        self.username = input('Enter your username: ')

    def set_password(self):
        self.password = getpass('Enter your password: ')
