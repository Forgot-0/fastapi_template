from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dishka.integrations.fastapi import FromDishka

from app.auth.models.user import User
from app.auth.repositories.user import UserRepository
from app.auth.security import decode_access_token
from app.core.mediators.imediator import DishkaMediator
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

# Type aliases for dependency injection
MediatorAuth = Annotated[DishkaMediator, FromDishka()]

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, FromDishka()],
    user_repository: Annotated[UserRepository, FromDishka()],
) -> User:
    """
    Получает текущего пользователя из JWT токена.
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials", 
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repository.get_by_id(session, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Проверяет, что пользователь активен.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

# Type alias for active user dependency
ActiveUserModel = Annotated[User, Depends(get_active_user)]