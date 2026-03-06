from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models.entity import User
from core.settings import settings
from sqlalchemy.future import select
import asyncio
import sys
import typer

sys.path.append('/app')

app = typer.Typer()


async def create_superuser(
        login: str,
        password: str,
        first_name: str,
        last_name: str
):
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.login == login))
        user = result.fetchone()

        if user:
            typer.echo(f"Пользователь с логином '{login}' уже существует.")
            return

        new_user = User(
            login=login,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=True
        )
        session.add(new_user)
        await session.commit()
        typer.echo(f"Суперпользователь '{login}' успешно создан.")

    await engine.dispose()


@app.command()
def main(login: str = typer.Option(..., prompt=True),
         password: str = typer.Option(..., prompt=True, hide_input=True),
         first_name: str = typer.Option(..., prompt=True),
         last_name: str = typer.Option(..., prompt=True), ):
    asyncio.run(create_superuser(login=login,
                                 password=password,
                                 first_name=first_name,
                                 last_name=last_name))


if __name__ == "__main__":
    app()
