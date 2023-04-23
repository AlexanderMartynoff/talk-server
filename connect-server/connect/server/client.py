import asyncio
from aioconsole import ainput
from .protocol import Message, decode, encode


class UI:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

        self._reader = None
        self._writer = None

        self._sender = ':client'
        self._receiver = ':server'

        self._income_messages = []

    async def _start_process_income_messages(self):
        async for message in self._read():
            self._income_messages.append(message)

    async def start(self):
        await self._connect()

        try:
            await asyncio.gather(self._start_process_income_messages(), self._start_process_input())
        except Exit:
            pass

    async def _start_process_input(self):
        while True:
            await self._process_input('Enter: ')

    async def _process_input(self, title):
        value = await ainput(title)

        if value.startswith(':'):
            await self._on_command(value)
        else:
            await self._write(Message(sender=self._sender, receiver=self._receiver, value=value))

    async def _on_command(self, command):
        match command:
            case ':quit' | ':q':
                raise Exit()
            case ':list' | ':l':
                pass
            case ':user' | ':u':
                pass
            case ':contact' | ':c':
                pass
            case ':help' | ':h':
                print(
                    '\r\n'
                    ':read (:r) <user>? - Fetch new messages (if user is not set fetch for all users)\r\n'
                    ':quit (:q) - Quit\r\n'
                    ':list (:l) - List all users\r\n'
                    ':user (:u) <user> - Authentication\r\n'
                    ':contact (:c) <user> - Set current contact'
                )
            case _:
                print(f'What is this - {command}')

    async def _read(self):
        while not self._writer.is_closing():
            yield decode(await self._reader.readuntil(b'\0'))

    async def _write(self, message, drain=False):
        if not self._writer or self._writer.is_closing():
            await self._connect()

        self._writer.write(encode(message))

        if drain:
            await self._writer.drain()

    async def _connect(self):
        if self._writer:
            self._writer.close()

        self._reader = None
        self._writer = None

        try:
            reader, writer = await asyncio.open_connection(self._host, self._port)
        except OSError:
            raise

        self._reader = reader
        self._writer = writer


def open(host, port):
    asyncio.run(UI(host, port).start())


class Exit(Exception):
    pass
