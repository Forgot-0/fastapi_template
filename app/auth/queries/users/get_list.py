from dataclasses import dataclass

from app.auth.dtos.user import AuthUserJWTData, UserDTO
from app.auth.exceptions import AccessDeniedException
from app.auth.filters.users import UserFilter
from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.db.repository import PageResult
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListUserQuery(BaseQuery):
    user_filter: UserFilter
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListUserQueryHandler(BaseQueryHandler[GetListUserQuery, PageResult[UserDTO]]):
    user_repository: UserRepository
    rbac_manager: AuthRBACManager

    async def handle(self, query: GetListUserQuery) -> PageResult[UserDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"user:view" }):
            raise AccessDeniedException(need_permissions={"user:view"} - set(query.user_jwt_data.permissions))

        pagination_users = await self.user_repository.find_by_filter(
            User,
            filters=query.user_filter
        )

        return PageResult(
            items=[UserDTO.model_validate(user.to_dict()) for user in pagination_users.items],
            total=pagination_users.total,
            page=pagination_users.page,
            page_size=pagination_users.page_size
        )
