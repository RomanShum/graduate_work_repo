from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    sql_host: str
    sql_port: str

    class Config:
        env_file = '.env'
