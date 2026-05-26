import asyncio
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- FORCE ENVIRONMENT LOADING FIRST ---
# This ensures it aligns with your Mac Mini filesystem configuration
env_path = Path(__file__).resolve().parent.parent / "env" / "backend-local.env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from backend.core.logging import configure_logging
import structlog

configure_logging(log_level="INFO")
logger = structlog.get_logger("raptor_ledger.scripts.seed_module4")

logger.info("seed_module4.py begins")

from backend.db.base import AsyncSessionLocal, engine, Base
from backend.models.models import User, Trade, PortfolioSnapshot
from sqlalchemy.future import select


async def seed_portfolio_data():
    target_db = os.getenv('DATABASE_URL', '')
    logger.info("Initializing Module 4 database verification rows", target_database=target_db)

    # 1. Guarantee structural table schemas exist before attempting mutations
    async with engine.begin() as conn:
        logger.info("Synchronizing relational table structures for Module 4...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        admin_email = "ayberk@raptorledger.ai"

        # 2. Fetch matching default developer context
        result = await session.execute(select(User).where(User.email == admin_email))
        user = result.scalar_one_or_none()

        if not user:
            logger.error("Seeding aborted. Please execute 'python seed_user.py' first to establish your profile structure.")
            return

        logger.info("Target developer account localized. Compiling ledger additions.", user_id=str(user.id))

        # Check if trades are already seeded to prevent duplicated primary keys
        trade_check = await session.execute(select(Trade).where(Trade.user_id == user.id))
        if trade_check.scalars().first():
            logger.info("Ledger rows already verified in tables. Skipping insertion step to prevent duplication.")
            return

        # 3. Inject Historical Trades matching Section 18.9.1 contracts
        base_time = datetime.utcnow()
        mock_trades = [
            Trade(
                user_id=user.id,
                symbol="BTCUSDT",
                action="BUY",
                quantity=0.002,
                price=64200.0,
                profit_loss=0.0,
                order_id="MOCK_HIST_881",
                timestamp=base_time - timedelta(days=2)
            ),
            Trade(
                user_id=user.id,
                symbol="ETHUSDT",
                action="BUY",
                quantity=0.5,
                price=3150.0,
                profit_loss=0.0,
                order_id="MOCK_HIST_882",
                timestamp=base_time - timedelta(hours=12)
            )
        ]
        session.add_all(mock_trades)

        # 4. Inject Historical Portfolio Snapshots matching Section 18.8.2 contracts
        mock_snapshots = [
            PortfolioSnapshot(
                user_id=user.id,
                balance=195.27,
                daily_pnl=1.12,
                open_positions=[
                    {"symbol": "BTCUSDT", "quantity": 0.002, "entry_price": 64200.0, "current_price": 64550.0, "unrealized_pnl": 0.70}
                ],
                created_at=base_time - timedelta(days=1)
            ),
            PortfolioSnapshot(
                user_id=user.id,
                balance=198.42,
                daily_pnl=3.15,
                open_positions=[
                    {"symbol": "BTCUSDT", "quantity": 0.002, "entry_price": 64200.0, "current_price": 64550.0, "unrealized_pnl": 0.70}
                ],
                created_at=base_time
            )
        ]
        session.add_all(mock_snapshots)

        try:
            print("⏳ Serializing historical ledger metrics to database cluster context...")
            await session.commit()
            logger.info("🎉 SUCCESS! Module 4 database tables synchronized and populated seamlessly.")
        except Exception as e:
            await session.rollback()
            logger.error("❌ Database transaction failed and rolled back safely", error=str(e))

if __name__ == "__main__":
    asyncio.run(seed_portfolio_data())
