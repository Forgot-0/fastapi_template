from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationException(Exception):

    @property
    def message(self) -> str:
        return 'App error'

    @property
    def status(self) -> int:
        return 400


@dataclass(eq=False)
class NotHandlerRegistry(ApplicationException):
    @property
    def message(self) -> str:
        return 'Не был зарегестрирован обработчик'

    @property
    def status(self) -> int:
        return 500