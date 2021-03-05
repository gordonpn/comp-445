import asyncio
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
                        rpl = (
                            ":server PART #global :"
                            f"{self.connected_users[_socket.getpeername()[1]]} has left."
                        )
                        print(rpl)
                        self.notify(rpl)
                        self.connected_users.pop(_socket.getpeername()[1], None)
                        _socket.close()

    def parse_msg_from_client(self, _socket, client_input):
        print(f'Client on port {_socket.getpeername()[1]}: "{client_input}"')
        rpl = ""
        if client_input.startswith("/nick"):
            nick = client_input.replace("/nick", "").strip()
            if nick in self.connected_users.values():
                rpl = f":server 433 * {nick} :Nickname already in use"
                _socket.send(rpl.encode())
            elif len(nick) > 9:
                rpl = f":server 432 * {nick} :Erroneous nickname"
                _socket.send(rpl.encode())
            else:
                rpl = (
                    f":server 001 {nick} :Welcome to the Internet Relay Network {nick}! "
                    "You are connected to the #global channel."
                )
                print(rpl)
                _socket.send(rpl.encode())
                self.connected_users[_socket.getpeername()[1]] = nick
                rpl = f":server JOIN #global :{nick} has joined #global."
                self.notify(rpl)
        elif _socket.getpeername()[1] not in self.connected_users:
            rpl = ":server 431 * * :You have not set a nickname"
            _socket.send(rpl.encode())
        elif "PRIVMSG" in client_input:
            rpl = f":{self.connected_users[_socket.getpeername()[1]]} {client_input}"
            self.notify(rpl)
        print(rpl)

    def close(self):
        self.socket.close()


class IRCSubscriber(Subscriber):
    def __init__(self, _socket, address):
        self._socket = _socket
        self.address = address

    def update(self, msg):
        self._socket.send(msg.encode())


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
