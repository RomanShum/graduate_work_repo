from fastapi import APIRouter

from api.v1 import user, roles

router = APIRouter(prefix='/auth')

router.include_router(user.router, prefix='/v1')
router.include_router(roles.router, prefix='/v1')
