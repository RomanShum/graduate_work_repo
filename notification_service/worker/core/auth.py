from settings import Settings
from core.models import User
import aiohttp
import logging
from uuid import UUID

settings = Settings()
logger = logging.getLogger(__name__)


class Auth:
    def __init__(self):
        self.url = settings.auth_url

    async def get_user_data(self, user_id: UUID):
        url = f"{self.url}/{user_id}"
        print(url)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Auth service error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Unexpected error in auth client: {str(e)}")
            return None


auth_client = Auth()
