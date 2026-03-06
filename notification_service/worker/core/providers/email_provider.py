from core.providers.base_provider import BaseProvider
from settings import Settings
from email.message import EmailMessage
import aiosmtplib
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from uuid import UUID

logger = logging.getLogger(__name__)
settings = Settings()


class EmailProvider(BaseProvider):
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.username = settings.username
        self.password = settings.password
        self.client = AsyncIOMotorClient(settings.database_mongo_url, uuidRepresentation='standard')
        self.db = self.client[settings.db_name]
        self.notifications = self.db[settings.db_table]

    async def send_notification(self, id_message, to_email, subject, body):
        message = EmailMessage()
        message['From'] = self.username
        message['To'] = to_email
        message['Subject'] = subject
        message.set_content(body)
        try:
            # async with aiosmtplib.SMTP(
            #         #hostname=self.smtp_host,
            #         #port=self.smtp_port,
            #         #username=self.username,
            #         #password=self.password,
            # ) as smtp:
            #     await smtp.send_message(message)
            async with aiosmtplib.SMTP(
                    hostname="mailhog",
                    port=1025,
            ) as smtp:
                await smtp.send_message(message)
                logger.info('The email was sent successfully.')
        except Exception as e:
            logger.error(f'Error: {e}')
        await self._success_notification_status(id_message)
        return True

    async def _success_notification_status(self, id_message):
        await self.notifications.find_one_and_update({"_id": UUID(id_message)}, {"$set": {"read": True}})
