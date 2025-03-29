from abc import ABC, abstractmethod
from typing import Any


class LogServiceInterface(ABC):
    @abstractmethod
    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def info(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def error(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...

    @abstractmethod
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        ...
