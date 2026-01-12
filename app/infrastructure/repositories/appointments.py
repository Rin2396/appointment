from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.appointments.entities import Appointment, AppointmentStatus
from app.infrastructure.db.models import AppointmentModel


def _to_domain(model: AppointmentModel) -> Appointment:
    return Appointment(
        id=model.id,
        client_id=model.client_id,
        provider_id=model.provider_id,
        service_id=model.service_id,
        slot_id=model.slot_id,
        status=model.status,
        created_at=model.created_at,
    )


class SqlAlchemyAppointmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        client_id: UUID,
        provider_id: UUID,
        service_id: UUID,
        slot_id: UUID,
        status: AppointmentStatus = AppointmentStatus.created,
    ) -> Appointment:
        model = AppointmentModel(
            client_id=client_id,
            provider_id=provider_id,
            service_id=service_id,
            slot_id=slot_id,
            status=status,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _to_domain(model)

    async def get(self, appointment_id: UUID) -> Appointment | None:
        stmt = select(AppointmentModel).where(AppointmentModel.id == appointment_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def update_status(self, appointment_id: UUID, status: AppointmentStatus) -> Appointment | None:
        stmt = select(AppointmentModel).where(AppointmentModel.id == appointment_id).with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.status = status
        await self.session.flush()
        return _to_domain(model)

