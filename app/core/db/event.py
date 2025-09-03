from uuid import UUID

from sqlalchemy import UUID as SAUUID, Boolean
from sqlalchemy.orm import Mapped,  mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from app.core.db.base_model import BaseModel, DateMixin



class EventLog(BaseModel, DateMixin):
    __tablename__ = "events_log"

    event_id: Mapped[UUID] = mapped_column(SAUUID, primary_key=True)
    meta_data: Mapped[dict] = mapped_column(JSONB, default={})

