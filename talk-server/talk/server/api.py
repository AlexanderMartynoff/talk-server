from .struct import Message


def put(message: Message) -> None:
    assert_role(message, ['user'])


def assert_role(session, roles: list[str]) -> None:
    pass
