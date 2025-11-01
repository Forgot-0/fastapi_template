from dataclasses import dataclass

from app.auth.repositories.session import SessionRepository
from app.auth.schemas.sessions import SessionDTO
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListSessionsUserQuery(BaseQuery):
    user_id: int


@dataclass(frozen=True)
class GetListSessionsUserQueryHandler(BaseQueryHandler[GetListSessionsUserQuery, list[SessionDTO]]):
    session_repository: SessionRepository

    async def handle(self, query: GetListSessionsUserQuery) -> list[SessionDTO]:
        result = await self.session_repository.get_active_by_user(user_id=query.user_id)
        return [SessionDTO.model_validate(session.to_dict()) for session in result]