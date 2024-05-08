import socket
import threading
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


class Server:
    def __init__(self):
        self.connections = []
        # type of socket will behost:port and TCP protocol
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind socket to the address and port
        self.socket.bind((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        # listen for x ammount of connections
        print("Server is listening on port " + config["top-secret"]["ServerPort"])
        self.socket.listen(int(config["top-secret"]["MaxConnections"]))

        self.Run()

    def Run(self):
        while True:
            conn, addr = self.socket.accept()
            # start a new thread to handle the connection
            c = threading.Thread(target=self.HandleIncomingSockets, args=(conn, addr))
            c.daemon = True
            c.start()

            self.connections.append(conn)

    def HandleIncomingSockets(self, conn, addr):
        # handle incoming connections, know what state they are in
        while True:
            data = conn.recv(1024).decode()
            print(f"{addr} {data}")

            if not data:
                break

        print(f"{addr} disconnected")


if __name__ == "__main__":
    Server()
