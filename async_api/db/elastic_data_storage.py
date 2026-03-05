from core.abstract_cache import AbstractCache
from core.settings import settings

from core.abstract_storage import AbstractStorage


class ElasticDataStorage(AbstractStorage):
    def __init__(self, storage):
        self.storage = storage

    async def get_by_id(self, index, id):
        return await self.storage.get(index=index, id=id)

    async def get_list(self, index, body):
        return await self.storage.search(index=index, body=body)
