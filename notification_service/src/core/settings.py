from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    project_name: str = "app"
    database_mongo_url: str = Field(default="mongodb://mongodb:27017")
    kafka_bootstrap_servers: str = Field(default="kafka:9092")

    class Config:
        env_file = ".env"


settings = Settings()
