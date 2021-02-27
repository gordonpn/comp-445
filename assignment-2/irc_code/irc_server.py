import asyncio
import json
import logging
import select
import socket

from args_parser import parse_server
from patterns import Publisher, Subscriber

logging.basicConfig(filename="view.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer(Publisher):
    def __init__(self, port, host):
        super().__init__()
        self.port = port
        self.host = host
        self.socket = socket.socket()
        self.connected_users = {}

    async def run(self):
        self.socket.setblocking(False)
        self.socket.bind((self.host, self.port))
        print(f"Accepting connections on {self.host}:{self.port}")
        self.socket.listen(10)

        inputs = [self.socket]
        outputs = []

        self.start_communications(inputs, outputs)

    def start_communications(self, inputs, outputs):
        while True:
            readable, _, _ = select.select(inputs, outputs, inputs)
            for _socket in readable:
                if _socket is self.socket:
                    client_socket, client_address = _socket.accept()
                    print(f"Client connected: {client_address}")
                    inputs.append(client_socket)
                    self.add_subscriber(
                        client_address, IRCSubscriber(client_socket, client_address)
                    )
                else:
                    client_input = _socket.recv(1024).decode()
                    if client_input:
                        self.parse_msg_from_client(_socket, client_input)
                    else:
                        print(f"Client disconnected: {_socket.getpeername()}")
                        inputs.remove(_socket)
                        self.rm_subscriber(_socket.getpeername())
                        _socket.close()

    def parse_msg_from_client(self, _socket, client_input):
        print(f'Client on port: "{_socket.getpeername()[1]} {client_input}"')
        if client_input.startswith("/nick"):
            nick = client_input.replace("/nick", "").strip()
            print(f"{nick=}")
            if nick in self.connected_users.values():
                _socket.send(f":server 433 * {nick} :Nickname already in use".encode())
            else:
                _socket.send(
                    (
                        f":server 001 {nick} :Welcome to the Internet Relay Network {nick}! "
                        "You are connected to the #global channel."
                    ).encode()
                )
                self.connected_users[_socket.getpeername()[1]] = nick
        elif _socket.getpeername()[1] not in self.connected_users:
            _socket.send(":server 431 * * :You have not set a nickname".encode())
        # TODO parse if it's a public message
        # decoded = json.loads(client_input)
        # packet = Packet(**decoded)
        # print(f"[{packet.username}]: {packet.message}")
        # self.notify(packet)

    def close(self):
        self.socket.close()


class IRCSubscriber(Subscriber):
    def __init__(self, _socket, address):
        self._socket = _socket
        self.address = address

    def update(self, msg):
        data = json.dumps(msg.__dict__)
        self._socket.send(data.encode())


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
