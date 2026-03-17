from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.settings import Settings

settings = Settings()

_engine: AsyncEngine | None = None
_session_factory: sessionmaker | None = None

Base = declarative_base()


async def init_engine() -> None:
    global _engine, _session_factory
    if _engine is None:
        database_url = settings.DATABASE_URL
        _engine = create_async_engine(database_url, echo=False, connect_args={
            "server_settings": {
                "search_path": settings.schema_name
            }
        })
        _session_factory = sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


async def close_engine() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if _session_factory is None:
        await init_engine()
    assert _session_factory is not None
    async with _session_factory() as session:
        yield session
