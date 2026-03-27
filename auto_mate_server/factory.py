from fastapi import Depends

from common.service.mqtt import MQTTService
from common.mqtt import get_client

def get_mqtt_service():
    with get_client("fastapi") as mqtt:
        yield MQTTService(mqtt)
