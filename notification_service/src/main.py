from models.entity import Notification
from contextlib import asynccontextmanager
from beanie import init_beanie
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from api.urls import router
from core.settings import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    client = AsyncIOMotorClient(settings.database_mongo_url)
    await init_beanie(database=client.db_name, document_models=[Notification])
    yield
    client.close()


app = FastAPI(
    lifespan=lifespan,
    title="App",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    description="App Service",
    version="0.1.0",
)

app.include_router(router)
