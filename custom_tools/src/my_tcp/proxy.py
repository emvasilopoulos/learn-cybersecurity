<<<<<<< HEAD
=======
"""
Why a proxy?
1) for forwarding traffic to bounce from host to host
2) for managing traffic in general

How? 4 main functions
1) Display communication between the local and remote machines to the console (hexdump)
2) Receive data from an incoming socket from either local or remote machine (receive_from)
3) Manage traffic direction between remote and local machines (proxy_handler)
4) Set up a listening socket and pass it our proxy_handler (server_loop)
"""
import sys
import socket
import threading

# The representation of a printable character has a length of 3. If the length is not 3, then the character is not printable.
HEX_FILTER = "".join([(len(repr(chr(i))) == 3) and chr(i) or "." for i in range(256)])


def hexdump(src: str, length=16, show=True):
    """
    This function provides us with a way to watch the communication going through the proxy in real time.

    Args:
        src (str): a string
        length (int, optional): Defaults to 16.
        show (bool, optional): Default to True.

    """
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i : i + length])

        printable = word.translate(HEX_FILTER)
        hexa = " ".join([f"{ord(c):02X}" for c in word])
        hexwidth = length * 3
        results.append(f"{i:04x}  {hexa:<{hexwidth}}  {printable}")


def receive_from(connection, timeout_in_seconds: int = 5):
    buffer = b""  # will accumulate responses from "connection"
    connection.settimeout(timeout_in_seconds)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer


def request_handler(buffer):
    # perform packet modifications
    return buffer


def response_handler(buffer):
    # perform packet modifications
    return buffer


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # Connect with remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # Receive data from remote host if necessary - FTP servers typically send a banner first
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print(f"<§ Sending {len(remote_buffer)} bytes to localhost.")
            client_socket.send(remote_buffer)

    # Now let's loop and read from local, send to remote, send to local, repeat
    while True:
        # Read from local host and if exists, send to remote host
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"§> Received {len(local_buffer)} bytes from localhost.")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("§> Sent to remote.")

        # Read from remote host and if exists, send to local host
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"<§ Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("<§= Sent to localhost.")

        # If no more data on either side, close the connections
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print(f"[!!] Check for other listening sockets or correct permissions.")
        print(f"[!!] Exception: {e}")
        sys.exit(0)
    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # Print out the local connection information
        print(f"§> Received incoming connection from {addr[0]}:{addr[1]}")
        # Start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first),
        )
        proxy_thread.start()
=======
            
        
>>>>>>> a62d648 (TCP proxy init)
