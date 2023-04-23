from .protocol import Message


def put(message: Message):
    assert_role(message.session, ['user'])


def handshake(user: str, secret: str):
    pass


def assert_role(session, roles: list[str]):
    pass
