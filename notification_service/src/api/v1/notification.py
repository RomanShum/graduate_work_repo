from fastapi import APIRouter, Depends, Request, status
from services import notification_service
from models.entity import Notification, UserRegistrationEvent, NewContentEvent, CreateRoomEvent

router = APIRouter(prefix="/event", tags=["events"])


@router.post("/register", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def register(
        body: UserRegistrationEvent
) -> Notification:
    return await notification_service.event(data=body)


@router.post("/new", response_model=Notification)
async def register(
        body: NewContentEvent
) -> Notification:
    return await notification_service.event(data=body)

@router.post("/create_room", response_model=Notification)
async def create_room(
        body: CreateRoomEvent
) -> Notification:
    print(body)
    return await notification_service.event(data=body)
