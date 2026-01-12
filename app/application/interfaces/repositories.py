from collections.abc import Sequence
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.domain.appointments.entities import Appointment, AppointmentStatus
from app.domain.schedules.entities import ScheduleSlot
from app.domain.services.entities import Service
from app.domain.users.entities import User, UserRole


class UserRepository(Protocol):
    async def create(self, email: str, full_name: str, role: UserRole) -> User: ...
    async def get(self, user_id: UUID) -> User | None: ...


class ServiceRepository(Protocol):
    async def list(self, provider_id: UUID | None = None) -> Sequence[Service]: ...
    async def create(self, provider_id: UUID, title: str, duration_min: int, price: float) -> Service: ...


class ScheduleRepository(Protocol):
    async def create_slot(self, provider_id: UUID, starts_at: datetime, ends_at: datetime) -> ScheduleSlot: ...
    async def list_available(self, provider_id: UUID | None, date_filter: date | None) -> Sequence[ScheduleSlot]: ...
    async def mark_slot_availability(self, slot_id: UUID, is_available: bool) -> ScheduleSlot | None: ...
    async def lock_slot(self, slot_id: UUID) -> ScheduleSlot | None: ...


class AppointmentRepository(Protocol):
    async def create(
        self,
        client_id: UUID,
        provider_id: UUID,
        service_id: UUID,
        slot_id: UUID,
        status: AppointmentStatus = AppointmentStatus.created,
    ) -> Appointment: ...

    async def get(self, appointment_id: UUID) -> Appointment | None: ...
    async def update_status(self, appointment_id: UUID, status: AppointmentStatus) -> Appointment | None: ...

