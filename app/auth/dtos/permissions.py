
from pydantic import BaseModel


class PermissionDTO(BaseModel):
    id: int
    name: str
