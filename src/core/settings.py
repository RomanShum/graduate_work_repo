from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str
    redis_host: str
    redis_port: int
    app_start_method: str = 'main:app'
    app_host: str = '0.0.0.0'
    app_port: int = 8000
    postgres_user: str
    postgres_password: str
    postgres_db: str
    sql_host: str
    sql_port: str
    notification_url: str
    ugc_url: str
    DEBUG: bool = False

    SECRET_KEY: str = "your-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 7 дней

    DATABASE_URL: str | None = None

    def model_post_init(self, __context):
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.sql_host}:{self.sql_port}/{self.postgres_db}"
            )

    class Config:
        env_file = '.env'


settings = Settings()
