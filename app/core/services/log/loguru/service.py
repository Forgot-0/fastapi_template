from typing import Any
from app.core.services.log.base import LogServiceInterface
from loguru import logger


class LoguruLogService(LogServiceInterface):
    def __init__(self) -> None:
        self._logger = logger

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> Any:
        return self._logger.exception(msg, *args, **kwargs)
