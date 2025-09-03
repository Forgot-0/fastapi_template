from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BaseModelEvent(BaseModel):
    event_id: UUID
    created_at: datetime
