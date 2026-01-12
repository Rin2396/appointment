from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.application.appointments.service import AppointmentService
from app.domain.appointments.entities import Appointment, AppointmentStatus
from app.domain.schedules.entities import ScheduleSlot
from tests.fakes import DummyPublisher, InMemoryCache


class StubSession:
    def begin(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    def in_transaction(self):
        return False


@pytest.mark.asyncio
async def test_create_and_cancel_appointment():
    session = StubSession()
    cache = InMemoryCache()
    publisher = DummyPublisher()

    schedule_repo = Mock()
    appointment_repo = Mock()

    slot_id = uuid4()
    schedule_repo.lock_slot = AsyncMock(
        return_value=ScheduleSlot(
            id=slot_id,
            provider_id=uuid4(),
            starts_at=datetime.now(UTC),
            ends_at=datetime.now(UTC),
            is_available=True,
        )
    )
    schedule_repo.mark_slot_availability = AsyncMock()
    appointment_repo.create = AsyncMock(
        return_value=Appointment(
            id=uuid4(),
            client_id=uuid4(),
            provider_id=uuid4(),
            service_id=uuid4(),
            slot_id=slot_id,
            status=AppointmentStatus.created,
            created_at=datetime.now(UTC),
        )
    )
    appointment_repo.get = AsyncMock(
        return_value=Appointment(
            id=uuid4(),
            client_id=uuid4(),
            provider_id=uuid4(),
            service_id=uuid4(),
            slot_id=slot_id,
            status=AppointmentStatus.created,
            created_at=datetime.now(UTC),
        )
    )
    appointment_repo.update_status = AsyncMock(
        return_value=Appointment(
            id=uuid4(),
            client_id=uuid4(),
            provider_id=uuid4(),
            service_id=uuid4(),
            slot_id=slot_id,
            status=AppointmentStatus.cancelled,
            created_at=datetime.now(UTC),
        )
    )

    service = AppointmentService(
        appointment_repo=appointment_repo,
        schedule_repo=schedule_repo,
        cache=cache,
        publisher=publisher,
        session=session,
    )

    appointment = await service.create_appointment(uuid4(), uuid4(), uuid4(), slot_id)
    assert appointment.status == AppointmentStatus.created
    assert publisher.events[0]["headers"]["event"] == "appointment.created"

    cancelled = await service.cancel_appointment(appointment.id)
    assert cancelled.status == AppointmentStatus.cancelled
    assert publisher.events[-1]["headers"]["event"] == "appointment.cancelled"
    assert cache.slots == {}

