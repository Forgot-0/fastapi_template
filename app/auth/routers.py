from fastapi import APIRouter

from app.auth.routes.v1 import auth, user, roles

router_v1 = APIRouter()
router_v1.include_router(auth.router, prefix='/auth', tags=['auth'])
router_v1.include_router(user.router, prefix='/users', tags=['users'])
router_v1.include_router(roles.router, prefix='/roles', tags=['roles'])