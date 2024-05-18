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
        shell_sign = None
        with open(parent_dir + "shell_sign.txt", "r") as file:
            shell_sign = file.read()

        try:
            with open(parent_dir + filename, "r") as file:
                return file.read() + shell_sign

        except FileNotFoundError:
            print(f"File {filename} not found")
            return "No File Found" + shell_sign

    def HandleAdminConsole(self):
        while True:
            command = input("$ ")
            if command == "list":
                for ipaddress, client in self.online_clients.items():
                    print(f"  IP: {ipaddress}\tusername: {client.username}")
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
        elif state == STATES["login_password"]:
            self.HandleLoginPassword(clientname, message)
        elif state == STATES["register_username"]:
            self.HandleRegisterUsername(clientname, message)
        elif state == STATES["register_password"]:
            self.HandleRegisterPassword(clientname, message)
        elif state == STATES["reenter_password"]:
            self.HandleReenterPassword(clientname, message)
        elif state == STATES["main_menu"]:
            self.HandleMainMenu(clientname, message)
        elif state == STATES["ping_a_user"]:
            self.HandlePingUser(clientname, message)
        elif state == STATES["view_direct_messages"]:
            self.HandleViewDirectMessages(clientname, message)
        elif state == STATES["open_direct_message"]:
            pass

    def HandleInitialMenu(self, clientname, message):
        if message == "1":  # login
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("login_username.txt"))
            self.online_clients[clientname].state = STATES["login_username"]
        elif message == "2":  # create account
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("register_username.txt"))
            self.online_clients[clientname].state = STATES["register_username"]
        elif message == "3":  # exit
            # TODO: CRASHES SERVER
            # safely remove client from online_clients
            pass
        else:
            initial_menu_string = self.GetMenuString("initial_menu.txt")
            initial_menu_string += "Invalid input. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, initial_menu_string)

    def HandleLoginUsername(self, clientname, message):
        username = message
        if self.DoesUserExist(username):
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("login_password.txt"))
            self.online_clients[clientname].state = STATES["login_password"]
            self.online_clients[clientname].username = username
        else:
            login_username = self.GetMenuString("login_username.txt")
            login_username += "User does not exist. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, login_username)

    def HandleLoginPassword(self, clientname, message):
        password = message

        cursor = self.cnx.cursor()
        cursor.execute(f"SELECT hashed_password FROM users WHERE username = '{self.online_clients[clientname].username}'")
        hashed_password = cursor.fetchone()[0]
        cursor.close()

        if bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            cur_client = self.online_clients[clientname]
            main_menu_string = self.GetMenuString("main_menu.txt")
            main_menu_string += f"Welcome back, {cur_client.username}!\n"
            self.SendMessages(self.online_clients[clientname].conn, main_menu_string)
            cur_client.state = STATES["main_menu"]
        else:
            login_password = self.GetMenuString("login_password.txt")
            login_password += "Invalid password. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, login_password)

    def HandleRegisterUsername(self, clientname, message):
        potential_username = message
        if self.VetUsername(potential_username):
            if self.DoesUserExist(potential_username):
                register_username = self.GetMenuString("register_username.txt")
                register_username += "Username already exists. Please try again.\n"
                self.SendMessages(self.online_clients[clientname].conn, register_username)
            else:
                self.online_clients[clientname].username = potential_username
                self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("register_password.txt"))
                self.online_clients[clientname].state = STATES["register_password"]
        else:
            register_username = self.GetMenuString("register_username.txt")
            register_username += "Invalid username. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, register_username)

    def HandleRegisterPassword(self, clientname, message):
        potential_password = message
        if self.VetPassword(potential_password):
            self.online_clients[clientname].password = potential_password
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("reenter_password.txt"))
            self.online_clients[clientname].state = STATES["reenter_password"]

    def HandleReenterPassword(self, clientname, message):
        if message == self.online_clients[clientname].password:
            username = self.online_clients[clientname].username
            hashed_password = bcrypt.hashpw(self.online_clients[clientname].password.encode("utf-8"), bcrypt.gensalt())
            query = f"""INSERT INTO users (username, hashed_password)
            VALUES (
                    '{username}',
                    '{hashed_password.decode("utf-8")}'
                    )"""
            cursor = self.cnx.cursor()
            cursor.execute(query)
            self.cnx.commit()

            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("main_menu.txt"))
            self.online_clients[clientname].state = STATES["main_menu"]
        else:
            reenter_password_string = self.GetMenuString("reenter_password.txt")
            reenter_password_string += "Passwords do not match. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, reenter_password_string)
            self.online_clients[clientname].state = STATES["reenter_password"]

    def HandleMainMenu(self, clientname, message):
        if message == "1":
            self.online_clients[clientname].state = STATES["view_direct_messages"]
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("view_direct_messages.txt"))
        elif message == "2":
            self.SendMessages(self.online_clients[clientname].conn, "START A NEW CHAT")
        elif message == "3":
            self.online_clients[clientname].state = STATES["ping_a_user"]
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("ping_a_user.txt"))
        elif message == "4":
            self.SendMessages(self.online_clients[clientname].conn, "LOGOUT")
        else:
            main_menu_string = self.GetMenuString("main_menu.txt")
            main_menu_string += "Invalid input. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, main_menu_string)

    def HandleViewDirectMessages(self, clientname, message):
        if message == "back":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("main_menu.txt"))
            self.online_clients[clientname].state = STATES["main_menu"]
            return

        # fetch their history messages from the database
        previous_chats = {}
        # insert dumby chat
        previous_chats["dumby"] = ["This is a dumby chat", "This is a dumby chat", "This is a dumby chat"]
        previous_chats["dumby2"] = ["This is a dumby chat", "This is a dumby chat", "This is a dumby chat"]
        previous_chats["dumby3"] = ["This is a dumby chat", "This is a dumby chat", "This is a dumby chat"]

        view_direct_messages_string = self.GetMenuString("view_direct_messages.txt")

        for chat in previous_chats:
            view_direct_messages_string += f"{chat}\n"

        self.SendMessages(self.online_clients[clientname].conn, view_direct_messages_string)

    def HandlePingUser(self, clientname, message):
        ping_a_user_string = self.GetMenuString("ping_a_user.txt")

        if message == "back":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("main_menu.txt"))
            self.online_clients[clientname].state = STATES["main_menu"]
            return

        if self.DoesUserExist(message):
            if self.PingUser(message):
                ping_a_user_string += f"{message} is currently online\n\n"
                self.SendMessages(self.online_clients[clientname].conn, ping_a_user_string)
            else:
                ping_a_user_string += f"{message} is currently offline\n\n"
                self.SendMessages(self.online_clients[clientname].conn, ping_a_user_string)
        else:
            ping_a_user_string += "User does not exist. Please try again.\n\n"
            self.SendMessages(self.online_clients[clientname].conn, ping_a_user_string)

    def VetPassword(self, password):
        return " " not in password and len(password) < 16

    def VetUsername(self, username):
        return " " not in username and len(username) < 16

    def PingUser(self, username):
        for ipaddress, client in self.online_clients.items():
            if client.username == username:
                return True
        return False

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
