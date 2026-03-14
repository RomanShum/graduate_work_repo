from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    sentry_dsn: Optional[str] = None
    event_ttl: int = 30
    project_name: str = 'app'
    min_review_length: int = 1
    max_review_length: int = 5000
    app_start_method: str = 'main:app'
    app_host: str = '0.0.0.0'
    database_mongo_url: str = Field(default="mongodb://mongodb:27017")
    secret_key: str = "your-super-secret-key"
    algorithm: str = "HS256"

    class Config:
        env_file = '.env'


settings = Settings()