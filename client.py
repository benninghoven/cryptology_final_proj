import socket

def start_client():
    # Set up the client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 5555))

    try:
        while True:
            # Send data to the server
            message = input("Enter message: ")
            client_socket.send(message.encode("utf-8"))

            # Receive response from the server
            response = client_socket.recv(1024).decode("utf-8")
            print(f"Server response: {response}")
    except KeyboardInterrupt:
        print("Client shutting down...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()

