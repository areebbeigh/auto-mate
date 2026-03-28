from enum import Enum

from common.dto.event.base import BaseEvent
from common.dto.event.integration import IntegrationUpdate, ListIntegration, ListIntegrationResponse

RPC_QUERY_PREFIX = "rpc/query"
RPC_RESPONSE_PREFIX = "rpc/response"

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
        return self.topic.replace(RPC_QUERY_PREFIX, RPC_RESPONSE_PREFIX)

    @classmethod
    def resolve_schema(cls, topic: str):
        for t in cls:
            if t.topic == topic:
                return t.schema
            if t.response_topic == topic:
                return t.response_schema
            
    @classmethod
    def resolve_topic(cls, event: BaseEvent):
        for t in cls:
            if t.schema == event.__class__:
                return t.topic
            if t.response_schema == event.__class__:
                return t.response_topic


class TopicRegistry(BaseTopicRegistry):
    # Agent topics
    INTEGRATION_UPDATE = ("integration/update", IntegrationUpdate, None)
    INTEGRATION_DELETE = ("integration/delete", None, None)
    DEVICE_UPDATE = ("device/update", None, None)
    DEVICE_DELETE = ("device/delete", None, None)
    DEVICE_STATE_CHANGE = ("device/state/change", None, None)

    # FastAPI topics
    LIST_INTEGRATIONS = (f"{RPC_QUERY_PREFIX}/integration/list", ListIntegration, ListIntegrationResponse)
