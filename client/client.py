import socket
import configparser
import threading


config = configparser.ConfigParser()
config.read("../config.ini")


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_length = int(config["top-secret"]["HeaderLength"])

        self.ConnectToServer()

        threading.Thread(target=self.Listen).start()
        threading.Thread(target=self.GetInput).start()

    def __del__(self):
        print("destroying client")
        self.DisconnectFromServer()

    def ConnectToServer(self):
        print("connecting to server...")
        try:
            self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))

        except Exception as e:
            print(f"Error: {e}")
            exit()

    def DisconnectFromServer(self):
        print("disconnecting from server...")
        self.socket.close()

    def GetInput(self):
        print("getting client input")
        while True:
            message = input()
            self.SendMessage(message)

    def SendMessage(self, message):
        message_length = len(message)
        # make sure message_length is the same length as header_length
        header = f"{message_length:<{self.header_length}}"
        print(f"header: {header}")

        print("start")
        print(f"message: {message}")
        print("end")
        try:
            self.socket.send(message.encode("utf-8"))

        except Exception as e:
            print(f"Error: {e}")
            exit()

    def Listen(self):
        print("listening for messages")

        try:
            while True:
                response = self.socket.recv(self.header_length).decode("utf-8")
                print(f"response: {response}")

        except Exception as e:
            print(e)
            exit()
