from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/streampy.db"

    # Security
    encryption_key: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 15
    jwt_refresh_expire_days: int = 30

    # App
    environment: str = "production"
    app_name: str = "StreamPy"
    app_version: str = "1.0.0"

    # CORS - allowed origins (local network + VPN)
    cors_origins: list[str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1",
        "http://192.168.0.0/16",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
