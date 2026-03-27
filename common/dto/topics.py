from enum import Enum

from common.dto.event.base import BaseEvent
from common.dto.event.integration import IntegrationUpdate, ListIntegration, ListIntegrationResponse


class BaseTopicRegistry(Enum):
    @property
    def topic(self):
        return self.value[0]

    @property
    def schema(self):
        return self.value[1]
    
    @property
    def response_schema(self):
        return self.value[2]
    
    @property
    def response_topic(self):
        if not self.response_schema:
            return
        return self.topic.replace("rpc/query", "rpc/response")

    @classmethod
    def resolve_schema(cls, topic: str):
        for t in cls:
            if t.schema and t.topic == topic:
                return t.schema
            
    @classmethod
    def resolve_topic(cls, event: BaseEvent):
        for t in cls:
            if t.schema == event.__class__:
                return t.topic


class TopicRegistry(BaseTopicRegistry):
    # Agent topics
    INTEGRATION_UPDATE = ("integration/update", IntegrationUpdate, None)
    INTEGRATION_DELETE = ("integration/delete", None, None)
    DEVICE_UPDATE = ("device/update", None, None)
    DEVICE_DELETE = ("device/delete", None, None)
    DEVICE_STATE_CHANGE = ("device/state/change", None, None)

    # FastAPI topics
    LIST_INTEGRATIONS = ("rpc/query/integration/list", ListIntegration, ListIntegrationResponse)
