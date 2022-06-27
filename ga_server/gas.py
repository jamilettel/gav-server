import asyncio
import signal
from uuid import UUID
from websockets import exceptions
from websockets import server
from websockets import client
from .client import GAClient


CONNECTIONS: dict[UUID, GAClient] = {}

async def message_handler(message, websocket: client.WebSocketClientProtocol):
    client = CONNECTIONS[websocket.id]
    client.messages += 1
    print(client, message)
    print(CONNECTIONS)
    await websocket.send(message)

async def ws_handler(websocket: client.WebSocketClientProtocol):
    CONNECTIONS[websocket.id] = GAClient(websocket)
    print(f"Connected: {websocket.id}")
    try:
        async for message in websocket:
            await message_handler(message, websocket)
    except exceptions.ConnectionClosedError:
        pass
    finally:
        del CONNECTIONS[websocket.id]
        print(f"Disconnected: {websocket.id}")

async def server_loop(host: str, port: int):
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    async with server.serve(ws_handler, "localhost", port):
        print(f"Server listening on {host}:{port}")
        await stop

def run_ga_server(host: str = "localhost", port: int = 8080):
    try:
        asyncio.run(server_loop(host, port))
    except KeyboardInterrupt:
        pass