from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from db import elastic
from db import redis
import logging
from core.logger import LOGGING
import uvicorn

from api.v1 import films
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=int(settings.redis_port))
    elastic.es = AsyncElasticsearch(hosts=[f'{settings.elastic_schema}://{settings.elastic_host}:{int(settings.elastic_port)}'])

    yield

    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])

if __name__ == '__main__':
    uvicorn.run(
        settings.app_start_method,
        host=settings.app_host,
        port=settings.app_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
