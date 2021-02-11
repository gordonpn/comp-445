import asyncio
import json
import logging
import socket

from args_parser import parse_server
from packet_type import Packet

logging.basicConfig(filename="view.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer:
    def __init__(self, port, host):
        super().__init__()
        self.username = "irc_server"
        self.port = port
        self.host = host
        self.socket = socket.socket()
        self.client_sockets = []
        # self.socket.setblocking(False)

    async def run(self):
        self.socket.bind((self.host, self.port))
        print(f"Accepting connections on {self.host}:{self.port}")
        self.socket.listen(10)
        client_socket, client_address = self.socket.accept()
        print(self.username, "Connection from: " + str(client_address))
        self.client_sockets.append(client_socket)

        while True:
            client_input = client_socket.recv(1024).decode()
            if not client_input:
                print("Socket connection broken")
                break
            decoded = json.loads(client_input)
            packet = Packet(**decoded)
            print(f"{packet.username=}, {packet.message=}")
            self.propagate(packet)

            # TODO handle when client disconnects
            # TODO handle more than 1 connection
            # TODO propagate message to other clients

    def propagate(self, packet):
        for client_socket in self.client_sockets:
            data = json.dumps(packet.__dict__)
            client_socket.send(data.encode())

    def close(self):
        self.socket.close()


def main(port, host):
    server = IRCServer(port, host)

    async def inner_run():
        await asyncio.gather(
            server.run(),
            return_exceptions=True,
        )

    try:
        asyncio.run(inner_run())
    except KeyboardInterrupt:
        print("\nGraceful server shutdown through SIGINT")
    server.close()


if __name__ == "__main__":
    port = parse_server()
    main(port, "0.0.0.0")
