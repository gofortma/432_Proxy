import signal
import socket
import threading
import sys


class proxy():
    def __init__(self):
        # creating a tcp socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # reuse the socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.your_ip = "127.0.0.1" # loop back address
        if(len(sys.argv) != 3):
            self.your_port = 6789
        else:
            self.your_port = sys.argv[2]
        

    def shutdown(self):
        # add your signal shutdown code here
        pass

    def getClientName(self, ip_address):
        try:
            hostname = socket.gethostbyaddr(ip_address)[0]
            return hostname
        except socket.herror:
            return "No domain name found"

    def client_threading(self):
        signal.signal(signal.SIGINT, self.shutdown)

        self.serverSocket.bind((self.your_ip, self.your_port))

        while True:
            # establish the connection
            self.serverSocket.listen(10)
            self.__clients = {}
            (clientSocket, client_address) = self.serverSocket.accept()
            print(client_address[0])

            d = threading.Thread(name= self.getClientName(client_address[0]),target = self.main, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()

    def main(self, conn, client_address):
        # get the request from browser
        from_client = conn.recv(4096)
        request = from_client.decode("utf-8")

        # parse the first line
        print("from_client: ", from_client)
        print("request: ", request)
        first_line = request.split('\n')[0]
        print("first line: ", first_line)

        # get url
        url = first_line.split(' ')[1]
        print("url: ",  url)

        http_pos = url.find("://")
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(":")

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1

        if port_pos == -1 or webserver_pos < port_pos:

            # default port
            port = 80
            webserver = temp[:webserver_pos]

        else:  # specific port
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(100)
        s.connect((webserver, port))
        print("request: " + request)
        s.sendall(from_client)
        print("sent data")

        while 1:
            # receive data from web server
            data = s.recv(4096)
            print("data received")

            if len(data) > 0:
                conn.send(data)  # send to browser/client

            else:
                break

p = proxy()
p.client_threading()

def getClientName(self, ip_address):
    try:
        hostname = socket.gethostbyaddr(ip_address)[0]
        return hostname
    except socket.herror:
        return "No domain name found"