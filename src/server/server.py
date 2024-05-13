import socket
import threading
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


class Server:
    def __init__(self):
        self.connections = {}

        self.header_length = 10

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        print("server is listening on port " + config["top-secret"]["ServerPort"])
        self.socket.listen(int(config["top-secret"]["MaxConnections"]))

        self.Run()

    def Run(self):
        while True:
            conn, addr = self.socket.accept()
            # start a new thread to handle the connection
            c = threading.Thread(target=self.HandleIncomingSockets, args=(conn, addr))
            c.daemon = True
            c.start()
            print(f"Connection: {conn}\nAddr: {addr}")
            # This your ip?
            peer_name = conn.getpeername()
            self.connections[peer_name] = {"connection": conn,
                                           "address": addr,
                                           "thread": c
                                               }

    def HandleIncomingSockets(self, conn, addr):
        while True:
            try:
                message_header = conn.recv(self.header_length)
                if not len(message_header):
                    break

                message_length = int(message_header.decode("utf-8").strip())
                message = conn.recv(message_length).decode("utf-8")

                print(f"Received message from {addr}: {message}")

                # broadcast the message to all clients
                for connection in self.connections:
                    if connection != conn:
                        connection.send(message_header + message.encode("utf-8"))

            except Exception as e:
                print(f"An error occurred: {e}")
                break
