from pydantic import BaseModel, Field

from app.auth.schemas.base import PasswordMixinSchema
from app.auth.schemas.user import BaseUser


class UserCreateRequest(BaseUser, PasswordMixinSchema):
    ...

class UserPermissionRequest(BaseModel):
    permissions: set[str] = Field(default_factory=set)
