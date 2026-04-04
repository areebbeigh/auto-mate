import logging
from typing import Generator
from contextlib import contextmanager

import paho.mqtt.client as mqtt

from auto_mate_server.config import settings
from common.dto.topics import TopicRegistry

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


def subscribe(topic: TopicRegistry, is_response_handler: bool = False):
    from common.service.mqtt import EventHandler

    def decorator(callback: EventHandler):
        callback._mqtt = {"topic": topic, "is_response_handler": is_response_handler}
        return callback

    return decorator


class MQTTSubscribeMixin:
    def _subscribe_topics(self):
        meta = {}
        for name, func in self.__class__.__dict__.items():
            if hasattr(func, "_mqtt"):
                meta[name] = func._mqtt

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            subscribe_metadata = (
                attr._mqtt if hasattr(attr, "_mqtt") else meta.get(attr_name)
            )

            if subscribe_metadata:
                topic = subscribe_metadata["topic"]
                is_response_handler = subscribe_metadata["is_response_handler"]
                if is_response_handler:
                    self.mqtt.subscribe_response(topic, attr, self.response_suffix)
                else:
                    self.mqtt.subscribe(topic, attr)
