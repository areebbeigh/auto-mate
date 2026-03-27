import os
import json

import tinytuya
from tinytuya.wizard import wizard
import tinytuya.scanner

from agent.base import BaseAgent
from agent.config import settings
from common.enums import IntegrationType
from common.dto.topics import TopicRegistry
from common.dto.event.integration import IntegrationUpdate, ListIntegration
from common.service.mqtt import MQTTService


class TinyTuyaAgent(BaseAgent):
    def __init__(self, name: str, mqtt_service: MQTTService) -> None:
        super().__init__(name, mqtt_service)

    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        if event.type != IntegrationType.TINYTUYA:
            return
        
        # TODO: Ideally, I should just call the tuya APIs instead of using a CLI wizard. Ideally.
        pwd = os.getcwd()
        try:
            tuyadir = settings.CONFIG_DIR / f"tuya_{event.id}"
            os.makedirs(tuyadir)
            os.chdir(tuyadir)
            credentials_file = tuyadir / "creds.json"
            with open(credentials_file, "w") as f:
                json.dump({
                    "apiKey": event.access_key,
                    "apiSecret": event.access_key_secret,
                    "apiRegion": "in",
                    "apiDeviceID": event.device_id or "scan",
                }, f)
            wizard(assume_yes=True, credentials={"file": credentials_file})
        finally:
            os.chdir(pwd)

    def on_start(self):
        self.mqtt.publish_event(ListIntegration(request_id="", reply_to=""))
