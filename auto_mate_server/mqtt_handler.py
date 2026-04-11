import logging
from typing import cast

from fastapi import Depends
from sqlalchemy import select

from common.utils import create_model, copy_attrs
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
    CreateOrUpdateDevicesRequest,
)
from auto_mate_server.factory import get_mqtt_service
from auto_mate_server.db.session import get_db_ctx
from auto_mate_server.db.models import Integration, Device
from auto_mate_server.db.repo import get_repos
from auto_mate_server.db.repo.device import DeviceRepo

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
        with get_repos(DeviceRepo) as (_, repo):
            repo = cast(DeviceRepo, repo)
            devices = repo.filter(
                Integration.type == event.integration_type,
                joins=[Device.integration],
            )

            self.mqtt.publish_response(
                ListDevicesResponse(
                    request_id=event.request_id,
                    context=event.context,
                    devices=[create_model(DeviceOut, d) for d in devices],
                ),
                event.response_suffix,
            )

    @subscribe(TopicRegistry.CREATE_OR_UPDATE_DEVICE)
    def on_create_or_update_devices(
        self, topic: str, event: CreateOrUpdateDevicesRequest
    ):
        with get_repos(DeviceRepo) as (session, device_repo):
            device_repo = cast(DeviceRepo, device_repo)

            with session.begin():
                update_count, insert_count = 0, 0
                for device in event.devices:
                    existing_device = device_repo.filter(
                        (Device.id == device.id)
                        | (Device.device_id == device.device_id)
                        if device.id
                        else Device.device_id == device.device_id
                    ).first()
                    if not existing_device:
                        try:
                            updated_device = create_model(Device, device)
                            device_repo.insert(updated_device)
                            insert_count += 1
                        except Exception:
                            logger.exception(f"Error while creating device")
                    else:
                        try:
                            copy_attrs(device, existing_device, ["id"])
                            updated_device = existing_device
                            update_count += 1
                        except Exception:
                            logger.exception(f"Error while updating device")

            logger.info(f"{update_count=}, {insert_count=}")
