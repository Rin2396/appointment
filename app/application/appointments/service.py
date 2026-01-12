from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.cache import CacheProvider
from app.application.interfaces.mq import EventPublisher
from app.application.interfaces.repositories import AppointmentRepository, ScheduleRepository
from app.domain.appointments.entities import Appointment, AppointmentStatus


class AppointmentService:
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        schedule_repo: ScheduleRepository,
        cache: CacheProvider,
        publisher: EventPublisher,
        session: AsyncSession,
    ):
        self.appointment_repo = appointment_repo
        self.schedule_repo = schedule_repo
        self.cache = cache
        self.publisher = publisher
        self.session = session

    async def create_appointment(
        self, client_id: UUID, provider_id: UUID, service_id: UUID, slot_id: UUID
    ) -> Appointment:
        async def _do_create() -> Appointment:
            slot = await self.schedule_repo.lock_slot(slot_id)
            if slot is None or not slot.is_available:
                raise ValueError("Slot is not available")
            await self.schedule_repo.mark_slot_availability(slot_id, False)
            appointment = await self.appointment_repo.create(
                client_id=client_id,
                provider_id=provider_id,
                service_id=service_id,
                slot_id=slot_id,
                status=AppointmentStatus.created,
            )
            return appointment

        if self.session.in_transaction():
            appointment = await _do_create()
        else:
            async with self.session.begin():
                appointment = await _do_create()

        await self.cache.invalidate_slots()
        await self.publisher.publish(
            routing_key="appointment.created",
            payload={
                "appointment_id": str(appointment.id),
                "client_id": str(client_id),
                "provider_id": str(provider_id),
                "service_id": str(service_id),
                "slot_id": str(slot_id),
            },
            headers={"attempt": 1, "event": "appointment.created"},
        )
        return appointment

    async def cancel_appointment(self, appointment_id: UUID) -> Appointment:
        async def _do_cancel() -> Appointment:
            appointment = await self.appointment_repo.get(appointment_id)
            if appointment is None:
                raise ValueError("Appointment not found")
            if appointment.status == AppointmentStatus.cancelled:
                raise ValueError("Appointment already cancelled")
            appointment = await self.appointment_repo.update_status(
                appointment_id, AppointmentStatus.cancelled
            )
            if appointment is None:
                raise ValueError("Unable to update appointment")
            await self.schedule_repo.mark_slot_availability(appointment.slot_id, True)

            return appointment

        if self.session.in_transaction():
            appointment = await _do_cancel()
        else:
            async with self.session.begin():
                appointment = await _do_cancel()

        await self.cache.invalidate_slots()
        await self.publisher.publish(
            routing_key="appointment.cancelled",
            payload={"appointment_id": str(appointment_id), "slot_id": str(appointment.slot_id)},
            headers={"attempt": 1, "event": "appointment.cancelled"},
        )
        return appointment

