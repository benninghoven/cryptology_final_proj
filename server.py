import socket
import threading


def handle_client(client_socket):
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break
            print(f"Received message: {data}")

            # Echo the received message back to the client
            client_socket.send(data.encode("utf-8"))
        except Exception as e:
            print(f"Error: {e}")
            break

    # Close the client socket when done
    client_socket.close()


def start_server():
    # Set up the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 5555))
    server_socket.listen(5)
    print("Server listening on port 5555...")

    try:
        while True:
            # Accept incoming connections
            client_socket, address = server_socket.accept()
            print(f"Accepted connection from {address}")

            # Handle each client in a separate thread
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
