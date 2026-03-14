import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_engine: AsyncEngine | None = None
_session_factory: sessionmaker | None = None

Base = declarative_base()

def _build_database_url() -> str:
  user = os.getenv("POSTGRES_USER", "postgres")
  password = os.getenv("POSTGRES_PASSWORD", "secret")
  db = os.getenv("POSTGRES_DB", "theatre")
  host = os.getenv("SQL_HOST", os.getenv("DB_HOST", "cinema_db"))
  port = os.getenv("SQL_PORT", os.getenv("DB_PORT", "5432"))
  return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


async def init_engine() -> None:
  global _engine, _session_factory
  if _engine is None:
    database_url = _build_database_url()
    _engine = create_async_engine(database_url, echo=False)
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

