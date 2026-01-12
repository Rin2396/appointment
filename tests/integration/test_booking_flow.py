from datetime import UTC, datetime, timedelta

import pytest
from testcontainers.postgres import PostgresContainer

from app.application.appointments.service import AppointmentService
from app.application.schedules.service import ScheduleService
from app.application.services.service import ServicesService
from app.core.db import Base, create_engine, create_session_factory
from app.domain.appointments.entities import AppointmentStatus
from app.domain.users.entities import UserRole
from app.infrastructure.db import models  # noqa: F401
from app.infrastructure.repositories.appointments import SqlAlchemyAppointmentRepository
from app.infrastructure.repositories.schedules import SqlAlchemyScheduleRepository
from app.infrastructure.repositories.services import SqlAlchemyServiceRepository
from app.infrastructure.repositories.users import SqlAlchemyUserRepository
from tests.fakes import DummyPublisher, InMemoryCache


@pytest.mark.asyncio
async def test_booking_and_cancellation_flow():
    with PostgresContainer("postgres:15") as pg:
        db_url = pg.get_connection_url()
        async_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://").replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        engine = create_engine(async_url)
        session_factory = create_session_factory(engine)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        cache = InMemoryCache()
        publisher = DummyPublisher()
        async with session_factory() as session:
            user_repo = SqlAlchemyUserRepository(session)
            provider = await user_repo.create("provider@example.com", "Provider", UserRole.provider)
            client = await user_repo.create("client@example.com", "Client", UserRole.client)
            await session.commit()

            service_repo = SqlAlchemyServiceRepository(session)
            services_service = ServicesService(service_repo, cache, session)
            service = await services_service.create_service(provider.id, "Consultation", 30, 50.0)

            schedule_repo = SqlAlchemyScheduleRepository(session)
            schedule_service = ScheduleService(schedule_repo, cache, session)
            start_time = datetime.now(UTC) + timedelta(hours=1)
            end_time = start_time + timedelta(minutes=30)
            slot = await schedule_service.create_slot(provider.id, start_time, end_time)

            appointment_repo = SqlAlchemyAppointmentRepository(session)
            appointment_service = AppointmentService(
                appointment_repo=appointment_repo,
                schedule_repo=schedule_repo,
                cache=cache,
                publisher=publisher,
                session=session,
            )

            appointment = await appointment_service.create_appointment(
                client_id=client.id,
                provider_id=provider.id,
                service_id=service.id,
                slot_id=slot.id,
            )
            assert appointment.status == AppointmentStatus.created
            slots_after_booking = await schedule_service.list_available(provider.id, start_time.date())
            assert slots_after_booking == []

            cancelled = await appointment_service.cancel_appointment(appointment.id)
            assert cancelled.status == AppointmentStatus.cancelled
            slots_after_cancel = await schedule_service.list_available(provider.id, start_time.date())
            assert len(slots_after_cancel) == 1
            assert slots_after_cancel[0].is_available is True

        await engine.dispose()

