import json
from collections.abc import Sequence
from datetime import date
from uuid import UUID

from redis.asyncio import Redis

from app.application.interfaces.cache import CacheProvider
from app.core.config import RedisSettings
from app.domain.schedules.entities import ScheduleSlot
from app.domain.services.entities import Service


class RedisCache(CacheProvider):
    def __init__(self, client: Redis, settings: RedisSettings):
        self.client = client
        self.settings = settings

    async def get_services(self, provider_id: UUID | None) -> Sequence[Service] | None:
        key = self._services_key(provider_id)
        raw = await self.client.get(key)
        if not raw:
            return None
        data = json.loads(raw)
        return [Service(**item) for item in data]

    async def set_services(self, provider_id: UUID | None, services: Sequence[Service]) -> None:
        key = self._services_key(provider_id)
        payload = json.dumps([service.model_dump() for service in services], default=str)
        await self.client.set(key, payload, ex=self.settings.services_ttl_seconds)

    async def invalidate_services(self) -> None:
        await self._invalidate_pattern("services:list:*")

    async def get_slots(self, provider_id: UUID | None, date_filter: date | None) -> Sequence[ScheduleSlot] | None:
        key = self._slots_key(provider_id, date_filter)
        raw = await self.client.get(key)
        if not raw:
            return None
        data = json.loads(raw)
        return [ScheduleSlot(**item) for item in data]

    async def set_slots(
        self, provider_id: UUID | None, date_filter: date | None, slots: Sequence[ScheduleSlot]
    ) -> None:
        key = self._slots_key(provider_id, date_filter)
        payload = json.dumps([slot.model_dump() for slot in slots], default=str)
        await self.client.set(key, payload, ex=self.settings.slots_ttl_seconds)

    async def invalidate_slots(self) -> None:
        await self._invalidate_pattern("slots:list:*")

    async def _invalidate_pattern(self, pattern: str) -> None:
        async for key in self.client.scan_iter(match=pattern):
            await self.client.delete(key)

    @staticmethod
    def _services_key(provider_id: UUID | None) -> str:
        suffix = str(provider_id) if provider_id else "all"
        return f"services:list:{suffix}"

    @staticmethod
    def _slots_key(provider_id: UUID | None, date_filter: date | None) -> str:
        provider_part = str(provider_id) if provider_id else "all"
        date_part = date_filter.isoformat() if date_filter else "any"
        return f"slots:list:provider:{provider_part}:date:{date_part}"

