from __future__ import annotations
from asyncio import StreamReader, StreamWriter, IncompleteReadError, start_server, run
from loguru import logger
from .protocol import Message, Handshake, Ping, Pong, decode, encode, delivery
from .broker import Broker
from . import api


async def _do_process(reader: StreamReader, writer: StreamWriter, broker: Broker):
    message = decode(await reader.readuntil(b'\0'))

    match message:
        case Message(sender=sender):
            broker.put(message)
            writer.write(encode(delivery(message)))

        case Handshake(sender=sender, secret=secret):
            api.handshake(sender, secret)

        case Ping():
            writer.write(encode(Pong()))

        case Pong():
            writer.write(encode(Ping()))


async def _process(reader: StreamReader, writer: StreamWriter):
    while True:
        try:
            await _do_process(reader, writer, Broker())
        except IncompleteReadError:
            break


async def start(port: int, host='0.0.0.0'):
    server = await start_server(_process, host, port)

    async with server:
        logger.info(f'Start server on: {host}:{port}')
        await server.serve_forever()


def open(port):
    run(start(port))
