import socket
import threading
import configparser
import mysql.connector
from datetime import datetime
from states import STATES
from activeclient import ActiveClient

import bcrypt

config = configparser.ConfigParser()
config.read("../config.ini")


class Server:
    def __init__(self):
        # need to use a lock for threads on online_clients
        self.online_clients = {}
        self.header_length = int(config["top-secret"]["HeaderLength"])

        self.socket = None
        self.admin_console_thread = None
        self.cnx = None

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

    def GetMenuString(self, filename):
        parent_dir = "strings/"
        try:
            with open(parent_dir + filename, "r") as file:
                return file.read()
        except FileNotFoundError:
            print(f"File {filename} not found")
            return "No File Found"

    def HandleAdminConsole(self):
        while True:
            command = input("$ ")
            if command == "list":
                print("list of connected clients:")
                for client in self.online_clients:
                    print(f"{client.name}")
            elif command == "exit":
                print("shutting down server...")
                self.cnx.close()
                exit()
            else:
                print("invalid command")

    def ListenForConnections(self):
        print("listening for connections")
        while True:
            conn, addr = self.socket.accept()

            # recieved a new connection!
            current_client = ActiveClient(conn, addr)
            self.online_clients[current_client.name] = current_client

            first_message_to_client = self.GetMenuString("initial_menu.txt")
            self.SendMessages(current_client.conn, first_message_to_client)

            current_client.thread = threading.Thread(target=self.HandleIncomingSockets, args=(current_client.name,))
            current_client.thread.start()

    def HandleIncomingSockets(self, clientname):
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

    def HandleMessage(self, clientname, message):

        cur_client = self.online_clients[clientname]
        state = cur_client.state
        # get the state key
        state_key = list(STATES.keys())[list(STATES.values()).index(state)]
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{cur_time}] {state_key} {clientname}: {message}")

        if state == STATES["initial_menu"]:
            self.HandleInitialMenu(clientname, message)
        elif state == STATES["login_username"]:
            self.HandleLoginUsername(clientname, message)
        elif state == STATES["register_username"]:
            self.HandleRegisterUsername(clientname, message)

    def VetPassword(self, password):
        return " " not in password and len(password) < 16

    def VetUsername(self, username):
        return " " not in username and len(username) < 16

    def HandleInitialMenu(self, clientname, message):
        if message == "1":
            self.online_clients[clientname].state = STATES["login_username"]
            login_message = self.GetMenuString("login_message.txt")
            self.SendMessages(self.online_clients[clientname].conn, login_message)
        elif message == "2":
            self.online_clients[clientname].state = STATES["register_username"]
            self.SendMessages(self.online_clients[clientname].conn, "Usernames must contain no whitespace and be less than 16 characters.\nEnter your desired username: ")
        else:
            self.SendMessages(self.online_clients[clientname].conn, "Invalid input. Please try again.")

    def HandleLoginUsername(self, clientname, message):
        cur_client = self.online_clients[clientname]
        if message == "exit":
            cur_client.state = STATES["initial_menu"]
            initial_menu = self.GetMenuString("initial_menu.txt")
            self.SendMessages(cur_client.conn, initial_menu)
            return
        # check if username exist in the database
        if self.DoesUserExist(message):
            # username found! time to enter your password
            cur_client.username = message
            cur_client.state = STATES["login_password"]
        else:
            self.SendMessages(cur_client.conn, "Username not found. Please enter your username or type 'exit' to return to previous menu: ")

    def HandleRegisterUsername(self, clientname, message):

        if self.DoesUserExist(message):
            self.SendMessages(self.online_clients[clientname].conn, "User already exists. Enter your username: ")
        else:
            self.SendMessages(self.online_clients[clientname].conn, "Enter your password: ")
            self.online_clients[clientname].state = STATES["register_password"]

    def PingUser(self, username):
        return self.online_clients[username]

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
