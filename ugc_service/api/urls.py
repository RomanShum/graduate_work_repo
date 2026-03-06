from fastapi import APIRouter

from api.v1 import like, favorite, review

router = APIRouter(prefix='/api')

router.include_router(like.router, prefix='/v1')
router.include_router(review.router, prefix='/v1')
router.include_router(favorite.router, prefix='/v1')
