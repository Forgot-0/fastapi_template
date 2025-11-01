from dataclasses import dataclass

from app.auth.models.session import Session
from app.auth.repositories.session import SessionRepository
from app.auth.schemas.sessions import SessionDTO, SessionListParams
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.api.schemas import PaginatedResult
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListSessionQuery(BaseQuery):
    session_query: SessionListParams
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class GetListSessionQueryHandler(BaseQueryHandler[GetListSessionQuery, PaginatedResult[SessionDTO]]):
    session_repository: SessionRepository
    rbac_manager: RBACManager

    async def handle(self, query: GetListSessionQuery) -> PaginatedResult[SessionDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"user:view", }):
            raise

        pagination_session = await self.session_repository.get_list(
            Session, params=query.session_query
        )
        return PaginatedResult(
            items=[SessionDTO.model_validate(session.to_dict()) for session in pagination_session.items],
            pagination=pagination_session.pagination
        )