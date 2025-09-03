from dataclasses import dataclass

from app.core.exceptions import ApplicationException


@dataclass(eq=False)
class AlreadyUserEmail(ApplicationException):
    field: str

    @property
    def message(self):
        return f'Пользователь с таким email уже существую'

    @property
    def status(self) -> int:
        return 400

@dataclass(eq=False)
class AlreadyUserUsername(ApplicationException):
    field: str

    @property
    def message(self):
        return f'Пользователь с таким username уже существую'

    @property
    def status(self) -> int:
        return 400

@dataclass(eq=False)
class InvalidJWTToken(ApplicationException):
    @property
    def message(self):
        return 'Неправильный токен'

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class NotFoundUserBy(ApplicationException):
    text: str

    @property
    def message(self):
        return f"Пользователь с таким {self.text} не найдем"

    @property
    def status(self) -> int:
        return 404


