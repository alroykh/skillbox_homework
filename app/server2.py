#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport
    clients: list = []
    message_history: list = []

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data)

        decoded = data.decode().strip()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                if self.login not in self.clients:
                    for message_h in self.message_history:
                        self.transport.write(message_h.encode())
                    self.transport.write(
                        f"Hello, {self.login}!\r\n".encode()
                        )
                    self.clients.append(self.login)
                    print(self.clients)
                else:
                    self.transport.write("Login already exist...\r\n".encode())
            else:
                self.transport.write("Incorrect login...\r\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("New client has come...")
        print("")


    def connection_lost(self, exception):
        self.server.clients.remove(self)
        self.clients.remove(self.login)
        print("Client logged out...")

    def send_message(self, content: str):
        content = content.replace("\r\n", "")
        message = f"{self.login}: {content}\r\n"
        if content:
            self.message_history.append(message)
            print(message.encode())
            if len(self.message_history) > 10:
                del (self.message_history[0])
            for user in self.server.clients:
                user.transport.write(message.encode())

                # if user != self:
                #     user.transport.write(self.message_history)
                # else:


class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            9000
        )

        print("Server is started...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Server stopped manually...")