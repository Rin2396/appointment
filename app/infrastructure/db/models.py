from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.appointments.entities import AppointmentStatus
from app.domain.users.entities import UserRole


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    services: Mapped[list["ServiceModel"]] = relationship("ServiceModel", back_populates="provider")


class ServiceModel(Base):
    __tablename__ = "services"

    id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    provider_id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_min: Mapped[int] = mapped_column()
    price: Mapped[float] = mapped_column(Numeric(10, 2))

    provider: Mapped[UserModel] = relationship("UserModel", back_populates="services")


class ScheduleSlotModel(Base):
    __tablename__ = "schedule_slots"

    id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    provider_id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="chk_slot_time"),
    )


class AppointmentModel(Base):
    __tablename__ = "appointments"

    id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider_id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    service_id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    slot_id: Mapped["UUID"] = mapped_column(PGUUID(as_uuid=True), ForeignKey("schedule_slots.id"), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status"), default=AppointmentStatus.created
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

