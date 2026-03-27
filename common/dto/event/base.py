from pydantic import BaseModel
from datetime import datetime


class BaseEvent(BaseModel):
    created_at: datetime
