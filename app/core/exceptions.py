from dataclasses import dataclass
from typing import ClassVar



@dataclass(eq=False)
class ApplicationException(Exception):
    status: ClassVar[int] = 500

    @property
    def message(self) -> str:
        return 'App error'


@dataclass(eq=False)
class NotHandlerRegistry(ApplicationException):
    @property
    def message(self) -> str:
        return 'Не был зарегестрирован обработчик'