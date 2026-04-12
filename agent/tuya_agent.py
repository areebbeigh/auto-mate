import os
import json
import io
import time
from contextlib import redirect_stdout

import tinytuya
import tinytuya.scanner
from tinytuya.wizard import wizard

from agent.base import BaseAgent
from agent.config import settings
from agent.transformers import tuya_dict_to_device
from common.enums import IntegrationType
from common.mqtt import subscribe
from common.dto.topics import TopicRegistry
from common.dto.event.integration import (
    IntegrationUpdate,
    ListIntegrations,
    ListIntegrationsResponse,
    Integration,
)
from common.dto.event.device import (
    ListDevices,
    ListDevicesResponse,
    CreateOrUpdateDevicesRequest,
    DeviceUpdate
)


class TuyaAgent(BaseAgent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.integrations = {}

    def integration_type(self) -> IntegrationType:
        return IntegrationType.TINYTUYA

    @subscribe(TopicRegistry.INTEGRATION_UPDATE)
    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        if event.type != IntegrationType.TINYTUYA:
            return

        self.logger.info(f"Integration {event.id} updated")
        self._init_integration(event)
    
    @subscribe(TopicRegistry.DEVICE_UPDATE)
    def on_device_update(self, topic: str, event: DeviceUpdate):
        if event.integration_id not in self.integrations:
            return
        
        self.add_device(event)

    @subscribe(TopicRegistry.LIST_INTEGRATIONS, is_response_handler=True)
    def on_integration_list(self, topic: str, event: ListIntegrationsResponse):
        self.logger.info(f"Received integration list")
        for integration in event.integrations:
            self.integrations[integration.id] = integration
            try:
                self._init_integration(integration)
                time.sleep(3)
            except Exception as e:
                self.logger.error(f"Failed to init integration {integration.id}: {e}")
        self.logger.info(f"Processed {len(event.integrations)} integrations")

    @subscribe(TopicRegistry.LIST_DEVICES, is_response_handler=True)
    def on_list_devices(self, topic: str, event: ListDevicesResponse):
        self.logger.info(f"Found {len(event.devices)} devices.")
        for device in event.devices:
            try:
                self.add_device(device)
            except Exception:
                self.logger.exception(f"Could not register device {device}")

    def on_start(self):
        self.publish_request(ListDevices(integration_type=IntegrationType.TINYTUYA))
        self.publish_request(ListIntegrations())

    def _init_integration(self, integration: Integration):
        if integration.type != IntegrationType.TINYTUYA:
            return

        self.logger.info(f"Initializing integration {integration.id}")

        # TODO: Ideally, I should just call the tuya APIs instead of using a CLI wizard. Ideally.
        pwd = os.getcwd()
        tuyadir = settings.CONFIG_DIR / f"tuya_{integration.id}"
        try:
            os.makedirs(tuyadir, exist_ok=True)
            os.chdir(tuyadir)
            credentials_file = tuyadir / "creds.json"
            with open(credentials_file, "w") as f:
                json.dump(
                    {
                        "apiKey": integration.access_key,
                        "apiSecret": integration.access_key_secret,
                        "apiRegion": "in",
                        "apiDeviceID": integration.device_id or "scan",
                    },
                    f,
                )
            buf = io.StringIO()
            with redirect_stdout(buf):
                wizard(assume_yes=True, credentials={"file": credentials_file})
        except Exception:
            self.logger.exception(f"Failed to run wizard for {integration.id}")
            return
        finally:
            os.chdir(pwd)

        # Save devices from snapshot.json
        with open(tuyadir / "snapshot.json") as f:
            snapshot = json.load(f)
            devices = snapshot.get("devices", [])

            if not devices:
                return

            device_objs = []
            for d in devices:
                try:
                    device_objs.append(
                        tuya_dict_to_device(
                            d,
                            integration_id=integration.id,
                            user_id=integration.user_id,
                        )
                    )
                except Exception:
                    self.logger.exception(f"Could not parse {d} into Device")
                    continue

            event = CreateOrUpdateDevicesRequest(devices=device_objs)
            self.publish_request(event)
