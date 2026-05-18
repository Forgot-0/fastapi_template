from dataclasses import dataclass

from app.auth.dtos.sessions import SessionDTO
from app.auth.dtos.user import AuthUserJWTData
from app.auth.filters.sessions import SessionFilter
from app.auth.models.session import Session
from app.auth.repositories.session import SessionRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.db.repository import PageResult
from app.core.queries import BaseQuery, BaseQueryHandler
from app.core.services.auth.exceptions import AccessDeniedException


@dataclass(frozen=True)
class GetListSessionQuery(BaseQuery):
    session_filter: SessionFilter
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListSessionQueryHandler(BaseQueryHandler[GetListSessionQuery, PageResult[SessionDTO]]):
    session_repository: SessionRepository
    rbac_manager: AuthRBACManager

    async def handle(self, query: GetListSessionQuery) -> PageResult[SessionDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"user:view" }):
            raise AccessDeniedException(need_permissions={"user:view"} - set(query.user_jwt_data.permissions))

        pagination_session = await self.session_repository.find_by_filter(
            model=Session, filters=query.session_filter
        )
        return PageResult(
            items=[SessionDTO.model_validate(session.to_dict()) for session in pagination_session.items],
            total=pagination_session.total,
            page=pagination_session.page,
            page_size=pagination_session.page_size
        )
