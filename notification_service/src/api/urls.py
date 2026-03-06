from fastapi import APIRouter

from api.v1 import notification

router = APIRouter(prefix="/notification")

router.include_router(notification.router, prefix="/v1")
