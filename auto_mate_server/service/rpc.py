import logging

import paho.mqtt.client as mqtt
from fastapi import Depends

from auto_mate_server.mqtt import get_client
from auto_mate_server.config import settings

logger = logging.getLogger(__name__)


class MQTTService:
    def __init__(self, client: mqtt.Client = Depends(get_client)):
        self.client = client

    def publish(self, topic: str, payload: str):
        if not topic.startswith(settings.MQTT_TOPIC_PREFIX):
            topic = f"{settings.MQTT_TOPIC_PREFIX}/{topic}"
        logging.info(f"Publishing to {topic}")
        self.client.publish(topic, payload)
