from .struct import Message


def put(message: Message):
    assert_role(message, ['user'])


def assert_role(session, roles: list[str]):
    pass
