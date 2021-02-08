import getopt
import socket
import sys


def server_program(port):
    host = "127.0.0.1"

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    print(f"Accepting connections on {host}:{port}")
    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data))
        data = input(" -> ")
        conn.send(data.encode())  # send data to the client

    conn.close()  # close the connection


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
    return int(port)


if __name__ == "__main__":
    # Parse your command line arguments here
    port = parse()
    server_program(port)
