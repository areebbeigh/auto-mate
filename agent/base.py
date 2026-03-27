"""Agents always run on the edge layer (LAN) and operate between IoT devices and control-pane (FastAPI server)"""
import abc
import logging
import json
from typing import Callable, Any

from common.service.mqtt import MQTTService
from common.dto.topics import TopicRegistry
from common.dto.event.integration import IntegrationUpdate, BaseEvent

class BaseAgent(abc.ABC):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        self.name = name
        self.mqtt = mqtt_service
        self.logger = logging.getLogger(self.__class__.__name__)

    def _subscribe_topics(self):
        self.mqtt.subscribe(TopicRegistry.INTEGRATION_UPDATE, self.on_integration_event)
    
    @abc.abstractmethod
    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        pass

    def on_start(self):
        pass

    def start(self):
        self._subscribe_topics()
        self.on_start()
    
    def loop_forever(self):
        self.mqtt.loop_forever()

    def loop_start(self):
        self.mqtt.loop_start()
