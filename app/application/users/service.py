from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories import UserRepository
from app.domain.users.entities import User, UserRole


class UserService:
    def __init__(self, repo: UserRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def create_user(self, email: str, full_name: str, role: UserRole) -> User:
        user = await self.repo.create(email=email, full_name=full_name, role=role)
        await self.session.commit()
        return user

