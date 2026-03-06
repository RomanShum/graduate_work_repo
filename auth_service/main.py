from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from db.postgres import create_db_engine, dispose_db_engine

from db import redis
import logging
from core.logger import LOGGING
import uvicorn

from api.urls import router
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
    create_db_engine()
    yield
    dispose_db_engine()
    await redis.redis.close()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url='/docs',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(
        settings.app_start_method,
        host=settings.app_host,
        port=settings.app_port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=True
    )
