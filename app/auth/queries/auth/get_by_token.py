from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.security import verify_token
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetByAcccessTokenQuery(BaseQuery):
    token: str


@dataclass(frozen=True)
class GetByAcccessTokenQueryHandler(BaseQueryHandler[GetByAcccessTokenQuery, User]):
    session: AsyncSession
    user_repository: UserRepository

    async def handle(self, query: GetByAcccessTokenQuery) -> User:
        token_data = verify_token(token=query.token, token_type="access")
        user_id = token_data.sub
        if not user_id:
            raise 

        user = await self.user_repository.get_by_id(self.session, int(user_id))
        if not user:
            raise

        return user