
from pydantic import BaseModel, Field



class BaseRole(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: list[str] = Field(default_factory=list)


class RoleDTO(BaseRole):
    id: int

