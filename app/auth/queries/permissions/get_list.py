from dataclasses import dataclass

from app.auth.repositories.permission import PermissionRepository
from app.auth.schemas.permissions import PermissionDTO, PermissionListParams
from app.auth.schemas.user import UserJWTData
from app.auth.services.rbac import RBACManager
from app.core.api.schemas import PaginatedResult
from app.core.queries import BaseQuery, BaseQueryHandler


@dataclass(frozen=True)
class GetListPemissionsQuery(BaseQuery):
    permission_query: PermissionListParams
    user_jwt_data: UserJWTData


@dataclass(frozen=True)
class GetListPemissionsQueryHandler(BaseQueryHandler[GetListPemissionsQuery, list[PermissionDTO]]):
    permission_repository: PermissionRepository
    rbac_manager: RBACManager

    async def handle(self, query: GetListPemissionsQuery) -> PaginatedResult[PermissionDTO]:
        self.rbac_manager.check_permission(query.user_jwt_data, {"permission:view", })
        pagination_permissions = await self.permission_repository.get_list(
            query.permission_query
        )
        return PaginatedResult(
            items=[PermissionDTO.model_validate(permission) for permission in pagination_permissions],
            pagination=pagination_permissions.pagination
        )