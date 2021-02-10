import asyncio
import getopt
import logging
import socket
import sys

import patterns
import view

logging.basicConfig(filename="view.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer(patterns.Subscriber):
    def __init__(self, port, host):
        super().__init__()
        self.username = "irc_server"
        self.port = port
        self.host = host
        self.socket = socket.socket()
        # self.socket.setblocking(False)

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        if not isinstance(msg, str):
            raise TypeError("Update argument must be a string")
        if len(msg) == 0:
            return
        logger.info("IRCServer.update -> msg: %s", msg)
        self.process_input(msg)

    def process_input(self, msg):
        self.add_msg(msg)
        if msg.lower().startswith("/quit"):
            raise KeyboardInterrupt
        # TODO server send message

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    async def run(self):
        self.socket.bind((self.host, self.port))
        self.add_msg(f"Accepting connections on {self.host}:{self.port}")
        self.socket.listen(10)
        client_socket, client_address = self.socket.accept()
        self.view.add_msg(self.username, "Connection from: " + str(client_address))

        while True:
            client_input = client_socket.recv(1024).decode()
            self.view.add_msg(client_address, str(client_input))
            # TODO handle when client disconnects
            # TODO handle more than 1 connection
            # TODO propagate message to other clients

    def close(self):
        self.socket.close()


def main(port, host):
    server = IRCServer(port, host)

    with view.View() as v:
        server.set_view(v)
        v.add_subscriber(server)

        async def inner_run():
            await asyncio.gather(
                v.run(),
                server.run(),
                return_exceptions=True,
            )

        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt:
            server.close()
    server.close()


def parse():
    usage = """usage: irc_server.py [-h] [--port PORT]

    optional arguments:
    -h, --help \t\tshow this help message and exit
    --port PORT \ttarget port to use"""

    options, _ = getopt.getopt(
        sys.argv[1:],
        "hp:",
        ["help", "port="],
    )
    port = "17573"
    for o, a in options:
        if o in ("-h", "--help"):
            print(usage)
            sys.exit()
        if o in ("-p", "--port"):
            port = a
            print(f"port option entered: {port}")
    if len(options) > 2:
        raise SystemExit(usage)
    return int(port)


if __name__ == "__main__":
    port = parse()
    main(port, "0.0.0.0")
