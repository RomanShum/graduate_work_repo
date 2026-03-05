from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str
    redis_host: str
    redis_port: int
    elastic_host: str
    elastic_port: int
    page_size: int = 50
    page_number: int = 1
    elastic_schema: str = 'http'
    film_cache_expire_in_seconds:int = 60 * 5
    app_start_method:str = 'main:app'
    app_host:str = '0.0.0.0'
    app_port:int = 8000

    class Config:
        env_file = '.env'


settings = Settings()
