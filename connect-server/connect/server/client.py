import asyncio
from uuid import uuid4
from aioconsole import ainput
from .protocol import Message, Element, Identity, decode, encode


class UI:
    def __init__(self, host: str, port: int, user: str):
        self._session = uuid4()

        self._host = host
        self._port = port

        self._reader = None
        self._writer = None

        self._user = user
        self._sender = user

        self._receiver = None

        self._messages: dict[str, Element] = {}

    async def start(self):
        await self._connect()
        await self._identity()

        try:
            await asyncio.gather(self._start_process_income_messages(), self._start_process_console())
        except Exit:
            pass

    async def _start_process_income_messages(self):
        async for message in self._read():
            self._messages[message.id] = message

    async def _start_process_console(self):
        while True:
            await self._process_console('Enter: ')

    async def _process_console(self, title):
        value = await ainput(title)

        if not value:
            return

        if value.startswith(':'):
            await self._on_command(value)
        else:
            await self._write(Message(sender=self._user, receiver=self._receiver, value=value))

    async def _on_command(self, command: str) -> None:
        if '=' not in command:
            command += '='

        command, argument = (v.strip() for v in command.split('=', 1))

        match command:
            case ':quit' | ':q':
                raise Exit()
            case ':list' | ':l':
                for message in self._messages.values():
                    if isinstance(message, Message):
                        print(f'|<{message.sender}>: {message.time}|')
                        print(f'|{message.value}|')
                        print('.\n.\n.')
            case ':user' | ':u':
                pass
            case ':status' | ':s':
                print('Receiver:', self._receiver)
                print('Messages:', len(self._messages))
            case ':help' | ':h':
                print(
                    ':quit (:q) - Quit\r\n'
                    ':list (:l) - List all users\r\n'
                    ':user (:u) <user> - Authentication\r\n'
                    ':contact (:c) <user> - Set current contact'
                )
            case ':c' | ':contact':
                if argument:
                    self._receiver = argument
            case _:
                print(f'What is this - {command}?')

    async def _read(self):
        while not self._writer.is_closing():
            yield decode(await self._reader.readuntil(b'\0'))

    async def _write(self, element: Element, drain=False):
        self._writer.write(encode(element))

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

    async def _identity(self):
        await self._write(Identity(
            session=self._session,
            sender=self._user,
            receiver='none',
            password='none',
        ))


def open(host, port, user):
    asyncio.run(UI(host, port, user).start())


class Exit(Exception):
    pass
