import logging

from fastapi import Depends
from sqlalchemy import select

from common.utils import create_model
from common.mqtt import subscribe, MQTTSubscribeMixin
from common.service.mqtt import MQTTService
from common.dto.topics import TopicRegistry
from common.dto.event.integration import (
    ListIntegrations,
    ListIntegrationsResponse,
    Integration as IntegrationOut,
)
from common.dto.event.device import (
    ListDevices,
    ListDevicesResponse,
    Device as DeviceOut,
)
from auto_mate_server.factory import get_mqtt_service
from auto_mate_server.db.session import get_db_ctx
from auto_mate_server.db.models import Integration, Device

logger = logging.getLogger(__name__)


class MQTTRequestHandler(MQTTSubscribeMixin):
    def __init__(self, mqtt_service: MQTTService = Depends(get_mqtt_service)) -> None:
        self.mqtt = mqtt_service

    @subscribe(TopicRegistry.LIST_INTEGRATIONS)
    def on_list_integrations(self, topic: str, event: ListIntegrations):
        logger.info(f"Received {topic=}")
        with get_db_ctx() as db:
            integrations = db.scalars(
                select(Integration).order_by(Integration.id)
            ).all()

        self.mqtt.publish_response(
            ListIntegrationsResponse(
                request_id=event.request_id,
                context=event.context,
                integrations=[create_model(IntegrationOut, i) for i in integrations],
            ),
            event.response_suffix,
        )

    @subscribe(TopicRegistry.LIST_DEVICES)
    def on_list_devices(self, topic: str, event: ListDevices):
        with get_db_ctx() as db:
            devices = db.scalars(
                select(Device)
                .join(Device.integration)
                .where(Integration.type == event.integration_type)
            )

        self.mqtt.publish_response(
            ListDevicesResponse(
                request_id=event.request_id,
                context=event.context,
                devices=[create_model(DeviceOut, d) for d in devices],
            ),
            event.response_suffix,
        )
