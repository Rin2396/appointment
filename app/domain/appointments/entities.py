from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class AppointmentStatus(str, Enum):
    created = "created"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Appointment(BaseModel):
    id: UUID
    client_id: UUID
    provider_id: UUID
    service_id: UUID
    slot_id: UUID
    status: AppointmentStatus
    created_at: datetime


