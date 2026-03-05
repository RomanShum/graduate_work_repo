from redis.asyncio import Redis

from models.film import ResponseFilmList, ResponseFilm

from core.settings import settings

redis: Redis | None = None


async def get_redis() -> Redis:
    return redis
