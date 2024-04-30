import socket
import threading
import json

from .config import GetConfig
from .user import User

config = GetConfig()


def generate_salt():
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def generate_hashed_password(password, salt):
    import hashlib
    return hashlib.sha256(password.encode() + salt.encode()).hexdigest()


def load_users():
    FILENAME = "users.json"

    print(f"checking if {FILENAME} exists...")
    try:
        with open(FILENAME, "r"):
            print(f"{FILENAME} found")
            pass
    except FileNotFoundError:
        print(f"{FILENAME} not found")
        with open(FILENAME, "w") as file:
            json.dump({}, file)

    with open(FILENAME, "r") as file:
        if file.read() == "":
            print(f"{FILENAME} is empty")
            return {}
        file.seek(0)  # json.load(file) is not working without this
        try:
            return json.load(file)
        except json.decoder.JSONDecodeError:
            print("error loading users from file")
            return {}


def save_users(users):
    print("saving users to file...")
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)
    print("users saved to file")


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user = User()
        self.connected = False
        self.Start()

    def Start(self):
        # if self.ConnectToChatServer() is True:
        if True:
            while True:
                self.StartMenu()
        else:
            print("could not connect to server")
            exit()

    def __del__(self):
        self.socket.close()

    def Listen(self):

        print("listening for messages from socket")

        try:
            while True:
                response = self.socket.recv(1024).decode("utf-8")
                print(response)

        except Exception as e:
            print(e)
            exit()

    def Send(self, message):
        self.socket.send(message.encode("utf-8"))

    def ConnectToChatServer(self):
        try:
            self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
            self.connected = True
            self.user = User()
            print("Connected to server")
            return True

        except ConnectionRefusedError:
            print("is the server running?")
            return False

    def StartMenu(self):
        print("1. Login")
        print("2. Register")
        print("3. List Users")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            self.Login()
        elif choice == "2":
            self.Register()
        elif choice == "3":
            self.ListUsers()
        elif choice == "9":
            exit()
        else:
            print("Invalid choice")
            self.StartMenu()

    def Login(self):
        users = load_users()
        self.user.set_username()

        if self.user.username in users:

            self.user.set_password()

            salt = users[self.user.username]["salt"]

            given_hashed_password = generate_hashed_password(self.user.password, salt)
            actual_hashed_password = (users[self.user.username]["hashed_password"])

            print(f"correct_hashed_password: {actual_hashed_password}")
            print(f"given_hashed_password:   {given_hashed_password}")

            if actual_hashed_password == given_hashed_password:
                self.Home()
            else:
                print("Invalid password")
                self.StartMenu()
        else:
            print("User not found")
            self.StartMenu()

    def Register(self):
        users = load_users()
        self.user.set_username()
        if self.user.username in users:
            print("Username already exists")
            self.Register()
        else:
            self.user.set_password()
            salt = generate_salt()
            hashed_password = generate_hashed_password(self.user.password, salt)

            users[self.user.username] = {
                "hashed_password": f"{hashed_password}",
                "salt": f"{salt}"
                }

            save_users(users)

            print("User registered successfully")

            self.StartMenu()

    def AddFriend(self):
        users = load_users()
        username = input("Enter username to add: ")
        if username in users:
            self.user.friends.append(username)
            print(f"sent {username} a friend request")
        else:
            print("user not found")

    def ListUsers(self):
        users = load_users()
        print("=-=-=-=-=-=-=-= Users =-=-=-=-=-=-=-=")
        for user in users:
            print(user)

    def Home(self):
        print(f"Logged in as: {self.user.username}")
        print(f"Online friends: {self.user.friends}/{len(self.user.friends)}")
        while True:
            print("1. Send message")
            print("2. Add friend")
            print("3. List users")
            print("9. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.SendMessage()
            elif choice == "2":
                self.AddFriend()
            elif choice == "3":
                self.ListUsers()
            elif choice == "9":
                self.StartMenu()
            else:
                print("Invalid choice")


if __name__ == "__main__":
    client = Client()
