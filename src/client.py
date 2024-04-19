import socket
import threading
from config import GetConfig

config = GetConfig()


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listeningThread = None

    def __del__(self):
        self.socket.close()

    def Listen(self):
        while True:
            response = self.socket.recv(1024).decode("utf-8")
            print(f"\tServer response: {response}")

    def Send(self, message):
        self.socket.send(message.encode("utf-8"))

    def Start(self):
        self.WelcomeMessage()

        try:
            self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))

            t1 = threading.Thread(target=self.Listen)
            t1.start()

            while True:
                message = input("Enter message: ")
                self.Send(message)

        except ConnectionRefusedError:
            print("is the server running?")
        except KeyboardInterrupt:
            print("closing client")

        finally:
            self.socket.close()

    def WelcomeMessage(self):
        try:
            with open("assets/logo.txt", "r") as f:
                print(f.read())

        except FileNotFoundError:
            print("Welcome to the chatroom\nNO FILE FOUND")


if __name__ == "__main__":
    client = Client()
    client.Start()
