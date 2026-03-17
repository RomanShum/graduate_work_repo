from core.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.entity import FilmWork

from models.schemas import ResponseFilm


async def get_movies_list_service(db: AsyncSession, limit: int):
    query = (select(FilmWork).
             limit(limit))

    result = await db.execute(query)
    films = result.scalars().all()
    return [ResponseFilm(title=film.title, id=film.id) for film in films]
