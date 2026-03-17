import uuid
from enum import Enum

from sqlalchemy import Column, DateTime, String, Float, Enum as EnumSQL
from sqlalchemy.dialects.postgresql import UUID

from db import Base
from datetime import datetime


class TypeEnum(Enum):
    movie = "movie"


class FilmWork(Base):
    __tablename__ = 'film_work'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(255))
    creation_date = Column(DateTime, default=datetime.utcnow)
    rating = Column(Float, default=0.0)
    type = Column(EnumSQL(TypeEnum), nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)
