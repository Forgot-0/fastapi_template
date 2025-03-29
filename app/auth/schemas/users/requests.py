from app.auth.schemas.base import PasswordMixinSchema
from app.auth.schemas.user import BaseUser


class UserCreateRequest(BaseUser, PasswordMixinSchema):
    ...