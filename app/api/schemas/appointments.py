from uuid import UUID

from pydantic import BaseModel

from app.domain.appointments.entities import AppointmentStatus


class AppointmentCreate(BaseModel):
    client_id: UUID
    provider_id: UUID
    service_id: UUID
    slot_id: UUID


class AppointmentResponse(BaseModel):
    id: UUID
    client_id: UUID
    provider_id: UUID
    service_id: UUID
    slot_id: UUID
    status: AppointmentStatus

