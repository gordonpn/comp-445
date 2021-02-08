import getopt
import sys


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
    return port


if __name__ == "__main__":
    # Parse your command line arguments here
    port = parse()
