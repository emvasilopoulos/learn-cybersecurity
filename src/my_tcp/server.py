import socket


class TcpClient:
    def __init__(self, host, port, max_connections=5):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(max_connections)  # maximum backlog of connections

    def send(self, data):
        self.socket.sendall(data)

    def receive(self, buffer_size=1024):
        return self.socket.recv(buffer_size)

    def close(self):
        self.socket.close()
