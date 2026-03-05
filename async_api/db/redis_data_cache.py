from core.abstract_cache import AbstractCache
from core.settings import settings


class RedisDataCache(AbstractCache):
    def __init__(self, cache):
        self.cache = cache

    async def get_data(self, key):
        return await self.cache.get(key)

    async def set_data(self, key, data):
        await self.cache.set(key, data, settings.film_cache_expire_in_seconds)
