from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.dtos.permissions import PermissionDTO
from app.auth.dtos.role import RoleDTO
from app.auth.dtos.sessions import SessionDTO
from app.auth.models.user import User
from app.core.services.auth.dto import UserJWTData


class BaseUser(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    username: str = Field(
        min_length=4,
        max_length=100,
        pattern=r"^[a-zA-Z0-9 ,.\'-]+$",
    )
    email: EmailStr


class AuthUserJWTData(UserJWTData):
    @classmethod
    def create_from_user(cls, user: User, device_id: str | None=None) -> "AuthUserJWTData":
        security_lvl = 0
        permissions = set()
        roles = set()

        for role in user.roles:
            roles.add(role.name)

            security_lvl = max(security_lvl, role.security_level)

            for permission in role.permissions:
                permissions.add(permission.name)

        for permission in user.permissions:
            permissions.add(permission.name)

        return cls(
            id=str(user.id),
            security_level=security_lvl,
            roles=list(roles),
            permissions=list(permissions),
            device_id=device_id
        )


class UserDTO(BaseUser):
    id: int

    roles: list[RoleDTO] = Field(default_factory=list)
    permissions: list[PermissionDTO] = Field(default_factory=list)
    sessions: list[SessionDTO] = Field(default_factory=list)

    is_active: bool
    is_verified: bool
