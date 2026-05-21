# backend/seed_user.py
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# --- FORCE ENVIRONMENT LOADING FIRST ---
env_path = Path(__file__).resolve().parent.parent / "env" / "backend-local.env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from backend.core.logging import configure_logging
import structlog

configure_logging(log_level="INFO")
logger = structlog.get_logger("raptor_ledger.scripts.seed_user")

from backend.db.base import AsyncSessionLocal
from backend.models.models import User
from backend.core.dependencies import hash_password


async def force_seed():
    target_db = os.getenv('DATABASE_URL', '')
    logger.info("FORCING unique verification database write...", target_database=target_db)

    async with AsyncSessionLocal() as session:
        admin_email = "ayberk@raptorledger.ai"

        try:
            # Create the user profile model instance directly
            user = User(
                email=admin_email,
                password_hash=hash_password("securepassword123")
            )

            session.add(user)
            print("⏳ Executing SQL statement serialization via async connection pool...")

            # Explicitly commit the unit of work to the database
            await session.commit()
            print("🚀 Transaction COMMIT command sent to PostgreSQL engine successfully!")

            logger.info("🎉 SUCCESS! Seed profile committed flawlessly.", user_email=admin_email)

        except Exception as e:
            await session.rollback()
            logger.error("❌ Database transaction failed and rolled back safely", error=str(e))

if __name__ == "__main__":
    asyncio.run(force_seed())
