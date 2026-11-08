from pydantic import UUID4


class UserNotFoundError(Exception):
    def __init__(self, uid: UUID4):
        self.uid = uid


class UsernameAlreadyExistsError(Exception):
    def __init__(self, username: str):
        self.username = username
