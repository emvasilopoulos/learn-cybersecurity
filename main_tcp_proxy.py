import sys
import argparse
from my_tcp.proxy import server_loop


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("local_host", type=str)
    argparser.add_argument("local_port", type=int)
    argparser.add_argument("remote_host", type=str)
    argparser.add_argument("remote_port", type=int)
    argparser.add_argument("receive_first", action="store_true")
    options = argparser.parse_args()

    server_loop(
        options.local_host,
        options.local_port,
        options.remote_host,
        options.remote_port,
        options.receive_first,
    )


if __name__ == "__main__":
    main()
