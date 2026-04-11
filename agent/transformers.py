from common.utils import common_kwargs
from common.dto.event.device import Device


def tuya_dict_to_device(device: dict, **kwargs):
    return Device(
        id=None,
        device_id=device["id"],
        last_known_ip=device["ip"],
        controllable=bool(device["key"]),
        payload=device,
        **common_kwargs(Device, device, ["id"]),
        **kwargs,
    )
