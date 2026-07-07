from pydantic import BaseModel, ConfigDict, Field

from app.auth.dtos.permissions import PermissionDTO


class BaseRole(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: list[PermissionDTO] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoleDTO(BaseRole):
    id: int

