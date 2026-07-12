from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppSettings:
    database_url: str
    host: str
    port: int
    debug: bool
    public_base_url: str
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_phone: str
    scheduler_enabled: bool
    scheduler_poll_seconds: int


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def load_settings() -> AppSettings:
    database_url = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./paint_shop.db"))
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
    debug = os.getenv("APP_DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    public_base_url = os.getenv("APP_BASE_URL", "").rstrip("/")
    twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_from_phone = os.getenv("TWILIO_FROM_PHONE", "")
    scheduler_enabled = os.getenv("APP_ENABLE_SCHEDULER", "false").lower() in {"1", "true", "yes", "on"}
    scheduler_poll_seconds = int(os.getenv("APP_SCHEDULER_POLL_SECONDS", "60"))
    return AppSettings(
        database_url=database_url,
        host=host,
        port=port,
        debug=debug,
        public_base_url=public_base_url,
        twilio_account_sid=twilio_account_sid,
        twilio_auth_token=twilio_auth_token,
        twilio_from_phone=twilio_from_phone,
        scheduler_enabled=scheduler_enabled,
        scheduler_poll_seconds=scheduler_poll_seconds,
    )


SETTINGS = load_settings()
