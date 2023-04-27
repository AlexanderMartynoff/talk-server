import enum
from time import time
from uuid import uuid4
from msgspec import Struct, field, UNSET, UnsetType as Unset
import msgspec


class Media(Struct, kw_only=True):
    value: bytes
    name: str


class Element(Struct, kw_only=True):
    id: str = field(default_factory=uuid4)
    time: float = field(default_factory=time)
    sender: str
    receiver: str


class Message(Element, kw_only=True, tag=True):
    value: str | Unset = UNSET
    media: Media | Unset = UNSET


class Identity(Element, kw_only=True, tag=True):
    session: str
    password: str


class Heartbeat(Element, kw_only=True, tag=True):
    pass


class Status(Element, kw_only=True, tag=True):
    class Value(enum.Enum):
        ACCEPTED = enum.auto()
        READED = enum.auto()

    value: Value
    message_id: str


def status(message: Message, value: Status.Value) -> Status:
    return Status(
        sender=message.receiver,
        receiver=message.sender,
        message_id=message.id,
        value=value)


def decode(data: bytes) -> Element:
    if data[-1:] == b'\0':
        data = data[:-1]

    return msgspec.json.decode(data, type=Message | Identity | Heartbeat | Status)


def encode(message: Message, terminate: bool = True) -> bytes:
    data = msgspec.json.encode(message)

    if terminate:
        data += b'\0'

    return data
