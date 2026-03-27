import logging
from typing import Generator, Callable
from contextlib import contextmanager

import paho.mqtt.client as mqtt
from fastapi import Depends

from common.dto.topics import AgentTopics
from common.dto.event.base import BaseEvent
from common.mqtt import get_client
from auto_mate_server.config import settings

logger = logging.getLogger(__name__)


class MQTTService:
    def __init__(self, client: mqtt.Client):
        self.client = client

    def prefix_topic(self, topic: str):
        if not topic.startswith(settings.MQTT_TOPIC_PREFIX):
            topic = f"{settings.MQTT_TOPIC_PREFIX}/{topic}"
        return topic

    def publish(self, topic: str, payload: str):
        topic = self.prefix_topic(topic)
        logger.info(f"Publishing to {topic}")
        self.client.publish(topic, payload)
    
    def publish_event(self, event: BaseEvent):
        topic = AgentTopics.resolve_topic(event)
        assert topic,f"No topic to publish {event}"
        self.publish(topic, event.model_dump_json())

    def subscribe(self, topic: str, on_message: Callable[[str, str, str], None]):
        topic = self.prefix_topic(topic)
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, on_message)
        logger.info(f"Subscripted to {topic} - {on_message.__name__}")

    def add_callback(self, topic: str, on_message: Callable[[str, str, str], None]):
        topic = self.prefix_topic(topic)
        self.client.message_callback_add(topic, on_message)

    def loop_forever(self):
        self.client.loop_forever()

    def loop_start(self):
        self.client.loop_start()

@contextmanager
def get_mqtt_service_ctx(client_id: str) -> Generator[MQTTService]:
    with get_client(client_id) as client:
        yield MQTTService(client)
