from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.schedules import SlotCreate, SlotResponse
from app.application.schedules.service import ScheduleService
from app.core.dependencies import get_cache, get_db_session
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.repositories.schedules import SqlAlchemyScheduleRepository

router = APIRouter()


@router.post("/slots", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
async def create_slot(
    payload: SlotCreate,
    session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
) -> SlotResponse:
    service = ScheduleService(repo=SqlAlchemyScheduleRepository(session), cache=cache, session=session)
    slot = await service.create_slot(
        provider_id=payload.provider_id, starts_at=payload.starts_at, ends_at=payload.ends_at
    )
    return SlotResponse.model_validate(slot.model_dump())


@router.get("/slots", response_model=list[SlotResponse])
async def list_slots(
    provider_id: UUID | None = Query(None),
    day: str | None = Query(None, description="Filter by date (YYYY-MM-DD or ISO datetime)"),
    session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
) -> list[SlotResponse]:
    parsed_day: date | None = None
    if day:
        try:
            parsed_day = date.fromisoformat(day)
        except ValueError:
            try:
                parsed_day = datetime.fromisoformat(day).date()
            except ValueError:
                raise HTTPException(status_code=422, detail="day must be ISO date or datetime") from None

    service = ScheduleService(repo=SqlAlchemyScheduleRepository(session), cache=cache, session=session)
    slots = await service.list_available(provider_id=provider_id, date_filter=parsed_day)
    return [SlotResponse.model_validate(slot.model_dump()) for slot in slots]

