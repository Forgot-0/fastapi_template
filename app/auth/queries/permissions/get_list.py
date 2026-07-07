from dataclasses import dataclass

from app.auth.dtos.permissions import PermissionDTO
from app.auth.dtos.user import AuthUserJWTData
from app.auth.filters.permissions import PermissionFilter
from app.auth.models.permission import Permission
from app.auth.repositories.permission import PermissionRepository
from app.core.db.repository import PageResult
from app.core.queries import BaseQuery, BaseQueryHandler
from app.core.services.auth.exceptions import AccessDeniedError
from app.core.services.auth.rbac import RBACManagerInterface


@dataclass(frozen=True)
class GetListPemissionsQuery(BaseQuery):
    permission_filter: PermissionFilter
    user_jwt_data: AuthUserJWTData


@dataclass(frozen=True)
class GetListPemissionsQueryHandler(BaseQueryHandler[GetListPemissionsQuery, PageResult[PermissionDTO]]):
    permission_repository: PermissionRepository
    rbac_manager: RBACManagerInterface

    async def handle(self, query: GetListPemissionsQuery) -> PageResult[PermissionDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"permission:view" }):
            raise AccessDeniedError(need_permissions={"permission:view"} - set(query.user_jwt_data.permissions))

        pagination_permissions = await self.permission_repository.find_by_filter(
            model=Permission, filters=query.permission_filter
        )

        return PageResult(
            items=[
                PermissionDTO.model_validate(permission)
                for permission in pagination_permissions.items
            ],
            total=pagination_permissions.total,
            page=pagination_permissions.page,
            page_size=pagination_permissions.page_size
        )
