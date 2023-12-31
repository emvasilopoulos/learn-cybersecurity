import argparse
from dataclasses import dataclass
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    """
    Execute a command and return the output as a string.

    Args:
        cmd (str): command to execute

    Returns:
        str: output of the command
    """
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(
        shlex.split(cmd), stderr=subprocess.STDOUT
    )  # runs the command on local OS and returns the output
    return output.decode()


@dataclass
class NetCatArguments:
    command: bool
    execute: str
    listen: bool
    port: int
    target: str
    upload: str


class NetCat:
    def __init__(
        self, args: NetCatArguments, buffer: bytes = None, recv_len_limit: int = 4096
    ) -> None:
        self.args = args
        self.buffer = buffer
        self.recv_len_limit = recv_len_limit
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # reuse socket
        # self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # disable Nagle's algorithm

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print("[*] Listening on {0}:{1}".format(self.args.target, self.args.port))
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.__handle, args=(client_socket,)
            )
            client_thread.start()

    def __handle(self, client_socket: socket.socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b""
            while (
                True
            ):  # read from socket bytes of size 4096 per iteration and append to file_buffer. When done, write to file
                data = client_socket.recv(self.recv_len_limit)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            message = f"Saved file {self.args.upload}"
            client_socket.send(message.encode())
        elif self.args.command:
            cmd_buffer = b""
            while True:
                try:
                    client_socket.send(b"BHP:#> ")
                    while (
                        "\n" not in cmd_buffer.decode()
                    ):  # When user hits enter, the command is executed
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b""
                except Exception as e:
                    print(f"Server killed {e}")
                    self.socket.close()
                    sys.exit()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer is not None:
            self.socket.send(self.buffer)
        try:
            while True:
                recv_len = 1
                response = ""
                while recv_len:
                    data = self.socket.recv(self.recv_len_limit)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < self.recv_len_limit:
                        break
                if response:
                    print(response)
                    buffer = input("> ")
                    buffer += "\n"
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("[*] User terminated...")
            self.socket.close()
            sys.exit()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            "Example:"
            "netcat.py -t 192.168.1.108 -p 5555 -l -c"  # command shell\
            "netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt"  # upload to file\
            'netcat.py -t 192.168.1.108 -p 5555 -l -e="cat /etc/passwd"'  # execute command\
            "echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135"
            "netcat.py -t 192.168.1.108 -p 5555"
        ),
    )  # connect to server
    arg_parser.add_argument(
        "-c", "--command", action="store_true", help="command shell"
    )
    arg_parser.add_argument(
        "-e", "--execute", help="execute specified command"
    )  # execute command
    arg_parser.add_argument(
        "-l", "--listen", action="store_true", help="listen"
    )  # listen
    arg_parser.add_argument(
        "-p", "--port", type=int, default=5555, help="specified port"
    )  # port
    arg_parser.add_argument("-t", "--target", default="192.168.56.101")  # target
    arg_parser.add_argument("-u", "--upload", help="upload file")  # upload file
    options = arg_parser.parse_args()
    if options.listen:
        buffer = ""
    else:
        if not options.upload:
            print(
                "Enter data to send to server. Ctrl-D for Linux or Ctrl-Z for Windows to terminate."
            )
            buffer = sys.stdin.read()
    nc = NetCat(
        NetCatArguments(
            command=options.command,
            execute=options.execute,
            listen=options.listen,
            port=options.port,
            target=options.target,
            upload=options.upload,
        ),
        buffer.encode(),
    )
    nc.run()
