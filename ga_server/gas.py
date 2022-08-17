import json
import traceback
from typing import Any, Callable, Generic, Tuple, TypeVar
from ga_server.client import GAClient
from threading import Lock
from websocket_server import WebsocketServer

T = TypeVar('T')

class GAServer(Generic[T]):

    json_dec = json.JSONDecoder()
    json_enc = json.JSONEncoder(separators=(',', ':'))
    
    connections: dict[Any, GAClient] = {}
    connections_mutex = Lock()
    
    sessions: dict[str, T] = {}
    sessions_mutex = Lock()

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8080,
        ga_data_provider: Callable[[], T] = None,
        commands: dict[str, Callable[[T, dict, Callable[[str], None], Callable[[str], None]], Tuple[str, bool] | None]] = {},
        command_protocol: str = "generic",
        title: str = "Generic Genetic Algorithm"
    ):
        self.host = host
        self.port = port
        self.ga_data_provider = ga_data_provider
        self.commands = commands
        self.command_protocol = command_protocol
        self.title = title
        self.server = WebsocketServer(host=self.host, port=self.port)
        self.server.set_fn_new_client(self.on_connect)
        self.server.set_fn_message_received(self.on_message)
        self.server.set_fn_client_left(self.on_close)
            # on_data_receive=self.on_message,
            # on_connection_open=self.on_connect,
            # on_connection_close=self.on_close


    def send_to_session(self, session: str, message: str):
        self.connections_mutex.acquire(1)
        try:
            for _, client in self.connections.items():
                if client.session_name == session:
                    self.server.send_message(client.ws, message)
        finally:
            self.connections_mutex.release()

    def get_session_list(self):
        return {
            "info": "session_list",
            "sessions": [x for x in self.sessions]
        }

    def session_join_or_create(self, ga_client: GAClient, data: dict):
        if "name" in data:
            name = data["name"]
            if name == "":
                return

            self.sessions_mutex.acquire(1)
            self.connections_mutex.acquire(1)
            try:
                if name not in self.sessions:
                    self.sessions[name] = self.ga_data_provider()
                    for _, client in self.connections.items():
                        self.server.send_message(client.ws, self.json_enc.encode(self.get_session_list()))
                ga_client.session_name = name
            finally:
                self.sessions_mutex.release()
                self.connections_mutex.release()

            self.session_info(ga_client)

    def send_session_list(self, ga_client: GAClient):
        self.sessions_mutex.acquire(1)
        try:
            self.server.send_message(ga_client.ws, self.json_enc.encode(self.get_session_list()))
        finally:
            self.sessions_mutex.release()

    def session_info(self, ga_client: GAClient):
        self.server.send_message(ga_client.ws, self.json_enc.encode({
            "info": "session",
            "session": ga_client.session_name,
        }))

    def session_delete(self, ga_client: GAClient):
        name = ga_client.session_name
        if name == None:
            return

        self.connections_mutex.acquire(1)
        self.sessions_mutex.acquire(1)
        try:
            if name in self.sessions:
                for _, c in self.connections.items():
                    if c.session_name == name:
                        c.session_name = None
                        self.session_info(c)
                del self.sessions[name]
                for _, client in self.connections.items():
                    self.server.send_message(client.ws, self.json_enc.encode(self.get_session_list()))
        finally:
            self.connections_mutex.release()
            self.sessions_mutex.release()

    def session_describe(self, ga_client: GAClient):
        self.server.send_message(ga_client.ws, self.json_enc.encode({
            "info": "session_describe",
            "title": self.title,
            "command_protocol": self.command_protocol
        }))

    def session_leave(self, ga_client: GAClient):
        ga_client.session_name = None
        self.session_info(ga_client)

    def handle_builtin(self, ga_client: GAClient, data: dict):
        if "session" in data:
            match data["session"]:
                case "join-or-create":
                    self.session_join_or_create(ga_client, data)
                case "delete":
                    self.session_delete(ga_client)
                case "list":
                    self.send_session_list(ga_client)
                case "info":
                    self.session_info(ga_client)
                case "describe":
                    self.session_describe(ga_client)
                case "leave":
                    self.session_leave(ga_client)
            return True
        return False

    def handle_command(self, ga_client: GAClient, data: dict):
        try:
            if "command" in data:
                if ga_client.session_name == None:
                    print("NoSession:", ga_client.ws.getpeername())
                    return True

                session = ga_client.session_name
                command = data["command"]

                if command in self.commands:
                    self.sessions_mutex.acquire(1)
                    try:
                        session_data = self.sessions[session]
                    finally:
                        self.sessions_mutex.release()

                    self.commands[command](
                        session_data, 
                        data, 
                        lambda msg: self.send_to_session(session, msg), 
                        lambda msg: self.server.send_message(ga_client.ws, msg)
                    )
                else:
                    print("CommandNotFound:", f'"{command}" from', ga_client)

                return True
        except Exception:
            print(traceback.format_exc())
        return False


    def message_handler(self, message: str, client: GAClient):

        try:
            data = self.json_dec.decode(message)
            if self.handle_builtin(client, data) == True:
                return
            if self.handle_command(client, data) == False:
                print("InvalidCommand:", f'"{message}" from', client)
        except json.JSONDecodeError:
            print("InvalidJSON:", f'"{message}" from', client)

    def on_connect(self, client: dict, server: WebsocketServer):
        self.connections_mutex.acquire(1)
        try:
            self.connections[client['address']] = GAClient(client)
        finally:
            self.connections_mutex.release()
        print(f"Connected: {client['address']}")

    def on_close(self, client: dict, _server: WebsocketServer):
        self.connections_mutex.acquire(1)
        try:
            del self.connections[client['address']]
        finally:
            self.connections_mutex.release()
        print(f"Disconnected: {client['address']}")

    def on_message(self, client: dict, _server: WebsocketServer, data: str):
        self.connections_mutex.acquire(1)
        try:
            ga_client = self.connections[client['address']]
        finally:
            self.connections_mutex.release()

        self.message_handler(data, ga_client)

    def run(self):
        try:
            print(f"Server starting on {self.host}:{self.port}")
            self.server.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.server_close()
