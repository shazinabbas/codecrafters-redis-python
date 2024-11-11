import socket
import threading

def main() -> None:
    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    while True:
        connection, address = server_socket.accept()
        print(f"Accepted connection - {address[0]}:{str(address[1])}")
        thread = threading.Thread(target=handle_connection, args=(connection,))
        thread.start()

def handle_connection(connection: socket.socket) -> None:
    with connection:
        while True:
            command = connection.recv(1024).decode()
            if not command:
                break  # Client disconnected
            print(f"Received - {command}")
            response = process_command(command)
            print(f"Responding with - {response}")
            connection.sendall(response.encode())

def process_command(command: str) -> str:
    parts = command.split("\r\n")
    if len(parts) < 4:
        return "-ERR Invalid command\r\n"
    
    try:
        # Parse RESP command
        arg_count = int(parts[0][1:])
        command_name = parts[2].upper()
        if command_name == "PING":
            return "+PONG\r\n"
        elif command_name == "ECHO" and arg_count == 2:
            echo_message = parts[4]
            return f"${len(echo_message)}\r\n{echo_message}\r\n"
        else:
            return "-ERR Unknown command\r\n"
    except (ValueError, IndexError) as e:
        print(f"Error processing command: {e}")
        return "-ERR Invalid command\r\n"

if __name__ == "__main__":
    main()
