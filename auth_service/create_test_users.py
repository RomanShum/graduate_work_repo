import asyncio
import random
import sys
from typing import Iterable

import typer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from core.settings import settings
from models.entity import User

sys.path.append("/app")


app = typer.Typer(help="Создание тестовых пользователей для сервиса авторизации.")


FIRST_NAMES = [
    "Иван",
    "Петр",
    "Сергей",
    "Анна",
    "Мария",
    "Ольга",
    "Дмитрий",
    "Алексей",
    "Екатерина",
    "Татьяна",
]

LAST_NAMES = [
    "Иванов",
    "Петров",
    "Сидоров",
    "Смирнов",
    "Кузнецов",
    "Попов",
    "Соколов",
    "Лебедев",
    "Козлов",
    "Новиков",
]


async def _user_exists(session: AsyncSession, login: str) -> bool:
    result = await session.execute(select(User).where(User.login == login))
    return result.scalar_one_or_none() is not None


async def _create_users(count: int, base_login: str, password: str) -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        created = 0
        for idx in range(1, count + 1):
            login = f"{base_login}{idx}"
            if await _user_exists(session, login):
                continue

            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            user = User(
                login=login,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_superuser=False,
                email=f"{login}@example.com"
            )
            session.add(user)
            created += 1

        if created:
            await session.commit()

    await engine.dispose()
    typer.echo(f"Создано пользователей: {created}")


@app.command()
def main(
    count: int = typer.Option(10, help="Количество создаваемых пользователей"),
    base_login: str = typer.Option("user", help="Префикс логина, например user -> user1, user2"),
    password: str = typer.Option("password", help="Пароль для всех тестовых пользователей"),
):
    """
    Создать набор тестовых пользователей в базе Auth Service.
    """
    asyncio.run(_create_users(count=count, base_login=base_login, password=password))


if __name__ == "__main__":
    app()

