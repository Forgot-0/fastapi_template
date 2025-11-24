import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db.session import get_session

MAX_TRIES = 60 * 1  # 1 minutes
WAIT_SECOND = 5

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECOND),
    before=before_log(logger, logging.INFO),  # type: ignore
    after=after_log(logger, logging.INFO),  # type: ignore
)
async def init(db: AsyncSession) -> None:
    try:
        await db.execute(select(1))
    except Exception as exc:
        logger.error("database_init_error", extra={"error": exc}, exc_info=exc)
        raise exc


async def pre_start() -> None:
    logger.info("app_initialization_started")
    async for db in get_session():
        await init(db)
    logger.info("app_initialization_finished")
