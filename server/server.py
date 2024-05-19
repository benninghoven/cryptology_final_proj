import socket
import threading
import configparser
import mysql.connector
import bcrypt
from datetime import datetime
from states import STATES
from activeclient import ActiveClient


config = configparser.ConfigParser()
config.read("../config.ini")


class Server:
    def __init__(self):
        self.online_clients = {}
        self.header_length = int(config["top-secret"]["HeaderLength"])
        self.socket = None
        self.admin_console_thread = None
        self.cnx = None

        self.Start()

    def Start(self):
        print("Server is starting...")
        self.ConnectToDatabase()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((config["top-secret"]["ServerIP"], int(config["top-secret"]["ServerPort"])))
        self.socket.listen(int(config["top-secret"]["MaxConnections"]))

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

    def ListenForConnections(self):
        while True:
            conn, addr = self.socket.accept()
            current_client = ActiveClient(conn, addr)
            self.online_clients[current_client.peername] = current_client
            current_client.thread = threading.Thread(target=self.HandleIncomingSockets, args=(current_client.peername,))
            current_client.thread.start()

    def HandleIncomingSockets(self, clientname):
        cur_client = self.online_clients[clientname]

        cur_client.state = STATES.INITIAL_MENU
        first_message_to_client = self.GetMenuString("initial_menu.txt")
        self.SendMessages(cur_client.conn, first_message_to_client)

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
                message = "Error decoding message"

            self.HandleMessage(clientname, message)

    def HandleMessage(self, clientname, message):
        cur_client = self.online_clients[clientname]
        state = cur_client.state
        # get the state key
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if cur_client.username:
            print(f"[{cur_time}] {state} {cur_client.username}: {message}")
        else:
            print(f"[{cur_time}] {state} {clientname}: {message}")

        if state == STATES.INITIAL_MENU:
            self.HandleInitialMenu(clientname, message)
        elif state == STATES.LOGIN_USERNAME:
            self.HandleLoginUsername(clientname, message)
        elif state == STATES.LOGIN_PASSWORD:
            self.HandleLoginPassword(clientname, message)
        elif state == STATES.REGISTER_USERNAME:
            self.HandleRegisterUsername(clientname, message)
        elif state == STATES.REGISTER_PASSWORD:
            self.HandleRegisterPassword(clientname, message)
        elif state == STATES.REENTER_PASSWORD:
            self.HandleReenterPassword(clientname, message)
        elif state == STATES.MAIN_MENU:
            self.HandleMainMenu(clientname, message)
        elif state == STATES.VIEW_DIRECT_MESSAGES:
            self.HandleViewDirectMessages(clientname, message)
        elif state == STATES.OPEN_DIRECT_MESSAGE:
            self.HandleOpenDirectMessage(clientname, message)
        elif state == STATES.PING_A_USER:
            self.HandlePingUser(clientname, message)
        elif state == STATES.STARTING_A_NEW_CHAT:
            self.HandleStartingANewChat(clientname, message)
        else:
            self.sendMessages(cur_client.conn, "Invalid state")

    def HandleInitialMenu(self, clientname, message):
        if message == "1":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("login_username.txt"))
            self.online_clients[clientname].state = STATES.LOGIN_USERNAME
        elif message == "2":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("register_username.txt"))
            self.online_clients[clientname].state = STATES.REGISTER_USERNAME
        elif message == "3":  # exit
            self.SendMessages(self.online_clients[clientname].conn, "Goodbye!")
        else:
            initial_menu_string = self.GetMenuString("initial_menu.txt")
            initial_menu_string += "Invalid input. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, initial_menu_string)

    def HandleLoginUsername(self, clientname, message):
        username = message
        if self.DoesUserExist(username):
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("login_password.txt"))
            self.online_clients[clientname].state = STATES.LOGIN_PASSWORD
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
            cur_client.state = STATES.MAIN_MENU
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
                self.online_clients[clientname].state = STATES.REGISTER_PASSWORD
        else:
            register_username = self.GetMenuString("register_username.txt")
            register_username += "Invalid username. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, register_username)

    def HandleRegisterPassword(self, clientname, message):
        potential_password = message
        if self.VetPassword(potential_password):
            self.online_clients[clientname].password = potential_password
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("reenter_password.txt"))
            self.online_clients[clientname].state = STATES.REENTER_PASSWORD

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
            main_menu_string = self.GetMenuString("main_menu.txt")
            cur_client = self.online_clients[clientname]
            main_menu_string += f"Welcome back, {cur_client.username}!\n"
            self.SendMessages(self.online_clients[clientname].conn, main_menu_string)
            self.online_clients[clientname].state = STATES.MAIN_MENU
        else:
            reenter_password_string = self.GetMenuString("reenter_password.txt")
            reenter_password_string += "Passwords do not match. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, reenter_password_string)
            self.online_clients[clientname].state = STATES.REENTER_PASSWORD

    def HandleMainMenu(self, clientname, message):
        if message == "1":
            self.online_clients[clientname].state = STATES.VIEW_DIRECT_MESSAGES
            view_direct_messages_string = self.GetMenuString("view_direct_messages.txt")
            view_direct_messages_string += self.GetDirectMessageList(self.online_clients[clientname].username)
            self.SendMessages(self.online_clients[clientname].conn, view_direct_messages_string)
        elif message == "2":
            self.online_clients[clientname].state = STATES.STARTING_A_NEW_CHAT
            start_a_new_chat_string = self.GetMenuString("start_a_new_chat.txt")
            self.SendMessages(self.online_clients[clientname].conn, start_a_new_chat_string)
        elif message == "3":
            self.online_clients[clientname].state = STATES.PING_A_USER
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("ping_a_user.txt"))
        elif message == "4":
            self.SendMessages(self.online_clients[clientname].conn, "LOGOUT")
        else:
            main_menu_string = self.GetMenuString("main_menu.txt")
            main_menu_string += "Invalid input. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, main_menu_string)

    def GetDirectMessageList(self, username):
        query = f"""
        SELECT user1, user2 FROM chat_histories
        WHERE user1 = '{username}'
        OR user2 = '{username}'
        """
        cursor = self.cnx.cursor()
        cursor.execute(query)
        chat_histories = cursor.fetchall()
        cursor.close()

        recently_chatted_with = ""

        for chat in chat_histories:
            if chat[0] == username:
                other_user = chat[1]
            else:
                other_user = chat[0]

            if self.PingUser(other_user):
                recently_chatted_with += f"{other_user} *\n"
            else:
                recently_chatted_with += f"{other_user}\n"

        return recently_chatted_with

    def HandleViewDirectMessages(self, clientname, message):
        cur_client = self.online_clients[clientname]

        if message == "!back":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("main_menu.txt"))
            self.online_clients[clientname].state = STATES.MAIN_MENU
            return

        view_direct_messages_string = self.GetMenuString("view_direct_messages.txt")
        view_direct_messages_string += self.GetDirectMessageList(cur_client.username)

        potential_user = message
        if self.DoesUserExist(potential_user):
            self.online_clients[clientname].state = STATES.OPEN_DIRECT_MESSAGE
            self.online_clients[clientname].chatting_with = potential_user
            self.SendMessages(self.online_clients[clientname].conn,
                              view_direct_messages_string + self.GetChatHistory(cur_client.username, potential_user)
                              )
        else:
            self.SendMessages(self.online_clients[clientname].conn, view_direct_messages_string)

    def HandleOpenDirectMessage(self, clientname, message):
        if message == "!back":
            view_direct_messages_string = self.GetMenuString("view_direct_messages.txt")
            view_direct_messages_string += self.GetDirectMessageList(self.online_clients[clientname].username)
            self.SendMessages(self.online_clients[clientname].conn, view_direct_messages_string)
            self.online_clients[clientname].state = STATES.VIEW_DIRECT_MESSAGES
            return

        cur_client = self.online_clients[clientname]

        chat_history = self.GetChatHistory(cur_client.username, cur_client.chatting_with)

        #  message crashes sql if message has a ' in it
        if "'" in message:
            message = message.replace("'", "")

        if chat_history == "Beggining of chat\n":
            print("inserting into database")

            chat_history += f"{cur_client.username}: {message}\n"
            query = f"""INSERT INTO chat_histories (user1, user2, chat)
            VALUES (
                    LEAST('{cur_client.username}', '{cur_client.chatting_with}'),
                    GREATEST('{cur_client.username}', '{cur_client.chatting_with}'),
                    '{chat_history}'
                    )"""
        else:
            chat_history += f"{cur_client.username}: {message}\n"
            least = min(cur_client.username, cur_client.chatting_with)
            greatest = max(cur_client.username, cur_client.chatting_with)
            query = f"""UPDATE chat_histories
            SET chat = '{chat_history}'
            WHERE (user1 = '{least}' AND user2 = '{greatest}')
            """

        view_direct_messages_string = self.GetMenuString("view_direct_messages.txt")

        for chat in chat_history.split("\n"):
            view_direct_messages_string += chat + "\n"

        cursor = self.cnx.cursor()
        cursor.execute(query)
        self.cnx.commit()

        # need to send the message to the other user if they are also in the same state chatting with the same person
        for ipaddress, client in self.online_clients.items():
            if client.username == cur_client.chatting_with and client.state == STATES.OPEN_DIRECT_MESSAGE:
                self.SendMessages(client.conn, view_direct_messages_string)

        self.SendMessages(self.online_clients[clientname].conn, view_direct_messages_string)

    def HandlePingUser(self, clientname, message):
        ping_a_user_string = self.GetMenuString("ping_a_user.txt")

        if message == "!back":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("main_menu.txt"))
            self.online_clients[clientname].state = STATES.MAIN_MENU
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

    def HandleStartingANewChat(self, clientname, message):
        print(f"STARTING A NEW CHAT WITH {message}")
        if message == "!back":
            self.SendMessages(self.online_clients[clientname].conn, self.GetMenuString("main_menu.txt"))
            self.online_clients[clientname].state = STATES.MAIN_MENU
            return

        cur_client = self.online_clients[clientname]

        if message == cur_client.username:
            starting_a_new_chat_string = self.GetMenuString("start_a_new_chat.txt")
            starting_a_new_chat_string += "You cannot start a chat with yourself. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, starting_a_new_chat_string)
            return

        if self.DoesUserExist(message):
            open_direct_message_string = self.GetMenuString("open_direct_message.txt")

            cur_client.state = STATES.OPEN_DIRECT_MESSAGE
            cur_client.chatting_with = message

            print(f"{cur_client.username} is now chatting with {cur_client.chatting_with}")

            self.SendMessages(
                    self.online_clients[clientname].conn,
                    open_direct_message_string + self.GetChatHistory(cur_client.username, cur_client.chatting_with)
                    )

        else:
            starting_a_new_chat_string = self.GetMenuString("start_a_new_chat.txt")
            starting_a_new_chat_string += "User does not exist. Please try again.\n"
            self.SendMessages(self.online_clients[clientname].conn, starting_a_new_chat_string)

    def GetChatHistory(self, username, chatting_with):
        query = f"""
        SELECT chat FROM chat_histories
        WHERE (user1 = LEAST('{username}', '{chatting_with}')
        AND user2 = GREATEST('{username}', '{chatting_with}')
               )"""
        cursor = self.cnx.cursor()
        cursor.execute(query)

        chat_history = cursor.fetchall()
        if chat_history:
            print(f"CHAT HISTORY FROM DATABASE: {chat_history}")
            chat_history = chat_history[0][0]
        else:
            chat_history = "Beggining of chat\n"

        return chat_history

    def OpenDirectMessage(self, clientname, message):
        print(f"OPENING DIRECT MESSAGE WITH {message}")
        cur_client = self.online_clients[clientname]
        # generate a fake list of contacts
        recently_chatted_with = ["user1", "user2", "user3"]
        open_direct_message_string = self.GetMenuString("open_direct_message.txt")
        for user in recently_chatted_with:
            # if the user is online, append an asterisk
            open_direct_message_string += f"{user}\n"
        self.SendMessages(cur_client.conn, open_direct_message_string)

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
