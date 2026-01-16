from pydantic import ConfigDict

from app.auth.dtos.user import BaseUser


class UserResponse(BaseUser):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)
    id: int
