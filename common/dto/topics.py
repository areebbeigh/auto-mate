from enum import Enum

from common.dto.event.integration import IntegrationCreate


class Base(Enum):
    @property
    def topic(self):
        return self.value[0]

    @property
    def schema(self):
        return self.value[1]

    @classmethod
    def resolve_schema(cls, topic: str):
        for t in cls:
            if t.schema and t.topic == topic:
                return t.schema


class AgentTopics(Base):
    """Agents listen to these topics"""

    INTEGRATION_CREATE = ("integration/create", IntegrationCreate)
    INTEGRATION_UPDATE = ("integration/update", None)
    INTEGRATION_DELETE = ("integration/delete", None)
    DEVICE_CREATE = ("device/create", None)
    DEVICE_UPDATE = ("device/update", None)
    DEVICE_DELETE = ("device/delete", None)
    DEVICE_STATE_CHANGE = ("device/state/change", None)
