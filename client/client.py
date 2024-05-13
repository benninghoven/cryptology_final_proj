import socket
import time
import configparser


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
        self.STREAM_SIZE = 1024
        self.Start()

    def __del__(self):
        self.DisconnectFromServer()

    def DisconnectFromServer(self):
        self.socket.close()

    def Start(self):
        self.ConnectToServer()
        self.Listen()

    def ConnectToServer(self):
        print("Connecting to server...")
        try:
            self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))

        except Exception as e:
            print(f"Error: {e}")
            exit()

    def Listen(self):
        print(f"👂 Listening to server...")
        try:
            while True:
                response = self.socket.recv(self.STREAM_SIZE).decode("utf-8")
                print(response)

        except Exception as e:
            print(e)
            exit()
