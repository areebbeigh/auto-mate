from common.dto.event.device import Device
from common.enums import IntegrationType


class RegistryDevice(Device):
    integration_type: IntegrationType
    integration_id: int


class DeviceRegistry:
    def __init__(self) -> None:
        self.devices = {}

    def register_device(self, device: RegistryDevice) -> None:
        self.devices.setdefault(device.integration_type, {}).setdefault(
            device.integration_id, {}
        )[device.id] = device

    def unregister_devices(self, device_ids: list[int]) -> int:
        count = 0
        for by_integration_id in self.devices.values():
            for by_device_id in by_integration_id.values():
                for device_id in device_ids:
                    if device_id in by_device_id:
                        del by_device_id[device_id]
                        count += 1
        return count

    def get_devices(
        self,
        integration_type: IntegrationType | None = None,
        integration_id: int | None = None,
        device_ids: list[int] | None = None,
    ):
        if device_ids:
            return [
                by_device_id[device_id]
                for by_integration_id in self.devices.values()
                for by_device_id in by_integration_id.values()
                for device_id in device_ids
                if device_id in by_device_id
            ]

        if integration_id:
            return list(
                self.devices.get(integration_type, {}).get(integration_id, []).values()
            )
        if integration_type:
            return [
                device
                for by_device_id in self.devices.get(integration_type, {}).values()
                for device in by_device_id.values()
            ]
        return [
            device
            for by_integration_id in self.devices.values()
            for by_device_id in by_integration_id.values()
            for device in by_device_id.values()
        ]
