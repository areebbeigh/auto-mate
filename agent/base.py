"""Agents always run on the edge layer (LAN) and operate between IoT devices and control-pane (FastAPI server)"""
import abc
import logging
import json
from typing import Callable, Any

import paho.mqtt.client as mqtt

from common.service.mqtt import MQTTService
from common.dto.topics import AgentTopics
from common.dto.event.integration import IntegrationCreate, BaseEvent

class BaseAgent(abc.ABC):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        self.name = name
        self.mqtt = mqtt_service
        self.logger = logging.getLogger(self.__class__.__name__)

    def _subscribe_topics(self):
        self._subscribe(AgentTopics.INTEGRATION_CREATE.topic, self.on_integration_event)
    
    def _subscribe(self, topic: str, callback: Callable[[str, BaseEvent], None]):
        def wrapped(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage):
            klass = AgentTopics.resolve_schema(topic)
            payload = json.loads(message.payload.decode())
            if klass:
                payload = klass(**payload)
            callback(message.topic, payload)

        wrapped.__name__ = f"wrapped_{callback.__name__}"

        self.mqtt.subscribe(topic, wrapped)

    @abc.abstractmethod
    def on_integration_event(self, topic: str, event: IntegrationCreate):
        pass

    def start(self):
        self._subscribe_topics()
    
    def loop_forever(self):
        self.mqtt.loop_forever()

    def loop_start(self):
        self.mqtt.loop_start()
