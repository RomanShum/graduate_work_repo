from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from core.utils import create_query_by_elastic, get_key
from db.redis import get_redis
from models.film import ResponseFilm, ResponseFilmList
from core.settings import settings

from core.abstract_cache import AbstractCache
from db.redis_data_cache import RedisDataCache

from core.abstract_storage import AbstractStorage
from db.elastic_data_storage import ElasticDataStorage


class FilmService:
    def __init__(self, cache: AbstractCache, storage: AbstractStorage):
        self.storage = storage
        self.cache = cache

    async def get_by_query_params(self,
                                  sort: str = '',
                                  page_size: int = settings.page_size,
                                  page_number: int = settings.page_number,
                                  query: str = ''
                                  ) -> ResponseFilmList | None:

        key = get_key(params=[sort, page_size, page_number, query])
        films = await self._from_cache_by_params(key=key, model_response=ResponseFilmList)

        if not films:
            films = await self._get_film_from_elastic_by_params(sort=sort,
                                                                page_size=page_size,
                                                                page_number=page_number,
                                                                query=query)
            if not films:
                return None
            await self._put_to_cache(key=key, data=films)
        return films

    async def get_by_id(self, film_id: str) -> ResponseFilm | None:
        key = get_key(params=[film_id])
        film = await self._from_cache_by_params(key=key, model_response=ResponseFilm)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_to_cache(key=key, data=film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> ResponseFilm | None:
        try:
            doc = await self.storage.get_by_id(index='movies', id=film_id)
        except NotFoundError:
            return None
        return ResponseFilm(**doc['_source'])

    async def _get_film_from_elastic_by_params(self, sort, page_size, page_number, query) -> ResponseFilmList | None:
        try:
            body = create_query_by_elastic(sort=sort, page_size=page_size, page_number=page_number, query=query)
            docs = await self.storage.get_list(index='movies', body=body)
        except NotFoundError:
            return None
        return ResponseFilmList(films=[ResponseFilm(**doc['_source']) for doc in docs['hits']['hits']])

    async def _put_to_cache(self, key: str, data):
        await self.cache.set_data(key, data.json())

    async def _from_cache_by_params(self, key: str, model_response):

        data = await self.cache.get_data(key)

        if not data:
            return None

        result = model_response.parse_raw(data)
        return result


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    cache = RedisDataCache(redis)
    storage = ElasticDataStorage(elastic)
    return FilmService(cache, storage)
