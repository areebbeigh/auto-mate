from pydantic import BaseModel
from datetime import datetime


class BaseEvent(BaseModel):
    created_at: datetime
    published_at: datetime = datetime.now()
