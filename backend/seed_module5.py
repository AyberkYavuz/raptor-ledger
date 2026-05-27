import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Force environment loading
env_path = Path(__file__).resolve().parent.parent / "env" / "backend-local.env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from backend.core.logging import configure_logging
import structlog

configure_logging(log_level="INFO")
logger = structlog.get_logger("raptor_ledger.scripts.seed_module5")

logger.info("seed_module5.py begins")

from backend.db.base import AsyncSessionLocal
from backend.models.models import User, Trade
from sqlalchemy.future import select


async def seed_test_position():
    async with AsyncSessionLocal() as session:
        # Get the test user (same as Module 4)
        result = await session.execute(select(User).where(User.email == "ayberk@raptorledger.ai"))
        user = result.scalar_one_or_none()
        if not user:
            logger.error("User not found. Run seed_user.py first.")
            return

        # Check if we already inserted this test trade (avoid duplicates)
        result = await session.execute(
            select(Trade).where(
                Trade.user_id == user.id,
                Trade.order_id == "MOCK_TEST_CLOSE_001"
            )
        )
        if result.scalar_one_or_none():
            logger.info("Test trade already exists – skipping insert.")
            return

        # Insert a BUY trade for testing manual close
        test_trade = Trade(
            user_id=user.id,
            symbol="SOLUSDT",           # changed from BTCUSDT
            action="BUY",
            quantity=5.0,               # 5 SOL
            price=180.0,                # entry price
            profit_loss=0.0,
            order_id="MOCK_TEST_SOL_001",
            timestamp=datetime.utcnow()
        )
        session.add(test_trade)
        await session.commit()
        logger.info("✅ Test BUY trade inserted. You can now call DELETE /api/trades/open-positions/BTCUSDT")

if __name__ == "__main__":
    asyncio.run(seed_test_position())
