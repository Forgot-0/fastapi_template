from fastapi import APIRouter

from app.auth.routes.v1 import auth, permissions, roles, sessions, user, oauth


router_v1 = APIRouter()
router_v1.include_router(auth.router, prefix='/auth', tags=['auth'])
router_v1.include_router(oauth.router, prefix='/oauth', tags=['oauth'])
router_v1.include_router(permissions.router, prefix='/permissions', tags=['permissions'])
router_v1.include_router(user.router, prefix='/users', tags=['users'])
router_v1.include_router(roles.router, prefix='/roles', tags=['roles'])
router_v1.include_router(sessions.router, prefix="/sessions", tags=['sessions'])