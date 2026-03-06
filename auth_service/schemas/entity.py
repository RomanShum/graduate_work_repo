from uuid import UUID

from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class LoginHistorySchema(BaseModel):
    user_agent: str
    login_at: datetime


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    login: str | None = None
    password: str | None = None


class RoleCreate(BaseModel):
    name: str
    description: str


class AssignRole(BaseModel):
    user_id: str
    role_id: str


class CheckPermission(BaseModel):
    role_name: str
    user_id: str = None

    class Config:
        orm_mode = True
