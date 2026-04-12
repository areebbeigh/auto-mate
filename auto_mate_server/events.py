from typing import Callable

from fastapi import Depends

from common.service.mqtt import MQTTService
from auto_mate_server.db.models import Base, Integration, Device
from common.dto.event.integration import IntegrationUpdate
from common.dto.event.device import DeviceUpdate
from common.utils import create_model
from auto_mate_server.factory import get_mqtt_service

EVENT_CLASS_MAP = {
    Integration: IntegrationUpdate,
    Device: DeviceUpdate,
}

UpdatePublisher = Callable[[Base], None]


def get_update_publisher(
    mqtt_service: MQTTService = Depends(get_mqtt_service),
) -> UpdatePublisher:
    def publish(obj: Base):
        klass = EVENT_CLASS_MAP[obj.__class__]
        event = create_model(klass, obj)
        if event:
            mqtt_service.publish_event(event)

    return publish
