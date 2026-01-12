from collections.abc import Sequence
from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.schedules.entities import ScheduleSlot
from app.domain.services.entities import Service


class CacheProvider(Protocol):
    async def get_services(self, provider_id: UUID | None) -> Sequence[Service] | None: ...
    async def set_services(self, provider_id: UUID | None, services: Sequence[Service]) -> None: ...
    async def invalidate_services(self) -> None: ...

    async def get_slots(self, provider_id: UUID | None, date_filter: date | None) -> Sequence[ScheduleSlot] | None: ...
    async def set_slots(
        self, provider_id: UUID | None, date_filter: date | None, slots: Sequence[ScheduleSlot]
    ) -> None: ...
    async def invalidate_slots(self) -> None: ...

