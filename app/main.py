import socket

def main():
    print("Logs from your program will appear here!")

    # Create a server socket that listens on localhost, port 6379
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    client, addr = server_socket.accept()  # Wait for a client to connect
    print(f"Connected by {addr}")

    try:
        while True:
            data = client.recv(1024)  # Receive data from client
            if not data:
                break  # Exit the loop if there's no more data (client disconnected)
            print(f"Received data: {data}")

            # Send a response back for each command received
            client.sendall(b"+PONG\r\n")
    finally:
        client.close()  # Close the client connection after loop exits
        server_socket.close()  # Close the server socket when done

if __name__ == "__main__":
    main()
