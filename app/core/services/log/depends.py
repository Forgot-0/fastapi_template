from loguru import logger

from app.core.services.log.base import LogServiceInterface


def get_log_service() -> LogServiceInterface:
    return logger