import socket
import configparser
import threading
import pwinput

config = configparser.ConfigParser()
config.read("../config.ini")


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header_length = int(config["top-secret"]["HeaderLength"])

        self.is_sensitive = False

        self.ConnectToServer()

        self.listen_thread = threading.Thread(target=self.Listen)
        self.listen_thread.start()

        self.input_thread = threading.Thread(target=self.Input)
        self.input_thread.start()

        self.chats = {}

        self.server_public_key = None
        try:
            with open("server_public_key.pem", "rb") as file:
                self.server_public_key = file.read()
                print("server public key loaded")
        except FileNotFoundError:
            print("Error, server public key not found")
            exit()

    def __del__(self):
        print("destroying client")
        self.DisconnectFromServer()

    def ConnectToServer(self):
        try:
            self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        except Exception as e:
            print(f"Error, could not connect to server: {e}")
            exit()

    def DisconnectFromServer(self):
        print("disconnecting from server...")
        self.socket.close()

    def Input(self):
        while True:
            if self.is_sensitive:
                message = self.GetSensitiveInput()
            else:
                message = self.GetInput()

            self.SendMessage(message)

    def GetInput(self):
        return input()

    def GetSensitiveInput(self):
        return pwinput.pwinput()

    def SendMessage(self, message):
        header = f"{len(message):<{self.header_length}}"
        full_message = header + message
        try:
            self.socket.send(full_message.encode("utf-8"))
        except Exception as e:
            print(f"Error, could not send message: {e}")
            exit()

    def Listen(self):
        try:
            while True:
                header = self.socket.recv(self.header_length).decode("utf-8")

                if not header:
                    print("server disconnected")
                    break

                message_length = int(header)
                message = self.socket.recv(message_length).decode("utf-8")
                # check if message is a symmetric key
                if message.startswith("sym_key"):
                    print(f"received symmetric key: {message}")

                print("\033[H\033[J")
                print(message)

        except Exception as e:
            print(f"Error, could not receive message: {e}")
            exit()
