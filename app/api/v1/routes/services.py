from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.services import ServiceCreate, ServiceResponse
from app.application.services.service import ServicesService
from app.core.dependencies import get_cache, get_db_session
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.repositories.services import SqlAlchemyServiceRepository

router = APIRouter()


@router.get("", response_model=list[ServiceResponse])
async def list_services(
    provider_id: UUID | None = Query(None),
    session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
) -> list[ServiceResponse]:
    service = ServicesService(repo=SqlAlchemyServiceRepository(session), cache=cache, session=session)
    services = await service.list_services(provider_id)
    return [ServiceResponse.model_validate(item.model_dump()) for item in services]


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    payload: ServiceCreate,
    session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
) -> ServiceResponse:
    service = ServicesService(repo=SqlAlchemyServiceRepository(session), cache=cache, session=session)
    try:
        created = await service.create_service(
            provider_id=payload.provider_id,
            title=payload.title,
            duration_min=payload.duration_min,
            price=payload.price,
        )
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ServiceResponse.model_validate(created.model_dump())

