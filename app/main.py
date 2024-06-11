import socket


def main() -> None:
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True) # Open the socket
    server_socket.listen() # Start listening
    
    while True:
        client, _ = server_socket.accept() # Accept incoming connections
        # client.send("HTTP/1.1 200 OK\r\n\r\n".encode("utf8"))

        req_msg:str = ""
        end_of_msg:bool = False
        while not end_of_msg:
            req_buf:str = client.recv(1024).decode("utf8")
            if len(req_buf) > 0:
                end_of_msg = True
            req_msg += req_buf
            
        print(f"Request Message: {req_msg}")

        http_req:list = req_msg.split(CRLF)
        http_req_line:str = http_req[0]
        req_line_parts:list = http_req_line.split(" ")

        match req_line_parts[1]:
            case "/":
                print("OK")
                client.sendall(f"HTTP/1.1 200 OK{CRLF}{CRLF}".encode("utf8"))
            case _:
                print("Not Found")
                client.sendall(f"HTTP/1.1 404 Not Found{CRLF}{CRLF}".encode("utf8"))


if __name__ == "__main__":
    CRLF:str = "\r\n"
    main()
