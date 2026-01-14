from dataclasses import dataclass

from app.auth.dtos.role import RoleDTO, RoleListParams
from app.auth.dtos.user import AuthUserJWTData
from app.auth.exceptions import AccessDeniedException
from app.auth.models.role import Role
from app.auth.repositories.role import RoleRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.api.schemas import PaginatedResult
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListRolesQuery(BaseQuery):
    role_query: RoleListParams
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListRolesQueryHandler(BaseQueryHandler[GetListRolesQuery, PaginatedResult[RoleDTO]]):
    role_repository: RoleRepository
    rbac_manager: AuthRBACManager

    async def handle(self, query: GetListRolesQuery) -> PaginatedResult[RoleDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"role:view" }):
            raise AccessDeniedException(need_permissions={"role:view"} - set(query.user_jwt_data.permissions))

        pagination_roles = await self.role_repository.get_list(
            params=query.role_query, model=Role, relations={"select": ["permissions"]}
        )

        return PaginatedResult(
            items=[RoleDTO.model_validate(role.to_dict()) for role in pagination_roles.items],
            pagination=pagination_roles.pagination
        )
