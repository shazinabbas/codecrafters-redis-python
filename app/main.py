import socket
import threading
import time

# Global dictionary for in-memory key-value storage and expiry times
data_store = {}
expiry_store = {}

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
        
        # Handle PING command
        if command_name == "PING":
            return "+PONG\r\n"
        
        # Handle ECHO command
        elif command_name == "ECHO" and arg_count == 2:
            echo_message = parts[4]
            return f"${len(echo_message)}\r\n{echo_message}\r\n"
        
        # Handle SET command with optional PX (expiry)
        elif command_name == "SET" and arg_count >= 3:
            key = parts[4]
            value = parts[6]
            data_store[key] = value
            
            # Check for PX (expiry) option
            if arg_count == 5 and parts[8].upper() == "PX":
                expiry_time_ms = int(parts[10])
                expiry_store[key] = time.time() + (expiry_time_ms / 1000)
            
            return "+OK\r\n"
        
        # Handle GET command with expiry check
        elif command_name == "GET" and arg_count == 2:
            key = parts[4]
            if key in data_store:
                # Check if the key has expired
                if key in expiry_store and time.time() >= expiry_store[key]:
                    # Key has expired
                    del data_store[key]
                    del expiry_store[key]
                    return "$-1\r\n"  # Null bulk string
                value = data_store[key]
                return f"${len(value)}\r\n{value}\r\n"
            else:
                return "$-1\r\n"  # Null bulk string for non-existent key
        
        # If command not recognized
        return "-ERR Unknown command\r\n"
    
    except (ValueError, IndexError) as e:
        print(f"Error processing command: {e}")
        return "-ERR Invalid command\r\n"

if __name__ == "__main__":
    main()
