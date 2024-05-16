import socket
import threading
import configparser
import mysql.connector

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
        # need to use a lock for threads on online_clients
        self.online_clients = {}
        self.header_length = int(config["top-secret"]["HeaderLength"])
        self.Start()

    def Start(self):
        self.ConnectToDatabase()
        print("server is starting")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        self.socket.listen(int(config["top-secret"]["MaxConnections"]))

        self.admin_console_thread = threading.Thread(target=self.HandleAdminConsole)
        self.admin_console_thread.start()

        self.ListenForConnections()

    def ConnectToDatabase(self):
        try:
            self.cnx = mysql.connector.connect(
                    user='user',
                    password='password',
                    host='127.0.0.1',
                    database='robco_database')
        except mysql.connector.Error as e:
            print(f"Error connecting to database: {e}")
            exit()

    def HandleAdminConsole(self):
        while True:
            command = input("$ ")
            if command == "list":
                print("list of connected clients:")
                for client in self.live_connections:
                    print(f"{client.name}")
            elif command == "exit":
                print("shutting down server...")
                self.cnx.close()
                exit()
            else:
                print("invalid command")

    def ListenForConnections(self):
        print("listening for connections...")
        while True:
            conn, addr = self.socket.accept()
            current_client = ActiveClient(conn, addr)
            if current_client.name in self.online_clients:
                print(f"{current_client.name} is already connected")
                continue
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
            try:
                message = message.decode("utf-8")
            except Exception as e:
                print(f"Error decoding message: {e}")

            self.HandleMessage(clientname, message)

    # STATES = {
    #    "login_menu": 0,
    #    "entering_username": 1,
    #    "entering_password": 2,
    #    "creating_account": 3,
    #    "logging_in": 4,
    #    "logged_in": 5,
    #    "main_menu": 6,
    # }


    def HandleMessage(self, clientname, message):

        cur_client = self.online_clients[clientname]
        state = cur_client.state

        if state is None:
            self.SendMessages(cur_client.conn, """
Welcome to the server!
1. Login
2. Create Account
3. Exit
""")
            if message == "1":
                cur_client.state = STATES["login_menu"]
            elif message == "2":
                cur_client.state = STATES["creating_account"]
            elif message == "3":
                pass

        elif state == STATES["login_menu"]:
            self.SendMessages(cur_client.conn, "Enter your username: ")
            pass
        elif state == STATES["logging_in"]:
            pass
        elif state == STATES["creating_account"]:
            pass
        elif state == STATES["entering_username"]:
            pass
        elif state == STATES["entering_password"]:
            pass
            pass
        elif state == STATES["logged_in"]:
            pass
        elif state == STATES["main_menu"]:
            pass


    def DoesUserExist(self, username):
        cursor = self.cnx.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
        if cursor.fetchone():
            return True
        return False

    def SendMessages(self, conn, message):
        message = f"{len(message):<{self.header_length}}".encode("utf-8") + message.encode("utf-8")
        try:
            conn.send(message)
        except Exception as e:
            print(f"Error sending message: {e}")

    def LoginMenu(self, current_connection):
        message = "You are now connected to the server."
        #self.SendMessages(current_connection.conn, message)
