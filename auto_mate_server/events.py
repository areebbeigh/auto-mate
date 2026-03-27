from typing import Callable

from fastapi import Depends

from common.service.mqtt import MQTTService
from auto_mate_server.db.models import Base, Integration
from common.dto.event.integration import IntegrationUpdate
from auto_mate_server.factory import get_mqtt_service

EVENT_CLASS_MAP = {
    Integration: IntegrationUpdate
}

UpdatePublisher = Callable[[Base], None]


def get_update_publisher(mqtt_service: MQTTService = Depends(get_mqtt_service)) -> UpdatePublisher:
    def publish(obj: Base):
        klass = EVENT_CLASS_MAP[obj.__class__]
        event = klass(**obj.__dict__)
        mqtt_service.publish_event(event)
    return publish
