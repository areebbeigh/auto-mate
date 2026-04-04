from common.dto.event.integration import IntegrationUpdate
from common.service.mqtt import MQTTService
from agent.base import BaseAgent


class TapoAgent(BaseAgent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        self.logger.info(f"{topic} {event}")
