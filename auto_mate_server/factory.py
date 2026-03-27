from fastapi import Depends

from common.service.mqtt import MQTTService
from common.mqtt import get_client

def get_mqtt_service(client_id: str = "fastapi"):
    with get_client(client_id) as mqtt:
        yield MQTTService(mqtt)
