from uuid import UUID

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    provider_id: UUID
    title: str
    duration_min: int
    price: float


class ServiceResponse(BaseModel):
    id: UUID
    provider_id: UUID
    title: str
    duration_min: int
    price: float

