"""Application configuration."""

import os
import logging.config


class Settings:
    """Simple environment-backed settings."""

    APP_NAME = os.getenv("APP_NAME", "auto-mate-api")
    APP_ENV = os.getenv("APP_ENV", "dev")
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", "8000"))
    APP_RELOAD = os.getenv("APP_RELOAD", "true").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./auto_mate.db")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-me-please-use-at-least-32-chars")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]
    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_USERNAME = os.getenv("MQTT_USERNAME", "admin")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "admin")
    MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "auto-mate")
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(module)s:%(funcName)s:%(levelname)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }

settings = Settings()
logging.config.dictConfig(settings.LOGGING)
