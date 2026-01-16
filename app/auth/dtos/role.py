from pydantic import BaseModel, Field

from app.auth.dtos.permissions import PermissionDTO


class BaseRole(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: list[PermissionDTO] = Field(default_factory=list)


class RoleDTO(BaseRole):
    id: int

