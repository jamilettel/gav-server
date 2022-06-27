from websockets import client


class GAClient:
    ws: client.WebSocketClientProtocol
    messages: int = 0

    def __init__(self, ws: client.WebSocketClientProtocol):
        self.ws = ws
        pass

    def __str__(self):
        return f"[Client {self.ws.id}, messages: {self.messages}]"