from datetime import date, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cache import CacheProvider
from app.application.interfaces.repositories import ScheduleRepository
from app.domain.schedules.entities import ScheduleSlot


class ScheduleService:
    def __init__(self, repo: ScheduleRepository, cache: CacheProvider, session: AsyncSession):
        self.repo = repo
        self.cache = cache
        self.session = session

    async def create_slot(self, provider_id: UUID, starts_at: datetime, ends_at: datetime) -> ScheduleSlot:
        slot = await self.repo.create_slot(provider_id=provider_id, starts_at=starts_at, ends_at=ends_at)
        await self.session.commit()
        await self.cache.invalidate_slots()
        return slot

    async def list_available(self, provider_id: UUID | None, date_filter: date | None) -> list[ScheduleSlot]:
        cached = await self.cache.get_slots(provider_id, date_filter)
        if cached is not None:
            return list(cached)
        slots = list(await self.repo.list_available(provider_id, date_filter))
        await self.cache.set_slots(provider_id, date_filter, slots)
        return slots

    async def mark_slot(self, slot_id: UUID, is_available: bool) -> ScheduleSlot | None:
        slot = await self.repo.mark_slot_availability(slot_id, is_available)
        await self.session.commit()
        await self.cache.invalidate_slots()
        return slot

