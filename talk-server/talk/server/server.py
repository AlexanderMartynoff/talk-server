from collections import defaultdict
from dataclasses import dataclass
from asyncio import StreamReader, StreamWriter, IncompleteReadError, start_server, run
from loguru import logger
from .struct import Message, Identity, Heartbeat, Status, decode, encode, status


@dataclass
class Pointer:
    session: str
    user: str
    reder: StreamReader
    writer: StreamWriter


class Manager:
    def __init__(self, port: int, host: str) -> None:
        self._pointers: dict[str, list[Pointer]] = defaultdict(list)
        self._port = port
        self._host = host

    async def _manage_stream(self, reader: StreamReader, writer: StreamWriter):
        element = decode(await reader.readuntil(b'\0'))

        match element:
            case Message(receiver=receiver):
                writer.write(encode(status(element, Status.Value.ACCEPTED)))

                for pointer in self._pointers[receiver]:
                    try:
                        pointer.writer.write(encode(element))
                    except Exception:
                        continue

            case Identity(session=session, sender=sender):
                logger.debug(f'User: "{sender}" append with session: "{session}"')

                self._pointers[sender].append(Pointer(
                    session=session,
                    user=sender,
                    reder=reader,
                    writer=writer,
                ))

            case Heartbeat():
                writer.write(encode(Heartbeat(receiver=element.sender, sender=element.receiver)))

    async def on_connect(self, reader: StreamReader, writer: StreamWriter):
        while True:
            try:
                await self._manage_stream(reader, writer)
            except IncompleteReadError:
                break

    async def start(self):
        logger.info(f'Run socket server: {self._host}:{self._port}')

        async with await start_server(self.on_connect, self._host, self._port) as server:
            await server.serve_forever()


def open(port: int, host: str = '0.0.0.0'):
    run(Manager(port, host).start())
