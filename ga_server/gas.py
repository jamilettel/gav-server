import websockets
import asyncio

from websockets import client

async def echo(websocket: websockets.client):
    async for message in websocket:
        print(message)
        
        await websocket.send(message)

async def server():
    async with websockets.serve(echo, "localhost", 8080):
        await asyncio.Future()


asyncio.run(server())