from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    name: str
    description: str
    security_level: int
    permissions: list[str] = Field(default_factory=list)
