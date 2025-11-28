from pydantic import BaseModel


class PermissionCreateRequest(BaseModel):
    name: str

