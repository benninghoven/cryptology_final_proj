import socket
import threading
from config import GetConfig


config = GetConfig()


def WelcomeMessage():
    return "Welcome to the server".encode("utf-8")


def handle_client(client_socket):
    client_socket.send(WelcomeMessage())
    while True:
        try:
            # WAITS HERE
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break
            print(f"Received message: {data}")

            client_socket.send(data.encode("utf-8"))
        except Exception as e:
            print(f"Error: {e}")
            break

    client_socket.close()




def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", int(config["top-secret"]["port"])))



def start_server():
    port = int(config["top-secret"]["port"])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen(5)
    print(f"Server listening on port {port}...")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"Accepted connection from {address}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
