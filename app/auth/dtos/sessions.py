from datetime import datetime

from pydantic import BaseModel


class SessionDTO(BaseModel):
    id: int
    user_id: int
    device_info: str
    user_agent: str
    last_activity: datetime
    is_active: bool
