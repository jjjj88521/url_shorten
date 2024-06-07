import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    SNOWFLAKE_SINCE_TIME: str
    API_KEY: str
    SSL_PEM_PATH: str

    class Config:
        env_file = f".env.{os.getenv('FASTAPI_ENV', 'dev')}"


settings = Settings()
