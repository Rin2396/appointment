from uuid import UUID

from pydantic import BaseModel


class Service(BaseModel):
    id: UUID
    provider_id: UUID
    title: str
    duration_min: int
    price: float


