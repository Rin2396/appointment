from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cache import CacheProvider
from app.application.interfaces.repositories import ServiceRepository
from app.domain.services.entities import Service


class ServicesService:
    def __init__(self, repo: ServiceRepository, cache: CacheProvider, session: AsyncSession):
        self.repo = repo
        self.cache = cache
        self.session = session

    async def list_services(self, provider_id: UUID | None = None) -> list[Service]:
        cached = await self.cache.get_services(provider_id)
        if cached is not None:
            return list(cached)
        services = list(await self.repo.list(provider_id))
        await self.cache.set_services(provider_id, services)
        return services

    async def create_service(self, provider_id: UUID, title: str, duration_min: int, price: float) -> Service:
        service = await self.repo.create(
            provider_id=provider_id, title=title, duration_min=duration_min, price=price
        )
        await self.session.commit()
        await self.cache.invalidate_services()
        return service

