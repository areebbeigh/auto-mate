"""Agents always run on the edge layer (LAN) and operate between IoT devices and control-pane (FastAPI server)"""

import abc
import logging

from common.enums import IntegrationType
from common.mqtt import MQTTSubscribeMixin
from common.service.mqtt import MQTTService
from common.dto.event.base import BaseRPCRequest
from common.dto.event.integration import IntegrationUpdate
from common.dto.event.device import Device
from agent.service.device_registry import DeviceRegistry, RegistryDevice


class BaseAgent(abc.ABC, MQTTSubscribeMixin):
    def __init__(
        self,
        name: str,
        mqtt_service: MQTTService,
        device_registry: DeviceRegistry,
    ) -> None:
        self.name = name
        self.mqtt = mqtt_service
        self.logger = logging.getLogger(self.__class__.__name__)
        self.device_registry = device_registry
        self.response_suffix = f"{self.__class__.__name__}"

    @abc.abstractmethod
    def on_integration_event(self, topic: str, event: IntegrationUpdate):
        pass

    @abc.abstractmethod
    def integration_type(self) -> IntegrationType:
        pass

    def on_start(self):
        pass

    def publish_request(self, request: BaseRPCRequest):
        if not request.response_suffix:
            request.response_suffix = self.response_suffix
        self.mqtt.publish_event(request)

    def add_device(self, device: Device):
        self.device_registry.register_device(
            RegistryDevice(
                **device.model_dump(),
                integration_type=self.integration_type(),
            )
        )
        self.logger.info(f"Registered device {device.id}")

    def start(self):
        self._subscribe_topics()
        self.on_start()

    def loop_forever(self):
        self.mqtt.loop_forever()

    def loop_start(self):
        self.mqtt.loop_start()
