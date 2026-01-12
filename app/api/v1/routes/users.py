from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.users import UserCreate, UserResponse
from app.application.users.service import UserService
from app.core.dependencies import get_db_session
from app.infrastructure.repositories.users import SqlAlchemyUserRepository

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_db_session)) -> UserResponse:
    service = UserService(repo=SqlAlchemyUserRepository(session), session=session)
    try:
        user = await service.create_user(email=payload.email, full_name=payload.full_name, role=payload.role)
    except Exception as exc:  # pragma: no cover - unexpected
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UserResponse.model_validate(user.model_dump())
