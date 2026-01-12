from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ScheduleSlot(BaseModel):
    id: UUID
    provider_id: UUID
    starts_at: datetime
    ends_at: datetime
    is_available: bool


