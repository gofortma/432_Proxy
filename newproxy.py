import socket
import threading
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


    def verify_valid_http_request(cls, request):
        lines = request.split('\r\n')
        line_1 = lines[0].split(' ')
        if len(line_1) != 3:
            raise Exception('first line error')

        for line in lines[1:]:
            if line == '':
                break
            if ':' not in line:
                raise Exception('wrong header format"')
            header_name, header_value = line.split(':', 1)
            if not header_name.strip() or not header_value.strip():
                raise Exception('empty headers')
        return True


def handle_client(client_sock):
    request_bytes = client_sock.recv(4096) + b'\r\n'
    request_bytes = request_bytes.decode().replace('HTTP/1.1', 'HTTP/1.0').replace('Connection: keep-alive', 'Connection: close').encode()
    print(request_bytes.decode())
    print(request_bytes)

    if not GETRequest.verify_valid_http_request(request_bytes.decode()):
        print("Handling bad request")
        response = b"HTTP/1.0 500 Malformed Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>500 Malformed Request</h1></body></html>"
        client_sock.send(response)
        return

    request = GETRequest(request_bytes.decode())
    print(request.__dict__)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.send(request_bytes)

    response = b''
    while True:
        data = server_socket.recv(4096)
        if not data:
            break
        response += data

    server_socket.close()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 8080))
    sock.listen(5)

    while True:
        client_sock, client_addr = sock.accept()
        print("connected")
        client_thread = threading.Thread(target=handle_client, args=(client_sock,))
        client_thread.start()


if __name__ == '__main__':
    main()
