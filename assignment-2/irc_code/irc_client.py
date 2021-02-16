#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import asyncio
import json
import logging
import socket

from args_parser import parse_client
from packet_type import Packet
from patterns import Subscriber
from view import View

logging.basicConfig(filename="view.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(Subscriber):
    # TODO change the message format being sent
    def __init__(self, port, server):
        super().__init__()
        self.username = str()
        self.registered = False
        self._run = True
        self.port = port
        self.server = server
        self.socket = socket.socket()
        self.loop = asyncio.get_event_loop()

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        if not isinstance(msg, str):
            raise TypeError("Update argument needs to be a string")
        if len(msg) == 0:
            return
        logger.info("IRCClient.update -> msg: %s", msg)
        self.process_input(msg)

    def process_input(self, msg):
        if msg.lower().startswith("/quit"):
            self.loop.close()
            raise KeyboardInterrupt
        if msg.lower().startswith("/nick"):
            self.username = msg.replace("/nick ", "")
            if not self.registered:
                self.connect()
                self.registered = True
            return
        packet = Packet(self.username, msg)
        data = json.dumps(packet.__dict__)
        self.socket.send(data.encode())

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    def connect(self):
        self.socket.connect((self.server, self.port))
        self.add_msg("Connection to server successful")

        self.loop.run_in_executor(None, self.listen_server)

    async def run(self):
        self.add_msg("Use command /nick to set your nickname")

    def listen_server(self):
        while True:
            server_input = self.socket.recv(1024).decode()
            if not server_input:
                self.view.add_msg("", "Connection terminated by server")
                return

            decoded = json.loads(server_input)
            packet = Packet(**decoded)
            self.view.add_msg(packet.username, packet.message)

    def close(self):
        logger.debug("Closing IRC Client object")
        self.socket.close()


def main(port, server):
    client = IRCClient(port, server)
    logger.info("Client object created")
    with View() as v:
        logger.info("Entered the context of a View object")
        client.set_view(v)
        logger.debug("Passed View object to IRC Client")
        v.add_subscriber("", client)
        logger.debug("IRC Client is subscribed to the View (to receive user input)")

        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )

        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt:
            logger.debug("Signifies end of process")
    client.close()


if __name__ == "__main__":
    server, port = parse_client()
    main(port, server)
