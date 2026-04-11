from auto_mate_server.db.repo.base import BaseRepo
from auto_mate_server.db.models import Device


class DeviceRepo(BaseRepo[Device]):
    @classmethod
    def get_model(cls) -> Device:
        return Device
