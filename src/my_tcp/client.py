import socket


class TcpClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send(self, data):
        self.socket.send(data)

    def receive(self, buffer_size=1024):
        return self.socket.recv(buffer_size)

    def close(self):
        self.socket.close()
