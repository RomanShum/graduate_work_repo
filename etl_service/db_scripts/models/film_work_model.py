from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class Person(BaseModel):
    id: str
    name: str


class FilmWorkModel(BaseModel):
    id: UUID
    imdb_rating: float | None = Field(default=None)
    genres: List[str] = Field(default_factory=list)
    title: str
    description: str | None = Field(default=None)
    directors: List[Person] | None = Field(default_factory=list)
    actors_names: List[str] = Field(default_factory=list)
    directors_names: List[str] = Field(default_factory=list)
    writers_names: List[str] = Field(default_factory=list)
    actors: List[Person] = Field(default_factory=list)
    writers: List[Person] = Field(default_factory=list)
