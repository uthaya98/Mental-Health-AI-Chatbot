import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal

logger = logging.getLogger("mental-health-ai")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency injector for SQLite (SQLAlchemy AsyncSession).

    - Provides an AsyncSession to API routes
    - Ensures proper session lifecycle
    - Compatible with async CRUD operations
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("SQLite DB session acquired")
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            logger.debug("SQLite DB session closed")
