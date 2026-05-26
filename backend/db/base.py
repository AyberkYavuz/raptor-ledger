# backend/db/base.py
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Fetch database environment settings fallback context
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ayberk:password123@localhost:5432/raptor_ledger"
)

# Initialize production grade asynchronous connection framework
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Declarative metadata wrapper target mappings
Base = declarative_base()

# Configure isolated transactional session factories
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# FastAPI context dependencies injector engine
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield operational session transactions safely utilizing structured block closures."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
