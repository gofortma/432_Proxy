import socket
import threading
import sys
from urllib.parse import urlparse

class GETRequest:
    def __init__(self, request):
        split = request.split()
        self.method = split[0]
        self.url = urlparse(split[1]).netloc

        if ':' in self.url:
            self.url, self.port = self.url.split(':')
            self.port = int(self.port)
        else:
            self.port = 80

        self.http_version = split[2]


    def verify_request(request):
        lines = request.split('\r\n')
        line_1 = lines[0].split(' ')
        if len(line_1) != 3:
            raise Exception('first line error')

        for line in lines[1:]:
            if line == '':
                break
            if ':' not in line:
                raise Exception('wrong header format')
            header_name, header_value = line.split(':', 1)
            if not header_name.strip() or not header_value.strip():
                raise Exception('empty headers')
        return True


def handle_client(conn):
    request_bytes = conn.recv(4096) + b'\r\n'
    request_bytes = request_bytes.decode().replace('HTTP/1.1', 'HTTP/1.0').replace('Connection: keep-alive', 'Connection: close').encode()

    if not GETRequest.verify_request(request_bytes.decode()):
        print("Handling bad request")
        response = b"HTTP/1.0 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>400 Bad Request</h1></body></html>"
        conn.send(response)
        return
    if (request_bytes.decode().find('GET') == -1):
        print("Not GET request")
        response = b"HTTP/1.0 501 Not Implemented\r\nContent-Type: text/html\r\n\r\n<html><body><h1>501 Not Implemented</h1></body></html>"
        conn.send(response)
        return
        

    request = GETRequest(request_bytes.decode())
    web_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    web_sock.connect((request.url, request.port))
    web_sock.send(request_bytes)

    response = b''
    while True:
        data = web_sock.recv(4096)
        if not data:
            break
        response += data
    
    conn.sendall(response)
    web_sock.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if int(len(sys.argv)) != 2:
        sock.bind(("localhost", 9876))
    else:
        sock.bind(("localhost", int(sys.argv[1])))
    sock.listen(5)

    while True:
        conn, client_addr = sock.accept()
        print("connected")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()


if __name__ == '__main__':
    main()