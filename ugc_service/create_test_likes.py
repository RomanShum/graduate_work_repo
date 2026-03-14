import asyncio
import random
import sys
from typing import List
from uuid import UUID

import typer
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from core.settings import Settings
from models.entity import Like, Favorite, Review

sys.path.append("/opt/app")

app = typer.Typer(help="Создание тестовых лайков фильмов в Mongo (UGC).")


async def _load_user_ids(session: AsyncSession, limit: int) -> List[str]:
    query = text(
        """
        SELECT id
        FROM public.users
        ORDER BY login
        LIMIT :limit
        """
    )
    result = await session.execute(query, {"limit": limit})
    return [str(row.id) for row in result.fetchall()]


async def _load_film_ids(session: AsyncSession, limit: int) -> List[str]:
    query = text(
        """
        SELECT id
        FROM content.film_work
        ORDER BY rating DESC NULLS LAST, title
        LIMIT :limit
        """
    )
    result = await session.execute(query, {"limit": limit})
    return [str(row.id) for row in result.fetchall()]


async def _create_likes(
        users_limit: int,
        films_limit: int,
) -> None:
    settings = Settings()
    pg_url = settings.DATABASE_URL

    engine = create_async_engine(pg_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        user_ids = await _load_user_ids(session, users_limit)
        film_ids = await _load_film_ids(session, films_limit)

    await engine.dispose()

    if not user_ids or not film_ids:
        typer.echo("Нет пользователей или фильмов для генерации лайков.")
        return

    # Подключаемся к Mongo / Beanie
    client = AsyncIOMotorClient(settings.database_mongo_url)
    await init_beanie(database=client.db_name, document_models=[Like, Favorite, Review])
    await Favorite.delete_all()
    # Простая генерация: для каждого пользователя лайкаем случайные 3 фильма
    for uid in user_ids:
        liked_films = [
            '3d825f60-9fff-4dfe-b294-1a45fa1e115d',
            '0312ed51-8833-413f-bff5-0e139c11264a',
            '025c58cd-1b7e-43be-9ffb-8571a613579b',
            'cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394',
            '3b914679-1f5e-4cbd-8044-d13d35d5236c'
        ]
        for fid in liked_films:
            like = Favorite(user_id=uid, film_id=UUID(fid), like_value=random.randint(7, 10))
            await like.insert()

    client.close()
    typer.echo(f"Созданы лайки для {len(user_ids)} пользователей.")


@app.command()
def main(
        users_limit: int = typer.Option(6, help="Сколько пользователей взять из Postgres"),
        films_limit: int = typer.Option(30, help="Сколько фильмов взять для лайков"),
):
    """
    Создать тестовые лайки фильмов в Mongo для существующих пользователей и фильмов.
    """
    asyncio.run(_create_likes(users_limit=users_limit, films_limit=films_limit))


if __name__ == "__main__":
    app()
