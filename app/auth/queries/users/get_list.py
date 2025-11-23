from dataclasses import dataclass

from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.schemas.user import UserDTO, UserJWTData, UserListParams
from app.auth.services.rbac import RBACManager
from app.core.api.schemas import PaginatedResult
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListUserQuery(BaseQuery):
    user_query: UserListParams
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class GetListUserQueryHandler(BaseQueryHandler[GetListUserQuery, PaginatedResult[UserDTO]]):
    user_repository: UserRepository
    rbac_manager: RBACManager

    async def handle(self, query: GetListUserQuery) -> PaginatedResult[UserDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"user:view", }):
            raise 

        pagination_users = await self.user_repository.get_list(
            params=query.user_query, model=User, relations={"select": ["permissions", "roles.permissions"]}
        )

        return PaginatedResult(
            items=[UserDTO.model_validate(user.to_dict()) for user in pagination_users.items],
            pagination=pagination_users.pagination
        )