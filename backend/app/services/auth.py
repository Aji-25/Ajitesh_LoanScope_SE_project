import uuid
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.repositories.users import UserRepository
from app.models.database import User
from app.models.domain import RoleName
from app.schemas.auth import RegisterRequest, UserResponse

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded_hash: str) -> bool:
    return password_hash.verify(password, encoded_hash)


def create_access_token(user_id: uuid.UUID) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> uuid.UUID | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        return None


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
    )


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.users.get_by_email(email)
        if user is None or not user.is_active or not verify_password(password, user.password_hash):
            return None
        return user

    async def register(self, data: RegisterRequest) -> User | None:
        if await self.users.get_by_email(str(data.email)) is not None:
            return None
        role = await self.users.get_role_by_name(RoleName.BUSINESS_ANALYST)
        if role is None:
            raise RuntimeError("Business Analyst role is unavailable.")
        user = User(
            email=str(data.email),
            full_name=data.full_name,
            password_hash=hash_password(data.password),
            role_id=role.id,
            role=role,
        )
        self.users.add(user)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            return None
        return user
