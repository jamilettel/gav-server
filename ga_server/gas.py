import asyncio
import json
import signal
from typing import Any, Callable
from uuid import UUID
from websockets import exceptions
from websockets import server
from websockets import client
from ga_server.client import GAClient


class GAServer:

    json_dec = json.JSONDecoder()
    connections: dict[UUID, GAClient] = {}

    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8080, 
        ga_data_provider: Callable[[], Any] = None,
        commands: dict[str, Callable[[GAClient, dict], str]] = {}
    ):
        self.host = host
        self.port = port
        self.ga_data_provider = ga_data_provider
        self.commands = commands

    async def message_handler(self, message, websocket: client.WebSocketClientProtocol):
        ga_client = self.connections[websocket.id]
        
        try:
            data = self.json_dec.decode(message)
            if "command" in data:
                if data["command"] in self.commands:
                    response = self.commands[data["command"]](ga_client, data)
                    if response is not None:
                        await websocket.send(response)
                else:
                    print("CommandNotFound:", f'"{message}" from', ga_client)
            else:
                print("InvalidCommand:", f'"{message}" from', ga_client)
        except json.JSONDecodeError:
            print("InvalidJSON:", f'"{message}" from', ga_client)


    async def ws_handler(self, websocket: client.WebSocketClientProtocol):
        self.connections[websocket.id] = GAClient(
            websocket,
            ga_data=self.ga_data_provider() if self.ga_data_provider != None else None
        )
        print(f"Connected: {websocket.id}")
        try:
            async for message in websocket:
                await self.message_handler(message, websocket)

        except exceptions.ConnectionClosedError:
            pass
        finally:
            del self.connections[websocket.id]
            print(f"Disconnected: {websocket.id}")

    async def server_loop(self, host: str, port: int):
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

        async with server.serve(self.ws_handler, "localhost", port):
            print(f"Server listening on {host}:{port}")
            await stop

    def run(self):
        try:
            asyncio.run(self.server_loop(self.host, self.port))
        except KeyboardInterrupt:
            pass
