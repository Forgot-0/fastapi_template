from dataclasses import dataclass

from app.auth.dtos.role import RoleDTO
from app.auth.dtos.user import AuthUserJWTData
from app.auth.filters.roles import RoleFilter
from app.auth.models.role import Role
from app.auth.repositories.role import RoleRepository
from app.auth.services.rbac import AuthRBACManager
from app.core.db.repository import PageResult
from app.core.queries import BaseQuery, BaseQueryHandler
from app.core.services.auth.exceptions import AccessDeniedException


@dataclass(frozen=True)
class GetListRolesQuery(BaseQuery):
    role_filter: RoleFilter
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListRolesQueryHandler(BaseQueryHandler[GetListRolesQuery, PageResult[RoleDTO]]):
    role_repository: RoleRepository
    rbac_manager: AuthRBACManager

    async def handle(self, query: GetListRolesQuery) -> PageResult[RoleDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"role:view" }):
            raise AccessDeniedException(need_permissions={"role:view"} - set(query.user_jwt_data.permissions))

        pagination_roles = await self.role_repository.find_by_filter(
            model=Role, filters=query.role_filter
        )

        return PageResult(
            items=[RoleDTO.model_validate(role.to_dict()) for role in pagination_roles.items],
            total=pagination_roles.total,
            page=pagination_roles.page,
            page_size=pagination_roles.page_size
        )
