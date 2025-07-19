"""
Example showing how to properly setup the DI system with all components.

This file demonstrates:
1. How to register command and query handlers
2. How to register event handlers
3. How to use the mediator pattern
4. How to inject dependencies in FastAPI endpoints
"""

from dishka import Container
from fastapi import FastAPI, Depends
from app.core.di import setup_di, inject, get_container
from app.core.mediators.base import BaseMediator

# Import all command handlers
from app.auth.commands.users.register import RegisterCommand, RegisterCommandHandler
from app.auth.commands.auth.login import LoginCommand, LoginCommandHandler

# Import all query handlers
from app.auth.queries.users.get_by_id import GetUserByIdQuery, GetUserByIdQueryHandler
from app.auth.queries.auth.get_current_user import GetCurrentUserQuery, GetCurrentUserQueryHandler

# Import all event handlers
from app.auth.events.users.created import CreatedUserEvent, CreatedUserEventHandler
from app.auth.events.users.verified import VerifiedUserEvent, VerifiedUserEventHandler


def setup_handlers_registration():
    """
    Example of how to register all handlers with their respective registries.
    This would typically be done during application startup.
    """
    container = get_container()
    
    with container() as app_scope:
        # Get registries
        command_registry = app_scope.get(type[CommandHandlerRegistry])  # type: ignore
        query_registry = app_scope.get(type[QueryHandlerRegistry])  # type: ignore
        event_registry = app_scope.get(type[EventHandlerRegistry])  # type: ignore
        
        # Register command handlers
        command_registry.register(RegisterCommand, RegisterCommandHandler)
        command_registry.register(LoginCommand, LoginCommandHandler)
        
        # Register query handlers
        query_registry.register(GetUserByIdQuery, GetUserByIdQueryHandler)
        query_registry.register(GetCurrentUserQuery, GetCurrentUserQueryHandler)
        
        # Register event handlers
        event_registry.subscribe(CreatedUserEvent, [
            EventHandlerInfo(handler_type=CreatedUserEventHandler)
        ])
        event_registry.subscribe(VerifiedUserEvent, [
            EventHandlerInfo(handler_type=VerifiedUserEventHandler)
        ])


# Example FastAPI endpoints using DI
app = FastAPI()
setup_di(app)


@app.post("/users/register")
async def register_user(
    request_data: dict,
    mediator: BaseMediator = inject(BaseMediator),
):
    """Example endpoint using mediator pattern."""
    command = RegisterCommand(
        username=request_data["username"],
        email=request_data["email"],
        password=request_data["password"],
        password_repeat=request_data["password_repeat"]
    )
    
    results = await mediator.handle_command(command)
    return {"user": results[0] if results else None}


@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    mediator: BaseMediator = inject(BaseMediator),
):
    """Example endpoint using query pattern."""
    query = GetUserByIdQuery(user_id=user_id)
    result = await mediator.handle_query(query)
    return {"user": result}


@app.get("/users/me")
async def get_current_user(
    token: str,
    mediator: BaseMediator = inject(BaseMediator),
):
    """Example endpoint with authentication."""
    query = GetCurrentUserQuery(token=token)
    result = await mediator.handle_query(query)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user": result}


# Alternative: Direct dependency injection without mediator
from app.auth.repositories.user import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession


@app.get("/users/{user_id}/direct")
async def get_user_direct(
    user_id: int,
    session: AsyncSession = inject(AsyncSession),
    user_repo: UserRepository = inject(UserRepository),
):
    """Example of direct repository injection."""
    user = await user_repo.get_by_id(session, user_id)
    if user:
        return {"user": user.to_dict()}
    return {"user": None}


# Example of service injection
from app.core.services.mail.service import MailServiceInterface
from app.core.services.cache.base import CacheServiceInterface


@app.post("/send-email")
async def send_email(
    request_data: dict,
    mail_service: MailServiceInterface = inject(MailServiceInterface),
    cache_service: CacheServiceInterface = inject(CacheServiceInterface),
):
    """Example of service injection."""
    # Use cache to check if email was recently sent
    cache_key = f"email_sent:{request_data['email']}"
    recently_sent = await cache_service.get(cache_key)
    
    if recently_sent:
        return {"message": "Email was recently sent"}
    
    # Send email
    await mail_service.send_plain(
        subject=request_data["subject"],
        recipient=request_data["email"], 
        body=request_data["body"]
    )
    
    # Cache that email was sent
    await cache_service.set(cache_key, True, ttl=300)  # 5 minutes
    
    return {"message": "Email sent successfully"}


if __name__ == "__main__":
    # Setup handlers during startup
    setup_handlers_registration()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)