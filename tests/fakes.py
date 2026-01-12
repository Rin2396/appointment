from collections.abc import Sequence
from datetime import date
from typing import Any
from uuid import UUID

from app.application.interfaces.cache import CacheProvider
from app.application.interfaces.mq import EventPublisher
from app.domain.schedules.entities import ScheduleSlot
from app.domain.services.entities import Service


class InMemoryCache(CacheProvider):
    def __init__(self):
        self.services: dict[str, list[Service]] = {}
        self.slots: dict[str, list[ScheduleSlot]] = {}

    async def get_services(self, provider_id: UUID | None):
        return self.services.get(str(provider_id))

    async def set_services(self, provider_id: UUID | None, services: Sequence[Service]) -> None:
        self.services[str(provider_id)] = list(services)

    async def invalidate_services(self) -> None:
        self.services.clear()

    async def get_slots(self, provider_id: UUID | None, date_filter: date | None):
        key = f"{provider_id}:{date_filter}"
        return self.slots.get(key)

    async def set_slots(
        self, provider_id: UUID | None, date_filter: date | None, slots: Sequence[ScheduleSlot]
    ) -> None:
        key = f"{provider_id}:{date_filter}"
        self.slots[key] = list(slots)

    async def invalidate_slots(self) -> None:
        self.slots.clear()


class DummyPublisher(EventPublisher):
    def __init__(self):
        self.events: list[dict[str, Any]] = []

    async def publish(self, routing_key: str, payload: dict, headers: dict | None = None) -> None:
        self.events.append({"routing_key": routing_key, "payload": payload, "headers": headers or {}})

