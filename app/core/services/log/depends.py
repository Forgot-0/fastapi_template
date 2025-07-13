from app.core.services.log.base import LogServiceInterface
from app.core.services.log.structlog.service import StructLogService
from app.core.services.log.structlog.init import logger


def get_log_service() -> LogServiceInterface:
    return StructLogService(logger)