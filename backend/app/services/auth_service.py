from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User

class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def authenticate_user(self, login_data: UserLogin) -> User | None:
        user = await self.repo.get_by_username(login_data.username)
        if not user:
            return None
        if not verify_password(login_data.password, user.password_hash):
            return None
        return user

    async def create_user(self, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        return await self.repo.create({
            "username": user_in.username,
            "password_hash": hashed_password,
            "role": "user" # Default role
        })

    def create_token(self, user: User) -> str:
        return create_access_token(subject=user.username)
