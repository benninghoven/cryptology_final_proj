import socket
import threading
from config import GetConfig

config = GetConfig()


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Start()

    def __del__(self):
        self.socket.close()

    def Listen(self):
        try:
            while True:
                response = self.socket.recv(1024).decode("utf-8")
                print(response)

        except Exception as e:
            print(e)
            exit()

    def Send(self, message):
        self.socket.send(message.encode("utf-8"))

    def Start(self):
        try:
            print("connecting to server...")
            self.socket.connect((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
            print("connected to server")

            listening_thread = threading.Thread(target=self.Listen)
            listening_thread.start()

            while True:
                message = input("Enter message: ")
                self.Send(message)

        except ConnectionRefusedError:
            print("is the server running?")
        except KeyboardInterrupt:
            print("closing client")

        finally:
            self.socket.close()


if __name__ == "__main__":
    client = Client()
