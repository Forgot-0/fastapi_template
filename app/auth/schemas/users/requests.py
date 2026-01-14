from pydantic import BaseModel, Field

from app.auth.dtos.user import BaseUser
from app.auth.schemas.base import PasswordMixinSchema


class UserCreateRequest(BaseUser, PasswordMixinSchema):
    ...

class UserPermissionRequest(BaseModel):
    permissions: set[str] = Field(default_factory=set)
