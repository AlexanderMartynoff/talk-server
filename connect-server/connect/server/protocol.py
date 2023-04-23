from uuid import uuid4
from msgspec import Struct, field, UNSET, UnsetType as Unset
import msgspec


class Element(Struct, kw_only=True):
    id: str = field(default_factory=uuid4)
    sender: str
    receiver: str


class Media(Struct, kw_only=True, tag=True):
    str: str
    format: str
    value: bytes


class Message(Element, kw_only=True, tag=True):
    value: str | Unset = UNSET
    media: Media | Unset = UNSET


class Handshake(Element, kw_only=True, tag=True):
    secret: str


class Ping(Element, kw_only=True, tag=True):
    pass


class Pong(Element, kw_only=True, tag=True):
    pass


class Delivery(Element, kw_only=True, tag=True):
    taget: str
    reverse_id: str


def decode(data: bytes) -> Element:
    if data[-1] == 0:
        data = data[:-1]

    return msgspec.json.decode(data, type=Message | Handshake | Ping | Pong | Delivery)


def encode(message: Message, terminate: bool = True) -> bytes:
    data = msgspec.json.encode(message)

    if terminate:
        data += b'\0'

    return data


def delivery(message: Message) -> Delivery:
    return Delivery(sender=message.receiver, receiver=message.sender, taget='server', reverse_id=message.id)
