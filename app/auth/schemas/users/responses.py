
from app.auth.schemas.user import BaseUser


class UserResponse(BaseUser):
    id: int

    class Config:
        orm_mode = True