from pydantic import BaseModel
from common.dto.event.base import BaseEvent, BaseRPCRequest, BaseRPCResponse
from common.enums import IntegrationType

class Integration(BaseModel):
    id: int
    type: IntegrationType
    access_key: str | None
    access_key_secret: str | None
    device_id: str | None
    username: str | None
    password: str | None


class IntegrationUpdate(BaseEvent, Integration):
    pass

class ListIntegration(BaseRPCRequest):
    pass


class ListIntegrationResponse(BaseRPCResponse):
    integrations: list[Integration]
