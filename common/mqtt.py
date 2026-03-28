import logging
from typing import Generator
from contextlib import contextmanager

import paho.mqtt.client as mqtt

from auto_mate_server.config import settings

logger = logging.getLogger(__name__)

@contextmanager
def get_client(client_id: str) -> Generator[mqtt.Client]:
    client = mqtt.Client(client_id=client_id)
    client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    client.connect(settings.MQTT_HOST, settings.MQTT_PORT)

    def on_connect(client, userdata, flags, rc):
        logger.info(f"Connected with result code {rc}")

    client.on_connect = on_connect
    client.loop_start()

    try:
        yield client
    finally:
        logger.info(f"Disconnecting mqtt client")
        client.disconnect()
