import sys
import socket
from threading import Thread
from pathlib import Path

def parse_request(http_msg:str) -> dict:
    http_req:list = http_msg.split(CRLF*2)
    
    # Parse HTTP request line
    req_line:str = http_req[0].split(CRLF)[0]
    split_req_line:list = req_line.split(" ")

    # Get HTTP headers
    http_headers:list = http_req[0].split(CRLF)[1:]

    parsed_msg = {
        "http_version": split_req_line[2],
        "verb": split_req_line[0],
        "url": split_req_line[1],
        "headers" : {header.split(":")[0].lower().strip() : header.split(":")[1].strip() for header in http_headers},
        "body": http_req[1]
    }
    return parsed_msg

def handle_get(client:socket, http_req:dict) -> None:
    url:str = http_req["url"]
    match url:
            case _ if url == "/":
                client.send(f"HTTP/1.1 200 OK{CRLF}{CRLF}".encode("utf8"))
            case _ if url.startswith("/echo"):
                print(f"{http_req["headers"]=}")
                content_encoding:str = None
                if "accept-encoding" in http_req["headers"]:
                    content_encoding= http_req["headers"]["accept-encoding"]
                if content_encoding == "gzip":
                    client.send(f"HTTP/1.1 200 OK{CRLF}Content-Type: text/plain{CRLF}Content-Encoding: gzip{CRLF}{CRLF}".encode("utf8"))
                else:
                    echo_msg:str = http_req["url"].split("/")[2]
                    client.send(f"HTTP/1.1 200 OK{CRLF}Content-Type: text/plain{CRLF}Content-Length: {len(echo_msg)}{CRLF}{CRLF}{echo_msg}".encode("utf8"))
            case _ if url == "/user-agent":
                usr_agent:str = http_req["headers"]["user-agent"]
                client.send(f"HTTP/1.1 200 OK{CRLF}Content-Type: text/plain{CRLF}Content-Length: {len(usr_agent)}{CRLF}{CRLF}{usr_agent}".encode("utf8"))
            case _ if url.startswith("/files"):
                file_name:str = url.split("/files/")[-1]
                print(f"Reading file {sys.argv[2]}/{file_name}")
                return_file:Path = Path(f"{sys.argv[2]}/{file_name}")
                if return_file.exists():
                    with open(return_file, mode="r") as output_file:
                        file_data:str = "".join(output_file.readlines())
                    client.send(f"HTTP/1.1 200 OK{CRLF}Content-Type: application/octet-stream{CRLF}Content-Length: {len(file_data)}{CRLF}{CRLF}{file_data}".encode("utf8"))
                else:
                    client.send(f"HTTP/1.1 404 Not Found{CRLF}{CRLF}".encode("utf8"))
            case _:
                client.send(f"HTTP/1.1 404 Not Found{CRLF}{CRLF}".encode("utf8"))

def handle_post(client:socket, http_req:dict) -> None:
    url:str = http_req["url"]
    match url:
        case _ if url.startswith("/files"):
            file_name:str = url.split("/files/")[-1]
            data:str = http_req["body"]
            with open(f"{sys.argv[2]}/{file_name}", "w") as data_file:
                print(f"Writing file {sys.argv[2]}{file_name}")
                data_file.write(data)
            client.send(f"HTTP/1.1 201 Created{CRLF}{CRLF}".encode("utf8"))
        case _:
            client.send(f"HTTP/1.1 404 Not Found{CRLF}{CRLF}".encode("utf8"))

def handle_request(client:socket.socket) -> None:
    with client:
        req_msg:str = ""
        end_of_msg:bool = False
        while not end_of_msg:
            req_buf:str = client.recv(1024).decode("utf8")
            if len(req_buf) > 0:
                end_of_msg = True
            req_msg += req_buf
            
        print(f"Request Message: {req_msg}")

        http_req:dict = parse_request(req_msg)
        
        verb:str = http_req["verb"]
        match verb:
            case "GET":
                handle_get(client, http_req)
            case "POST":
                handle_post(client, http_req)
            case _:
                client.send(f"HTTP/1.1 405 Method Not Allowed{CRLF}{CRLF}".encode("utf8"))

def main() -> None:
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True) # Open the socket
    server_socket.listen() # Start listening
    
    threads:list = []
    while True:
        client, _ = server_socket.accept() # Accept incoming connections
        thread:Thread = Thread(target=handle_request, args=[client])
        threads.append(thread)
        thread.run()

if __name__ == "__main__":
    CRLF:str = "\r\n"
    main()
