import asyncio
import logging

from app.core.config import get_settings
from app.db.repositories.users import UserRepository
from app.db.session import session_factory
from app.models.database import User
from app.models.domain import RoleName
from app.services.auth import hash_password

logger = logging.getLogger(__name__)


async def seed_bootstrap_user() -> None:
    settings = get_settings()
    if not settings.bootstrap_user_email or not settings.bootstrap_user_password:
        logger.info("Bootstrap user variables are not set; skipping account creation")
        return

    async with session_factory() as session:
        users = UserRepository(session)
        existing = await users.get_by_email(settings.bootstrap_user_email)
        if existing is not None:
            return

        role = await users.get_role_by_name(RoleName.BUSINESS_ANALYST)
        if role is None:
            raise RuntimeError("Business Analyst role is missing; apply migrations first")

        users.add(
            User(
                email=settings.bootstrap_user_email.lower(),
                full_name=settings.bootstrap_user_name,
                password_hash=hash_password(settings.bootstrap_user_password),
                role_id=role.id,
            )
        )
        await session.commit()
        logger.info("Created bootstrap user for local development")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_bootstrap_user())
