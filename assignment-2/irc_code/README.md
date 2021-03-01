# Simplified IRC server and IRC clients

## Objective

Get familiar with Python sockets by programming an IRC client & server

## Design Description

First, we modified the original `patterns.py` to hold a dictionary of subscribers rather than a list for two reasons.

The first reason, this way it could keep track of subscribers with their ports as the dictionary key.

The second reason, we decided to make the `IRCServer` class inherit from a Publisher class and we created a class `IRCSubscriber` as a Subscriber that is used by the `IRCServer` class.

### IRC Client

First, we parse the command line arguments using a method defined in `args_parser.py`, nothing too special here.

Second, upon starting the client, the client will attempt to connect to the server right away, but the user will not be allowed to talk on the channel until they register themselves.

An asyncio event loop is used to listen to the server in a non-blocking manner to allow the user to type on the ncurses interface.

As messages are received from the server socket, they are parsed and displayed using the provided ncurses interface.

Welcome messages from the server sets (confirms) the username on the client and allows the client on talk on the channel.

The client is also notified when the server ends the connection.

Finally, messages are correctly formatted for the server when they leave the client.

### IRC Server

The server:

- uses a similar argument parser as the client with the exception that it does not allow for user-defined server address.

- does not use the same ncurses interface as the client, but simply prints useful messages to the terminal.

- sends and receives messages in a non-blocking manner using `select`.

When the server receives a new connection, that client is added as a subscriber (`IRCSubscriber`) to allow message propagation later.

If the message is 0 bytes, that means the client has closed the connection with the server and the other users whom are still connected are notified of that user leaving.

The server handles nickname collisions by dropping the request, not allowing the client to register until they choose a unique nickname.

## Development

### Instructions

This project uses Python 3.9.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.dev.txt
```

The above only installs useful developer dependencies. This project only uses the following standard libraries:

- abc
- asyncio
- getopt
- logging
- select
- socket
- sys

You must start the IRC server before starting any IRC clients as the clients are not designed to retry connections.
