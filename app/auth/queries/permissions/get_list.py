from dataclasses import dataclass

from app.auth.models.permission import Permission
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
class GetListPemissionsQueryHandler(BaseQueryHandler[GetListPemissionsQuery, PaginatedResult[PermissionDTO]]):
    permission_repository: PermissionRepository
    rbac_manager: RBACManager

    async def handle(self, query: GetListPemissionsQuery) -> PaginatedResult[PermissionDTO]:
        if not self.rbac_manager.check_permission(query.user_jwt_data, {"permission:view", }):
            raise 

        pagination_permissions = await self.permission_repository.get_list(
            params=query.permission_query, model=Permission
        )

        return PaginatedResult(
            items=[PermissionDTO.model_validate(permission.to_dict()) for permission in pagination_permissions.items],
            pagination=pagination_permissions.pagination
        )