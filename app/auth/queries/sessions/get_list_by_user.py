from dataclasses import dataclass

from app.auth.dtos.sessions import SessionDTO
from app.auth.dtos.user import AuthUserJWTData
from app.auth.repositories.session import SessionRepository
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListSessionsUserQuery(BaseQuery):
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListSessionsUserQueryHandler(BaseQueryHandler[GetListSessionsUserQuery, list[SessionDTO]]):
    session_repository: SessionRepository

    async def handle(self, query: GetListSessionsUserQuery) -> list[SessionDTO]:
        result = await self.session_repository.get_active_by_user(user_id=int(query.user_jwt_data.id))
        return [SessionDTO.model_validate(session.to_dict()) for session in result]
