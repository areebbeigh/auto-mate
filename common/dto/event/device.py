from pydantic import BaseModel
from common.dto.event.base import BaseEvent, BaseRPCRequest, BaseRPCResponse
from common.enums import IntegrationType


class Device(BaseModel):
    id: int
    device_id: str
    name: str
    last_known_ip: str
    payload: dict
    controllable: bool
    integration_id: int
    user_id: int
    payload: dict


class ListDevices(BaseRPCRequest):
    integration_type: IntegrationType


class ListDevicesResponse(BaseRPCResponse):
    devices: list[Device] = []
