from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.appointments import AppointmentCreate, AppointmentResponse
from app.application.appointments.service import AppointmentService
from app.core.dependencies import get_cache, get_db_session, get_publisher
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.mq.publisher import EventPublisher
from app.infrastructure.repositories.appointments import SqlAlchemyAppointmentRepository
from app.infrastructure.repositories.schedules import SqlAlchemyScheduleRepository

router = APIRouter()


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
    publisher: EventPublisher = Depends(get_publisher),
) -> AppointmentResponse:
    service = AppointmentService(
        appointment_repo=SqlAlchemyAppointmentRepository(session),
        schedule_repo=SqlAlchemyScheduleRepository(session),
        cache=cache,
        publisher=publisher,
        session=session,
    )
    try:
        appointment = await service.create_appointment(
            client_id=payload.client_id,
            provider_id=payload.provider_id,
            service_id=payload.service_id,
            slot_id=payload.slot_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AppointmentResponse.model_validate(appointment.model_dump())


@router.post("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    cache: RedisCache = Depends(get_cache),
    publisher: EventPublisher = Depends(get_publisher),
) -> AppointmentResponse:
    service = AppointmentService(
        appointment_repo=SqlAlchemyAppointmentRepository(session),
        schedule_repo=SqlAlchemyScheduleRepository(session),
        cache=cache,
        publisher=publisher,
        session=session,
    )
    try:
        appointment = await service.cancel_appointment(appointment_id)
    except ValueError as exc:
        detail = str(exc)
        if "already cancelled" in detail.lower():
            raise HTTPException(status_code=409, detail=detail) from exc
        raise HTTPException(status_code=404, detail=detail) from exc
    return AppointmentResponse.model_validate(appointment.model_dump())

