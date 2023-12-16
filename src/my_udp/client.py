import socket


class UdpClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.sock.sendto(data, (self.host, self.port))

    def receive(self, buffer_size=1024):
        return self.sock.recv(buffer_size)

    def close(self):
        self.sock.close()

    def __del__(self):
        self.sock.close()
