from common.service.mqtt import MQTTService
from agent.base import BaseAgent


class TapoAgent(BaseAgent):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        super().__init__(name, mqtt_service)
