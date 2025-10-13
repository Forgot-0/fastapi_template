from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: set[str] = Field(default_factory=set)


class RoleAssignRequest(BaseModel):
    role_name: str


class RoleRemoveRequest(BaseModel):
    role_name: str


class RolePermissionRequest(BaseModel):
    permission: set[str] = Field(default_factory=set)

