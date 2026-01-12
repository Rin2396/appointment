from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.domain.users.entities import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    role: UserRole

