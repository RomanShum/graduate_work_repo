from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    first_name: str
    email: str
