# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True) # Open the socket
    server_socket.listen() # Start listening

    while True:
        client, address = server_socket.accept() # Accept incoming connections
        client.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf8"))
if __name__ == "__main__":
    main()
