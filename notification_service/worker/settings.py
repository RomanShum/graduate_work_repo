from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    allowed_topics: str
    consumer_server: str
    consumer_group: str
    enable_auto_commit: bool = False
    auth_url: str = ""
    smtp_host: str
    smtp_port: int
    username: str
    password: str
    database_mongo_url: str
    db_name: str
    db_table: str

    @property
    def topic_list(self) -> List[str]:
        return self.allowed_topics.split(',')

    class Config:
        env_file = ".env"
