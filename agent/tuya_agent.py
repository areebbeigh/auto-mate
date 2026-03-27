from agent.base import BaseAgent
from common.service.mqtt import MQTTService


class TinyTuyaAgent(BaseAgent):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        super().__init__(name, mqtt_service)
