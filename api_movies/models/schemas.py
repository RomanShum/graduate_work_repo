from pydantic import BaseModel, Field
from uuid import UUID

class ResponseFilm(BaseModel):
    id: UUID
    title: str

class ResponseFilmList(BaseModel):
    films: list[ResponseFilm] | None = Field(default_factory=list)