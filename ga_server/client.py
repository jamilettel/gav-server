from socket import socket

class GAClient():
    messages: int = 0
    session_name: str | None = None

    def __init__(self, ws: socket):
        self.ws = ws
        pass

    def __str__(self):
        return f"[Client {self.ws.getpeername()}, messages: {self.messages}]"

