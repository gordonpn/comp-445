class Packet(dict):
    def __init__(self, username, message):
        self.username = username
        self.message = message
