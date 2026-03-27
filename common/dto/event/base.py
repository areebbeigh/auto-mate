from pydantic import BaseModel
from datetime import datetime


class BaseEvent(BaseModel):
    published_at: datetime = datetime.now()


class BaseRPCRequest(BaseEvent):
    request_id: str
    reply_to: str | None

class BaseRPCResponse(BaseEvent):
    request_id: str
