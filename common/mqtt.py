import logging
from typing import Generator
from contextlib import contextmanager

import paho.mqtt.client as mqtt

from auto_mate_server.config import settings

logger = logging.getLogger(__name__)

@contextmanager
def get_client() -> Generator[mqtt.Client]:
    client = mqtt.Client()
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.connect(settings.MQTT_HOST, settings.MQTT_PORT)

    def on_connect(client, userdata, flags, rc):
        logger.info(f"Connected with result code {rc}")

    def on_message(client, userdata, msg):
        logger.info(f"Received message on {msg.topic}: {msg.payload.decode()}")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        yield client
    finally:
        logger.info(f"Disconnecting mqtt client")
        client.disconnect()
