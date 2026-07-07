from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionDTO(BaseModel):
    id: int
    user_id: int
    device_info: str
    user_agent: str
    last_activity: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
