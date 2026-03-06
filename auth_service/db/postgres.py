from core.settings import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

Base = declarative_base()

engine = None
async_session = None


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def create_db_engine():
    global engine, async_session
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def dispose_db_engine():
    if engine:
        engine.sync_engine.dispose()
