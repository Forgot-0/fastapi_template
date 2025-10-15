from pydantic import BaseModel


class PermissionCreateRequest(BaseModel):
    name: str

class PermissionDeleteRequest(BaseModel):
    name: str
