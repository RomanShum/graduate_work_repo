from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service

from models.film import ResponseFilm, ResponseFilmList
from core.settings import settings

from core.page_dependency import PageDependency

router = APIRouter()


@router.get('/search', response_model=ResponseFilmList, response_model_by_alias=False, description="Get films by query")
async def film_search_list(
        page: Annotated[PageDependency, Depends(PageDependency)],
        query: Annotated[str, Query(title="query", description="Query")] = '',
        film_service: FilmService = Depends(get_film_service)
) -> ResponseFilm:
    films = await film_service.get_by_query_params(query=query, page_size=page.size, page_number=page.number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films


@router.get('/{film_id}', response_model=ResponseFilm, response_model_by_alias=False, description="Get film by id")
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> ResponseFilm:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return ResponseFilm(**dict(film))


@router.get('', response_model=ResponseFilmList, response_model_by_alias=False, description="Get films")
async def film_list(
        page: Annotated[PageDependency, Depends(PageDependency)],
        sort: Annotated[str, Query(title="sort", descrition="Sort")] = '',
        film_service: FilmService = Depends(get_film_service)) -> ResponseFilmList:
    films = await film_service.get_by_query_params(sort=sort, page_size=page.size, page_number=page.number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films
