import os
import json

import tinytuya
from tinytuya.wizard import wizard
import tinytuya.scanner

from agent.base import BaseAgent
from agent.config import settings
from common.enums import IntegrationType
from common.dto.event.integration import (
    IntegrationUpdate,
    ListIntegrations,
    ListIntegrationsResponse,
)
from common.dto.event.device import ListDevices
from common.service.mqtt import MQTTService


class TuyaAgent(BaseAgent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        if event.type != IntegrationType.TINYTUYA:
            return

        # TODO: Ideally, I should just call the tuya APIs instead of using a CLI wizard. Ideally.
        pwd = os.getcwd()
        tuyadir = settings.CONFIG_DIR / f"tuya_{event.id}"
        try:
            os.makedirs(tuyadir)
            os.chdir(tuyadir)
            credentials_file = tuyadir / "creds.json"
            with open(credentials_file, "w") as f:
                json.dump(
                    {
                        "apiKey": event.access_key,
                        "apiSecret": event.access_key_secret,
                        "apiRegion": "in",
                        "apiDeviceID": event.device_id or "scan",
                    },
                    f,
                )
            wizard(assume_yes=True, credentials={"file": credentials_file})
        except Exception:
            self.logger.exception(f"Failed to run wizard for {event.id}")
            return
        finally:
            os.chdir(pwd)

        # Save devices from snapshot.json
        with open(tuyadir / "snapshot.json") as f:
            snapshot = json.load(f)
            devices = snapshot.get("devices", [])

    def on_integration_list_response(self, topic: str, event: ListIntegrationsResponse):
        self.logger.info(f"Integration list: {event=}")
        # TODO: Run integration
        # TODO: Update device list if required

    def on_start(self):
        self.publish_request(ListDevices(integration_type=IntegrationType.TINYTUYA))
        self.publish_request(ListIntegrations())
