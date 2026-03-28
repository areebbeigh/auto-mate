"""Agents always run on the edge layer (LAN) and operate between IoT devices and control-pane (FastAPI server)"""
import abc
import logging

from common.service.mqtt import MQTTService, EventHandler
from common.dto.topics import TopicRegistry
from common.dto.event.integration import IntegrationUpdate, ListIntegrationResponse


def subscribe(topic: TopicRegistry, is_response_handler: bool = False):
    def decorator(callback: EventHandler):
        callback._mqtt = {
            "topic": topic,
            "is_response_handler": is_response_handler
        }
        return callback
    return decorator

class BaseAgent(abc.ABC):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        self.name = name
        self.mqtt = mqtt_service
        self.logger = logging.getLogger(self.__class__.__name__)

    def _subscribe_topics(self):
        meta = {}
        for cls in self.__class__.__mro__:
            for name, func in cls.__dict__.items():
                if hasattr(func, "_mqtt"):
                    meta[name] = func._mqtt

        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            subscribe_metadata = attr._mqtt if hasattr(attr, "_mqtt") else meta.get(attr_name)

            if subscribe_metadata:
                topic = subscribe_metadata["topic"]
                is_response_handler = subscribe_metadata["is_response_handler"]
                if is_response_handler:
                    self.mqtt.subscribe_response(topic, attr)
                else:
                    self.mqtt.subscribe(topic, attr)

    @subscribe(TopicRegistry.INTEGRATION_UPDATE)
    @abc.abstractmethod
    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        pass
    
    @subscribe(TopicRegistry.LIST_INTEGRATIONS, is_response_handler=True)
    def on_integration_list_response(self, topic: str, event: ListIntegrationResponse):
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
