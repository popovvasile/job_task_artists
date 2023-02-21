import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Config(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080
    WRITER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/immomio"
    READER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/immomio"
    JWT_SECRET_KEY: str = "fastapi"
    JWT_ALGORITHM: str = "HS256"
    SENTRY_SDN: str = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    FREQUENCY: int = 5
    SPOTIFY_CLIENT_ID: str = os.getenv("CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("CLIENT_SECRET")


class DevelopmentConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/immomio"
    READER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/immomio"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


class LocalConfig(Config):
    WRITER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/immomio"
    READER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/immomio"


class ProductionConfig(Config):
    DEBUG: str = False
    WRITER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/prod"
    READER_DB_URL: str = f"postgresql+asyncpg://klaus:password@localhost:6500/prod"


def get_config():
    env = os.getenv("ENV", "local")
    config_type = {
        "dev": DevelopmentConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()


