from websockets import client
from typing import TypeVar, Generic


T = TypeVar('T')

class GAClient(Generic[T]):
    ws: client.WebSocketClientProtocol
    messages: int = 0
    ga_data: T

    def __init__(self, ws: client.WebSocketClientProtocol, ga_data: T = None):
        self.ws = ws
        self.ga_data = ga_data
        pass

    def __str__(self):
        return f"[Client {self.ws.id}, messages: {self.messages}]"

