import json
import os
import time
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEBUG_LOG_PATH = "/Users/vladislavargun/Documents/GitHub/Cursor/Appointment Hub/.cursor/debug.log"


#region agent log
def _debug_log(hypothesis_id: str, message: str, data: dict) -> None:
    payload = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": hypothesis_id,
        "location": "core/config.py",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    try:
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass
#endregion


class DatabaseSettings(BaseModel):
    url: str = Field(..., description="Database DSN in asyncpg format")


class RedisSettings(BaseModel):
    url: str = Field(..., description="Redis URL")
    services_ttl_seconds: int = Field(900, description="TTL for services list cache")
    slots_ttl_seconds: int = Field(180, description="TTL for slots list cache")


class RabbitSettings(BaseModel):
    url: str = Field(..., description="RabbitMQ URL")
    notifications_queue: str = Field("notifications.send", description="Queue for notifications")
    max_retries: int = Field(3, description="Max retry attempts for sending events")


class TelegramSettings(BaseModel):
    bot_token: str | None = Field(None, description="Telegram bot token")
    chat_id: str | None = Field(None, description="Telegram chat id")


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    app_name: str = "Appointment Hub API"
    environment: Literal["local", "dev", "prod"] = "local"
    api_prefix: str = "/api/v1"
    db: DatabaseSettings
    redis: RedisSettings
    rabbit: RabbitSettings
    telegram: TelegramSettings = TelegramSettings(bot_token=None, chat_id=None)
    log_level: str = "INFO"


@lru_cache
def get_settings() -> AppSettings:
    env_presence = {
        "DB__URL": bool(os.getenv("DB__URL")),
        "REDIS__URL": bool(os.getenv("REDIS__URL")),
        "RABBIT__URL": bool(os.getenv("RABBIT__URL")),
    }
    _debug_log("H2", "get_settings_called", {"env_presence_flags": env_presence})
    try:
        settings = AppSettings()  # type: ignore[call-arg]
        _debug_log(
            "H2",
            "app_settings_created",
            {
                "has_db_url": bool(settings.db.url),
                "has_redis_url": bool(settings.redis.url),
                "has_rabbit_url": bool(settings.rabbit.url),
            },
        )
        return settings
    except Exception as exc:  # pragma: no cover - debug path
        _debug_log("H1", "app_settings_error", {"error": type(exc).__name__, "detail": str(exc)})
        raise

