from dishka import FromDishka
from dishka.integrations.taskiq import inject
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.token import Token
from app.core.services.queue.task import BaseTask
from app.core.utils import now_utc


class RemoveInactiveTokens(BaseTask):
    __task_name__ = "token.remove"

    @staticmethod
    @inject
    async def run(session: FromDishka[AsyncSession]):
        stmt = delete(Token).where(Token.expires_at < now_utc())
        await session.execute(stmt)
        await session.commit()