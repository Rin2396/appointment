from collections.abc import Sequence
from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schedules.entities import ScheduleSlot
from app.infrastructure.db.models import ScheduleSlotModel


def _to_domain(model: ScheduleSlotModel) -> ScheduleSlot:
    return ScheduleSlot(
        id=model.id,
        provider_id=model.provider_id,
        starts_at=model.starts_at,
        ends_at=model.ends_at,
        is_available=model.is_available,
    )


class SqlAlchemyScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_slot(self, provider_id: UUID, starts_at: datetime, ends_at: datetime) -> ScheduleSlot:
        model = ScheduleSlotModel(provider_id=provider_id, starts_at=starts_at, ends_at=ends_at)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _to_domain(model)

    async def list_available(self, provider_id: UUID | None, date_filter: date | None) -> Sequence[ScheduleSlot]:
        stmt = select(ScheduleSlotModel)
        if provider_id:
            stmt = stmt.where(ScheduleSlotModel.provider_id == provider_id)
        if date_filter:
            next_day = date_filter + timedelta(days=1)
            stmt = stmt.where(
                ScheduleSlotModel.starts_at >= datetime.combine(date_filter, datetime.min.time()),
                ScheduleSlotModel.starts_at < datetime.combine(next_day, datetime.min.time()),
            )
        stmt = stmt.where(ScheduleSlotModel.is_available.is_(True))
        result = await self.session.execute(stmt)
        return [_to_domain(model) for model in result.scalars().all()]

    async def mark_slot_availability(self, slot_id: UUID, is_available: bool) -> ScheduleSlot | None:
        stmt = select(ScheduleSlotModel).where(ScheduleSlotModel.id == slot_id).with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.is_available = is_available
        await self.session.flush()
        return _to_domain(model)

    async def lock_slot(self, slot_id: UUID) -> ScheduleSlot | None:
        stmt = select(ScheduleSlotModel).where(ScheduleSlotModel.id == slot_id).with_for_update()
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

