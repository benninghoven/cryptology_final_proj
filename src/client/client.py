import socket
import threading
import configparser
import time

from Crypto.PublicKey import RSA

public_key = RSA.import_key("public.pem")
print(public_key)

config = configparser.ConfigParser()
config.read("config.ini")

STATES = {
    "MENU": 0,
    "LOGIN": 1,
    "LOGOUT": 2,
    "SAVE": 3,
    "EXIT": 4
}


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Start()

    def Start(self):
        self.ConnectToServer()
        self.LoginMenu()

    def ConnectToServer(self):
        print("Connecting to server...")
        while True:
            try:
                self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
                print("connected to server")
                return

            except Exception as e:
                print("Cannot connect to server!")
                print(e)
                time.sleep(1)

    def LoginMenu(self):
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter choice: ")
        self.Send(choice)

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
        #key = RSA.import_key(open('public_key.pub').read())
        ciphertext = message
        self.socket.send(ciphertext.encode("utf-8"))

    def DisconnectFromServer(self):
        self.socket.close()

    def Login(self):
        return False

    def Logout(self):
        return False

    def SaveData(self):
        return False
