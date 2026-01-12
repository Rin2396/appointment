from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SlotCreate(BaseModel):
    provider_id: UUID
    starts_at: datetime
    ends_at: datetime


class SlotResponse(BaseModel):
    id: UUID
    provider_id: UUID
    starts_at: datetime
    ends_at: datetime
    is_available: bool

