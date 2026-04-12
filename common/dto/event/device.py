from pydantic import BaseModel
from common.dto.event.base import BaseEvent, BaseRPCRequest, BaseRPCResponse
from common.enums import IntegrationType


class Device(BaseModel):
    id: int | None
    device_id: str
    name: str
    last_known_ip: str
    payload: dict
    controllable: bool
    integration_id: int
    user_id: int | None = None
    payload: dict


class ListDevices(BaseRPCRequest):
    integration_type: IntegrationType


class ListDevicesResponse(BaseRPCResponse):
    devices: list[Device] = []


class CreateOrUpdateDevicesRequest(BaseRPCRequest):
    devices: list[Device] = []


class DeviceUpdate(BaseEvent, Device):
    pass
