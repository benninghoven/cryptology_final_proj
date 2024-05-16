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
        header = f"{len(message):<{self.header_length}}"
        print(f"HEADER: {header}")
        full_message = header + message
        print(f"FULL MESSAGE: {full_message}")
        try:
            self.socket.send(full_message.encode("utf-8"))
        except Exception as e:
            print(f"Error: {e}")
            exit()

    def Listen(self):
        print("listening for messages")

        try:
            while True:
                header = self.socket.recv(self.header_length).decode("utf-8")
                if not header:
                    print("server disconnected")
                    break
                message_length = int(header)
                message = self.socket.recv(message_length).decode("utf-8")
                print(f"server: {message}")

        except Exception as e:
            print(e)
            exit()
