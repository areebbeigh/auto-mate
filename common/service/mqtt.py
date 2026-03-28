import logging
import json
from typing import Generator, Callable, Any, Type
from contextlib import contextmanager

import paho.mqtt.client as mqtt
from fastapi import Depends

from common.dto.topics import TopicRegistry
from common.dto.event.base import BaseEvent
from common.mqtt import get_client
from auto_mate_server.config import settings

logger = logging.getLogger(__name__)

EventHandler = Callable[[str, BaseEvent], None]

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
        topic = TopicRegistry.resolve_topic(event)
        assert topic, f"No topic to publish {event}"
        self.publish(topic, event.model_dump_json())

    def _subscribe(self, topic: str, on_message: Callable[[str, str, str], None]):
        topic = self.prefix_topic(topic)
        self.client.subscribe(topic)
        self.client.message_callback_add(topic, on_message)
        logger.info(f"Subscribed to {topic} - {on_message.__name__}")

    def _get_wrapped_callback(self, topic: TopicRegistry, callback: Callable[[str, BaseEvent], None], response: bool = False):
        def wrapped(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
            payload = json.loads(message.payload.decode())
            klass = topic.response_schema if response else topic.schema
            if klass:
                payload = klass(**payload)
            callback(message.topic, payload)

        wrapped.__name__ = f"wrapped_{callback.__name__}"
        return wrapped


    def subscribe(self, topic: TopicRegistry, callback: Callable[[str, BaseEvent], None]):
        wrapped = self._get_wrapped_callback(topic, callback)
        self._subscribe(topic.topic, wrapped)
    
    def subscribe_response(self, topic: TopicRegistry, callback: Callable[[str, BaseEvent], None]):
        wrapped = self._get_wrapped_callback(topic, callback, True)
        self._subscribe(topic.response_topic, wrapped)

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
