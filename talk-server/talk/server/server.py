from uuid import uuid4
from collections import defaultdict
from dataclasses import dataclass, field
from asyncio import StreamReader, StreamWriter, IncompleteReadError, start_server, run
from loguru import logger
from .struct import Message, Identity, Heartbeat, Status, decode, encode, status, EOM


@dataclass
class Pointer:
    id: str = field(default=uuid4)
    user: str
    reder: StreamReader
    writer: StreamWriter


class API:
    def __init__(self, port: int, host: str) -> None:
        self._pointers: dict[str, list[Pointer]] = defaultdict(list)
        self._port = port
        self._host = host

    async def start(self) -> None:
        logger.info(f'Run socket server: {self._host}:{self._port}')

        async with await start_server(self._on_connect, self._host, self._port) as server:
            await server.serve_forever()

    async def _manage_stream(self, reader: StreamReader, writer: StreamWriter) -> None:
        element = decode(await reader.readuntil(EOM))

        match element:
            case Message(receiver=receiver):
                writer.write(encode(status(element, Status.Value.ACCEPTED)))

                for pointer in self._pointers[receiver]:
                    try:
                        pointer.writer.write(encode(element))
                    except Exception:
                        continue

            case Identity(sender=sender):
                self._pointers[sender].append(Pointer(
                    user=sender,
                    reder=reader,
                    writer=writer,
                ))

            case Heartbeat():
                writer.write(encode(Heartbeat(receiver=element.sender, sender=element.receiver)))

    async def _on_connect(self, reader: StreamReader, writer: StreamWriter) -> None:
        while True:
            try:
                await self._manage_stream(reader, writer)
            except IncompleteReadError:
                break


def open(port: int, host: str = '0.0.0.0') -> None:
    run(API(port, host).start())
