"""Common config shared between services"""

import os
import logging.config

class Settings:
    APP_ENV = os.getenv("APP_ENV", "dev")
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

logging.config.dictConfig(Settings.LOGGING)
