import asyncio
import json
from re import A
import signal
from typing import Callable, Generic, Tuple, TypeVar
from uuid import UUID
from websockets import exceptions
from websockets import server
from websockets import client
from ga_server.client import GAClient

T = TypeVar('T')

class GAServer(Generic[T]):

    json_dec = json.JSONDecoder()
    json_enc = json.JSONEncoder()
    connections: dict[UUID, GAClient] = {}
    sessions: dict[str, T] = {}

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        ga_data_provider: Callable[[], T] = None,
        commands: dict[str, Callable[[T, dict], Tuple[str, bool] | None]] = {},
        command_protocol: str = "generic"
    ):
        self.host = host
        self.port = port
        self.ga_data_provider = ga_data_provider
        self.commands = commands
        self.command_protocol = command_protocol

    async def send_to_session(self, session: str, message: str):
        for _, client in self.connections.items():
            if client.session_name == session:
                await client.ws.send(message)

    async def session_join_or_create(self, ga_client: GAClient, data: dict):
        if "name" in data:
            name = data["name"]
            if name == "":
                return
            elif name not in self.sessions:
                self.sessions[name] = self.ga_data_provider()
            ga_client.session_name = name
            await self.session_info(ga_client)
    
    async def session_list(self, ga_client: GAClient):
        await ga_client.ws.send(self.json_enc.encode({
            "info": "session_list",
            "sessions": [x for x in self.sessions]
        }))
    
    async def session_info(self, ga_client: GAClient):
        await ga_client.ws.send(self.json_enc.encode({
            "info": "session",
            "session": ga_client.session_name,
        }))

    async def session_delete(self, ga_client: GAClient):
        name = ga_client.session_name
        if name != None:
            for _, c in self.connections.items():
                if c.session_name == name:
                    c.session_name = None
                    await self.session_info(c)

    async def session_describe(self, ga_client: GAClient):
        await ga_client.ws.send(self.json_enc.encode({
            "info": "session_describe",
            "command_protocol": self.command_protocol
        }))

    async def handle_builtin(self, ga_client: GAClient, data: dict):
        if "session" in data:
            match data["session"]:
                case "join-or-create":
                    await self.session_join_or_create(ga_client, data)
                case "delete":
                    await self.session_delete(ga_client)
                case "list":
                    await self.session_list(ga_client)
                case "info":
                    await self.session_info(ga_client)
                case "describe":
                    await self.session_describe(ga_client)
            return True
        return False

    async def handle_command(self, ga_client: GAClient, data: dict):
        if "command" in data:
            if ga_client.session_name == None:
                print("NoSession:", ga_client.ws.id)
                return True

            session = ga_client.session_name
            command = data["command"]

            if command in self.commands:
                response = self.commands[command](self.sessions[session], data)
                if response is not None:
                    message = response[0]
                    broadcast = response[1]
                    if broadcast:
                        await self.send_to_session(session, message)
                    else:
                        await ga_client.ws.send(message)
            else:
                print("CommandNotFound:", f'"{command}" from', ga_client)

            return True
        return False


    async def message_handler(self, message, websocket: client.WebSocketClientProtocol):
        ga_client = self.connections[websocket.id]

        try:
            data = self.json_dec.decode(message)
            if await self.handle_builtin(ga_client, data) == True:
                return
            if await self.handle_command(ga_client, data) == False:
                print("InvalidCommand:", f'"{message}" from', ga_client)
        except json.JSONDecodeError:
            print("InvalidJSON:", f'"{message}" from', ga_client)

    async def ws_handler(self, websocket: client.WebSocketClientProtocol):
        self.connections[websocket.id] = GAClient(websocket)
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
