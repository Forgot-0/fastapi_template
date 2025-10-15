
from pydantic import BaseModel, Field



class BaseRole(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: set[str] = Field(default_factory=set)


class RoleDTO(BaseRole):
    id: int


