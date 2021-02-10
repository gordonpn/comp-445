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
import getopt
import logging
import socket
import sys

import patterns
import view

logging.basicConfig(filename="view.log", level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):
    def __init__(self, port, server):
        super().__init__()
        self.username = str()
        self._run = True
        self.port = port
        self.server = server
        self.socket = socket.socket()
        # self.socket.setblocking(False)

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError("Update argument needs to be a string")
        if len(msg) == 0:
            # Empty string
            return
        logger.info("IRCClient.update -> msg: %s", msg)
        self.process_input(msg)

    def process_input(self, msg):
        # Will need to modify this
        self.add_msg(msg)
        if msg.lower().startswith("/quit"):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt
        self.socket.send(msg.encode())

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    async def run(self):
        """
        Driver of your IRC Client
        """
        self.socket.connect((self.server, self.port))
        self.add_msg("Connection to server successful")

        # TODO receive messages from server
        # while True:
        #     server_input = self.socket.recv(1024).decode()
        #     self.view.add_msg("", server_input)
        # Remove this section in your code, simply for illustration purposes
        # for x in range(10):
        #     self.add_msg(f"call after View.loop: {x}")
        #     await asyncio.sleep(2)

    def close(self):
        logger.debug("Closing IRC Client object")
        self.socket.close()


def main(port, server):
    # Pass your arguments where necessary
    client = IRCClient(port, server)
    logger.info("Client object created")
    with view.View() as v:
        logger.info("Entered the context of a View object")
        client.set_view(v)
        logger.debug("Passed View object to IRC Client")
        v.add_subscriber(client)
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
    client.close()


def parse():
    usage = """usage: irc_client.py [-h] [--server SERVER] [--port PORT]

    optional arguments:
    -h, --help \t\tshow this help message and exit
    --server SERVER \ttarget server to initiate a connection to
    --port PORT \ttarget port to use"""

    options, _ = getopt.getopt(
        sys.argv[1:],
        "hp:s:",
        ["help", "port=", "server="],
    )
    port = "17573"
    server = "0.0.0.0"
    for o, a in options:
        if o in ("-h", "--help"):
            print(usage)
            sys.exit()
        if o in ("-p", "--port"):
            port = a
            print(f"port option entered: {port}")
        if o in ("-s", "--server"):
            server = a
            print(f"server option entered: {server}")
    if len(options) > 3:
        raise SystemExit(usage)
    return server, int(port)


if __name__ == "__main__":
    # Parse your command line arguments here
    server, port = parse()
    main(port, server)
