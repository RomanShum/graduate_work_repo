from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import CurrentUser, get_current_user
from db import get_session

from models.schemas import ResponseFilmList
from services import movies_service

router = APIRouter(tags=["films"])


@router.get("/films/", response_model=ResponseFilmList)
async def list_films(
        limit: int = 50,
        db: AsyncSession = Depends(get_session),
        current_user: CurrentUser = Depends(get_current_user),
):
    films = await movies_service.get_movies_list_service(db=db, limit=limit)
    if not films:
        return []
    return ResponseFilmList(films=films)
