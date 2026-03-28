import logging

from fastapi import Depends

from common.service.mqtt import MQTTService
from auto_mate_server.factory import get_mqtt_service
from common.dto.topics import TopicRegistry
from common.dto.event.integration import ListIntegration, ListIntegrationResponse

logger = logging.getLogger(__name__)


class MQTTRequestHandler:
    def __init__(self, mqtt_service: MQTTService = Depends(get_mqtt_service)) -> None:
        self.mqtt = mqtt_service

    def _subscribe_topics(self):
        self.mqtt.subscribe(TopicRegistry.LIST_INTEGRATIONS, self.on_list_integrations)

    def on_list_integrations(self, topic: str, event: ListIntegration):
        logger.info(f"Received {topic=} {event=}")
        self.mqtt.publish_event(ListIntegrationResponse(request_id=event.request_id, context=event.context, integrations=[]))
