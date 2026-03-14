from models.entity import Notification
from fastapi import HTTPException, status
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from kafka import KafkaProducer
from models.entity import UserRegistrationEvent, BaseEvent
from core.settings import Settings
from aiokafka import AIOKafkaProducer

settings = Settings()


async def get_notification_from_db(object_id: UUID, type: str) -> Optional[Notification]:
    return await Notification.find_one(Notification.object_id == object_id, Notification.type == type)


async def event(data: BaseEvent):
    notification = Notification(
        id=uuid4(),
        object_id=data.object_id,
        room_id=data.room_id,
        type=data.type,
        created_at=datetime.now(),
        read=False
    )
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await producer.start()
    try:
        await producer.send_and_wait("event", notification.model_dump_json().encode('utf-8'))
    finally:
        await producer.stop()
    return await notification.insert()