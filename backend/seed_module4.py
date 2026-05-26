import asyncio
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from backend.models.models import User, Trade, PortfolioSnapshot
# Adjust connection string to pull from your local configuration environment
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/raptor_ledger"

logger = structlog.get_logger("raptor_ledger.seeder.module4")

logger.info("seed_module4.py begins")


async def seed_portfolio_data():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Fetch matching default developer context
        result = await session.execute(select(User).where(User.email == "ayberk@raptorledger.ai"))
        user = result.scalar_one_or_none()

        if not user:
            logger.error("Seeding aborted. Execute 'python seed_user.py' before running this module seeder.")
            return

        logger.info("Target developer account localized. Compiling ledger mutations.", user_id=str(user.id))

        # 2. Inject Historical Trades matching contracts
        mock_trades = [
            Trade(
                user_id=user.id,
                symbol="BTCUSDT",
                action="BUY",
                quantity=0.002,
                price=64200.0,
                order_id="MOCK_HIST_881",
                timestamp=datetime.utcnow() - timedelta(days=2)
            ),
            Trade(
                user_id=user.id,
                symbol="ETHUSDT",
                action="BUY",
                quantity=0.5,
                price=3150.0,
                order_id="MOCK_HIST_882",
                timestamp=datetime.utcnow() - timedelta(hours=12)
            )
        ]
        session.add_all(mock_trades)

        # 3. Inject Historical Portfolio Snapshots
        mock_snapshots = [
            PortfolioSnapshot(
                user_id=user.id,
                balance=195.27,
                daily_pnl=1.12,
                open_positions=[],
                created_at=datetime.utcnow() - timedelta(days=1)
            ),
            PortfolioSnapshot(
                user_id=user.id,
                balance=198.42,
                daily_pnl=3.15,
                open_positions=[],
                created_at=datetime.utcnow()
            )
        ]
        session.add_all(mock_snapshots)

        await session.commit()
        logger.info("Module 4 database ledger initialized and synchronized successfully.")

if __name__ == "__main__":
    asyncio.run(seed_portfolio_data())
