import argparse
import socket
import threading


class TcpServer:
    def __init__(self, host, port, max_connections=5):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(max_connections)  # maximum backlog of connections
        print(f"[*] Listening on {host}:{port}")

    def run(self):
        while True:
            client, address = self.socket.accept()
            print(f"[*] Accepted connection from {address[0]}:{address[1]}")
            client_handler = threading.Thread(
                target=self.__handle_client, args=(client,)
            )
            client_handler.start()

    def __handle_client(self, client_socket):
        with client_socket as sock:
            request = sock.recv(1024)
            print(f"[*] Received: {request.decode('utf-8')}")
            sock.send(b"ACK")

    def send(self, data):
        self.socket.sendall(data)

    def receive(self, buffer_size=1024):
        return self.socket.recv(buffer_size)

    def close(self):
        self.socket.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="TCP server")
    arg_parser.add_argument("host", help="Interface the server listens at")
    arg_parser.add_argument("port", type=int, help="TCP port the server listens at")
    options = arg_parser.parse_args()
    # Example usage
    server = TcpServer(options.host, options.port)
    try:
        server.run()
    except KeyboardInterrupt:
        print("[*] Exiting...")
        del server
    exit(0)
