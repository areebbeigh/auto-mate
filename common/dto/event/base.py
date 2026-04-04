from uuid import uuid4
from datetime import datetime

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    published_at: datetime = datetime.now()


class BaseRPCRequest(BaseEvent):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    response_suffix: str = ""
    context: dict = {}

class BaseRPCResponse(BaseEvent):
    request_id: str
    context: dict = {}
