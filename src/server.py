import socket
import threading
from config import GetConfig

CONNECTION_STATES = {
    "INIT": 0,
    "LOGIN": 1,
    "LOGGED_IN": 2
}


class Connection:
    def __init__(self, socket, address):
        self.socket = socket
        self.address = address
        self.username = None
        self.state = "INIT"

    def __str__(self):
        return f"{self.address} - {self.username}"


class Server:
    def __init__(self):
        self.connections = []
        self.config = GetConfig()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = int(self.config["top-secret"]["ServerPort"])
        self.socket.bind(("localhost", self.port))
        self.socket.listen(int(self.config["top-secret"]["MaxConnections"]))

        self.Start()

    def __del__(self):
        self.socket.close()

    def ConnectionHandler(self, client_socket, address):
        connection = Connection(client_socket, address)
        self.connections.append(connection)

        print(f"new connection from {address}")

        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8")

                if not data:
                    break

                if connection.state == CONNECTION_STATES["INIT"]:
                    if data == "login":
                        connection.state = CONNECTION_STATES["LOGIN"]
                        client_socket.send("Enter username: ".encode("utf-8"))
                    else:
                        client_socket.send("Invalid command".encode("utf-8"))

                elif connection.state == CONNECTION_STATES["LOGIN"]:
                    connection.username = data
                    connection.state = CONNECTION_STATES["LOGGED_IN"]
                    client_socket.send("Welcome".encode("utf-8"))

                    ClientMenu(connection)

            except Exception as e:
                print(f"Error: {e}")
                break

        print(f"Connection from {address} closed")
        self.connections.remove(connection)

    def Start(self):
        print("server starting")

        admin_thread = threading.Thread(target=self.Admin_CLI)
        admin_thread.start()

        print("handling incoming connections")
        try:
            while True:

                client_socket, address = self.socket.accept()

                connection_handler_thread = threading.Thread(target=self.ConnectionHandler, args=(client_socket, address))
                connection_handler_thread.start()

        except KeyboardInterrupt:
            print("shutting server down")
            exit()

    def Admin_CLI(self):

        print("Admin CLI started")

        while True:
            try:
                command = input("$ ")
                if command == "shutdown":
                    print("shutting down server")
                    self.socket.close()
                    exit()
                    break
                elif command == "ls":
                    print("==== active connections ====")
                    for connection in self.connections:
                        print(f"{connection}")
                elif "say" in command:
                    command = command.split(" ")
                    for connection in self.connections:
                        connection.socket.send(" ".join(["server:"] + command[1:]).encode("utf-8"))
                else:
                    print("Invalid command")

            except Exception as e:
                print(f"Error: {e}")
                break


def ClientMenu(client):

    print(f"Welcome {client}!")
    print("1. Login")
    print("2. Create Account")
    print("3. Exit")

    while True:

        try:
            choice = int(input("Enter choice: "))

            if choice == 1:
                friends = client.list_friends()
                print("==== Friends ====")
                for friend in friends:
                    print(friend)
            elif choice == 2:
                friend = input("Enter friend: ")
                client.add_friend(friend)
                print(f"{friend} added to friends")
            elif choice == 3:
                exit()
            else:
                print("Invalid choice")

        except Exception as e:
            print(f"Error: {e}")
            break


if __name__ == "__main__":
    Server()
