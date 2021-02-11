import getopt
import sys


def parse_client():
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


def parse_server():
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
