from dataclasses import dataclass

from app.auth.models.role import Role
from app.auth.repositories.role import RoleRepository
from app.auth.schemas.role import RoleDTO, RoleListParams
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.api.schemas import PaginatedResult
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListRolesQuery(BaseQuery):
    role_query: RoleListParams
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class GetListRolesQueryHandler(BaseQueryHandler[GetListRolesQuery, PaginatedResult[RoleDTO]]):
    role_repository: RoleRepository
    rbac_manager: RBACManager

    async def handle(self, query: GetListRolesQuery) -> PaginatedResult[RoleDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"role:view", }):
            raise

        pagination_roles = await self.role_repository.get_list(
            params=query.role_query, model=Role
        )

        return PaginatedResult(
            items=[RoleDTO.model_validate(role.to_dict()) for role in pagination_roles.items],
            pagination=pagination_roles.pagination
        )