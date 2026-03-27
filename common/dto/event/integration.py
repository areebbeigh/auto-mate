from common.dto.event.base import BaseEvent
from common.enums import IntegrationType


class IntegrationCreate(BaseEvent):
    id: int
    type: IntegrationType
    access_key: str | None
    access_key_secret: str | None
    device_id: str | None
    username: str | None
    password: str | None
