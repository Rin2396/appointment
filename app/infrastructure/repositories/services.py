from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services.entities import Service
from app.infrastructure.db.models import ServiceModel


def _to_domain(model: ServiceModel) -> Service:
    return Service(
        id=model.id,
        provider_id=model.provider_id,
        title=model.title,
        duration_min=model.duration_min,
        price=float(model.price),
    )


class SqlAlchemyServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, provider_id: UUID | None = None) -> Sequence[Service]:
        stmt = select(ServiceModel)
        if provider_id:
            stmt = stmt.where(ServiceModel.provider_id == provider_id)
        result = await self.session.execute(stmt)
        return [_to_domain(model) for model in result.scalars().all()]

    async def create(self, provider_id: UUID, title: str, duration_min: int, price: float) -> Service:
        model = ServiceModel(provider_id=provider_id, title=title, duration_min=duration_min, price=price)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return _to_domain(model)

