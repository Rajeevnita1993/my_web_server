import signal
import socket
import sys
import os
import threading
import time

def signal_handler(sig, frame):
    print("\nServer is shutting down...")
    sys.exit(0)

def handle_client(client_socket, client_address, www_dir):
    print(f"Connection from {client_address}")
    thread_id = threading.get_ident()

    try:
        # Receive the request data
        request_data = client_socket.recv(1024).decode('utf-8')
        print(f"Request data:\n{request_data}")

        # Parse the first line of request
        request_line = request_data.splitlines()[0]
        request_type, path, http_version = request_line.split()
        print("path: ", path)

        # Default to serving index.html if path is /
        if path == '/':
            path = '/index.html'

        # Construct the full path to the requested file
        requested_file_path = os.path.join(www_dir, path.lstrip('/'))

        # Ensure the requested file is within the wwww directory
        www_dir_abs = os.path.abspath(www_dir)
        requested_file_path_abs = os.path.abspath(requested_file_path)
        if os.path.commonpath([www_dir_abs, requested_file_path_abs]) == www_dir_abs:
            if os.path.exists(requested_file_path_abs) and os.path.isfile(requested_file_path_abs):
                with open(requested_file_path_abs, 'r', encoding='utf-8') as file:
                    reponse_body = file.read()
                response = f"HTTP/1.1 200 OK\r\n\r\n{reponse_body}"
            else:
                reponse_body = "Not Found"
                response = f"HTTP/1.1 404 Not Found\r\n\r\n{reponse_body}"
        else:
            reponse_body = "Forbidden"
            response = f"HTTP/1.1 403 Forbidden\r\n\r\n{reponse_body}"

        # Send the response back to the client
        client_socket.sendall(response.encode('utf-8'))

        # Sleep for 20 seconds to simulate processing time
        print(f"Path: {path}, Thread Id: {thread_id}")
        time.sleep(20)

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        # Close the client connection
        client_socket.close()



def start_server(www_dir):
    # Create a socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Reuse the socket address to avoid "Address already in use" error
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to the address and port
    server_socket.bind(('127.0.0.1', 8080))

    # Listen for connection. Allow up to 5 pending connections
    server_socket.listen(5)

    print("server is listening on port 8080...")

    while True:
        try:
            # Accept an incoming connection
            client_socket, client_address = server_socket.accept()

            # Create a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, www_dir))
            client_thread.start()
            

        except KeyboardInterrupt:
            print("\nServer is shutting down...")
            server_socket.close()
            sys.exit(0)

def main():
    if len(sys.argv) != 2:
        print("Usage: python my_server.py <www_directory>")
        sys.exit(1)

    www_dir = sys.argv[1]
    if not os.path.isdir(www_dir):
        print(f"Error: {www_dir} is not a valid directory")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    start_server(www_dir)

if __name__ == "__main__":
    main()