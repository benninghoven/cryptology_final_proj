import socket
import threading
from config import GetConfig
from user import User
import json

config = GetConfig()


def load_users():
    print("loading users from file")
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
            return users
    except FileNotFoundError:
        return {}


def save_users(users):
    print("saving users to file")
    with open("users.json", "w") as file:
        json.dump(users, file)


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.user = None
        self.connected = False
        self.Start()

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
            return True

        except ConnectionRefusedError:
            print("is the server running?")
            return False

    def Start(self):
        if self.ConnectToChatServer() is True:
            self.StartMenu()
        else:
            print("could not connect to server")
            exit()

    def StartMenu(self):
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            self.Login()
        elif choice == "2":
            self.Register()
        elif choice == "3":
            exit()
        else:
            print("Invalid choice")
            self.StartMenu()

    def Login(self):
        users = load_users()
        self.user.set_username()

        if self.user.username in users:
            self.user.set_password()
            if self.user.password == users[self.user.username]["password"]:
                self.Home()
            else:
                print("Invalid password")
                self.Login()
        else:
            print("User not found")
            self.Login()

        self.Home()

    def Register(self):
        users = load_users()
        self.user.set_username()
        if self.user.username in users:
            print("Username already exists")
            self.Register()
        else:
            self.user.set_password()
            users = {self.user.username: {
                "password": f"{self.user.password}",
                }}
            save_users(users)
            print("User registered successfully")
            self.StartMenu()

    def AddFriend(self):
        users = load_users()
        username = input("Enter username to add: ")
        if username in users:
            self.user.friends.append(username)
            print(f"{username} added to friends list")
        else:
            print("User not found")

    def Home(self):
        print(f"Logged in as: {self.user.username}")
        print(f"Online friends: {self.user.friends}/{len(self.user.friends)}")
        while True:
            print("1. Send message")
            print("2. Add friend")
            print("3. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.SendMessage()
            elif choice == "2":
                self.AddFriend()
            elif choice == "3":
                self.StartMenu()
            else:
                print("Invalid choice")


if __name__ == "__main__":
    client = Client()
