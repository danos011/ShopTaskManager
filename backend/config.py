from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    celery_broker_dsn: str
    celery_backend_dsn: str
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: int
    redis_max_connections: int
    redis_socket_timeout: int
    redis_decode_responses: bool

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"
        extra = "ignore"


CONFIG = Settings()
