from agent.base import BaseAgent
from common.dto.event.integration import IntegrationCreate
from common.service.mqtt import MQTTService


class TinyTuyaAgent(BaseAgent):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        super().__init__(name, mqtt_service)

    def on_integration_event(self, topic: str, event: IntegrationCreate):
        self.logger.info(f"{topic} {event}")
