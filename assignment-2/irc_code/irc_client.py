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
    def __init__(self):
        super().__init__()
        self.username = str()
        self._run = True

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        # Will need to modify this
        self.add_msg(msg)
        if msg.lower().startswith("/quit"):
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    async def run(self):
        """
        Driver of your IRC Client
        """
        # Remove this section in your code, simply for illustration purposes
        for x in range(10):
            self.add_msg(f"call after View.loop: {x}")
            await asyncio.sleep(2)

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        pass


def main(args):
    # Pass your arguments where necessary
    client = IRCClient()
    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")

        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )

        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
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
    server = "127.0.0.1"
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


def client_program(host, port):

    client_socket = socket.socket()  # instantiate
    client_socket.connect((host, port))  # connect to the server

    message = input(" -> ")  # take input

    while message.lower().strip() != "bye":
        client_socket.send(message.encode())  # send message
        data = client_socket.recv(1024).decode()  # receive response

        print("Received from server: " + data)  # show in terminal

        message = input(" -> ")  # again take input

    client_socket.close()  # close the connection


if __name__ == "__main__":
    # Parse your command line arguments here
    server, port = parse()
    client_program(server, port)
    args = None
    main(args)
