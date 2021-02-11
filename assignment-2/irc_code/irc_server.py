import asyncio
import json
import logging
import select
import socket

from args_parser import parse_server
from packet_type import Packet

logging.basicConfig(filename="view.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer:
    # TODO refactor to use observer pattern
    def __init__(self, port, host):
        super().__init__()
        self.port = port
        self.host = host
        self.socket = socket.socket()
        self.client_sockets = []

    async def run(self):
        self.socket.setblocking(False)
        self.socket.bind((self.host, self.port))
        print(f"Accepting connections on {self.host}:{self.port}")
        self.socket.listen(10)

        inputs = [self.socket]
        outputs = []

        while True:
            readable, _, _ = select.select(inputs, outputs, inputs)

            for _socket in readable:
                if _socket is self.socket:
                    client_socket, client_address = _socket.accept()
                    print(f"Client connected: {client_address}")
                    inputs.append(client_socket)
                    self.client_sockets.append((client_socket, client_address))
                else:
                    client_input = _socket.recv(1024).decode()
                    if client_input:
                        decoded = json.loads(client_input)
                        packet = Packet(**decoded)
                        print(f"[{packet.username}]: {packet.message}")
                        self.propagate(packet)
                    else:
                        print(f"Client disconnected: {_socket.getpeername()}")
                        inputs.remove(_socket)
                        self.client_sockets.remove((_socket, _socket.getpeername()))
                        _socket.close()

    def propagate(self, packet):
        for client_socket, _ in self.client_sockets:
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
