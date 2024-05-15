import socket
import threading
import configparser

config = configparser.ConfigParser()
config.read("../config.ini")


def PeerToStringName(conn):
    peername = conn.getpeername()
    return f"{peername[0]}:{peername[1]}"


class Server:
    def __init__(self):
        self.live_connections = {}
        self.header_length = int(config["top-secret"]["HeaderLength"])
        self.Start()
        self.ListenForConnections()

    def Start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        print("server is listening on port " + config["top-secret"]["ServerPort"])
        self.socket.listen(int(config["top-secret"]["MaxConnections"]))

    def ListenForConnections(self):
        while True:
            conn, addr = self.socket.accept()
            # start a new thread to handle the connection
            c = threading.Thread(target=self.HandleIncomingSockets, args=(conn, addr))
            c.daemon = True
            c.start()

    def HandleIncomingSockets(self, conn, addr):
        while True:
            try:
                print(f"Header Length {self.header_length}Bytes")

                message_header = conn.recv(self.header_length)
                # get's 4bytes

                print(f"message header: {message_header}")

            except Exception as e:
                print(f"Error: {e}")
                break

        conn.close()
        print("connection closed by server")
