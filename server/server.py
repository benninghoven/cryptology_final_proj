import socket
import threading
import configparser

config = configparser.ConfigParser()
config.read("../config.ini")


def PeerNameToStringName(conn):
    peername = conn.getpeername()
    return f"{peername[0]}:{peername[1]}"


STATES = {
    "login_menu": 0,
    "entering_username": 1,
    "entering_password": 2,
    "creating_account": 3,
    "logging_in": 4,
    "logged_in": 5,
    "main_menu": 6,
}


class ActiveClient:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.name = PeerNameToStringName(self.conn)
        self.state = None
        self.thread = None


class Server:
    def __init__(self):
        self.online_clients = {}
        self.header_length = int(config["top-secret"]["HeaderLength"])
        self.Start()

    def Start(self):
        print("server is starting")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        self.socket.listen(int(config["top-secret"]["MaxConnections"]))

        self.admin_console_thread = threading.Thread(target=self.HandleAdminConsole)
        self.admin_console_thread.start()

        self.ListenForConnections()

    def HandleAdminConsole(self):
        while True:
            command = input("$ ")
            if command == "list":
                print("list of connected clients:")
                for client in self.live_connections:
                    print(f"{client.name}")
            elif command == "exit":
                print("shutting down server...")
                exit()
            else:
                print("invalid command")

    def ListenForConnections(self):
        print("listening for connections...")
        while True:
            conn, addr = self.socket.accept()
            current_client = ActiveClient(conn, addr)
            self.online_clients[current_client.name] = current_client
            print(f"{current_client.name} connected")
            current_client.thread = threading.Thread(target=self.HandleIncomingSockets, args=(current_client.name,))
            current_client.thread.start()

    def HandleIncomingSockets(self, clientname):
        # start with handshake protocol
        # then start listening to what they say and reply based on state
        cur_client = self.online_clients[clientname]
        while True:
            header = cur_client.conn.recv(self.header_length)
            if not len(header):
                print(f"{clientname} disconnected")
                del self.online_clients[clientname]
                break
            message = cur_client.conn.recv(int(header))
            print(f"{clientname}: {message}")

    def SendMessages(self, conn, message):
        # attach the header to the message
        message = f"{len(message):<{self.header_length}}".encode("utf-8") + message.encode("utf-8")
        print(f"Sending message: {message}")
        conn.send(message)



    def LoginMenu(self, current_connection):
        message = "You are now connected to the server."
        #self.SendMessages(current_connection.conn, message)
