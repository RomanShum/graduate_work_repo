import uuid
from pydantic import BaseModel, Field, AliasChoices


class UuidMixin(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)


class Person(UuidMixin, BaseModel):
    full_name: str = Field(validation_alias=AliasChoices('name', 'full_name'))


class ResponseFilm(UuidMixin, BaseModel):
    title: str
    imdb_rating: float
    description: str | None
    directors: list[Person] = Field(default_factory=list)
    actors: list[Person] = Field(default_factory=list)
    writers: list[Person] = Field(default_factory=list)


class ResponseFilmList(BaseModel):
    films: list[ResponseFilm] | None = Field(default_factory=list)
