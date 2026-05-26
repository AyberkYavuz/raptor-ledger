# backend/services/scheduler_service.py
import asyncio
from typing import List, Optional, Dict, Any, Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
import structlog

from backend.core.state import trading_state
from backend.tools.mock_binance_tool import MockBinanceTool
from backend.services.portfolio_service import PortfolioService
from backend.core.config import settings

logger = structlog.get_logger("raptor_ledger.services.scheduler")

logger.info("scheduler_service.py begins")


class TradingScheduler:
    """Singleton manager for the background trading loop."""
    _instance = None
    _scheduler: Optional[AsyncIOScheduler] = None
    _job_id = "trading_cycle_job"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._scheduler is not None:
            return
        self._scheduler = AsyncIOScheduler()
        # Default interval (seconds) – can be made configurable
        self.cycle_interval = 30

    async def start_scheduler(self) -> None:
        """Start the APScheduler background worker (does NOT start trading)."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Background scheduler started")

    async def shutdown_scheduler(self) -> None:
        """Gracefully shutdown scheduler on app exit."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Background scheduler shut down")

    async def start_trading(
        self,
        symbols: List[str],
        initial_budget: float,
        max_daily_loss: float,
        trading_mode: str,
        agent_callback: Optional[Callable[[], Awaitable[None]]] = None
    ) -> None:
        """
        Activate trading workflow: store config, clear emergency flag,
        add or replace the background job.
        """
        # Validate
        if not symbols:
            raise ValueError("Symbols list cannot be empty")
        if initial_budget <= 0:
            raise ValueError("initial_budget must be > 0")
        if max_daily_loss <= 0:
            raise ValueError("max_daily_loss must be > 0")
        if trading_mode not in ("paper", "live"):
            raise ValueError("trading_mode must be 'paper' or 'live'")

        # Reset emergency flag
        await trading_state.set_emergency_active(False)

        # Store configuration
        config = {
            "symbols": symbols,
            "initial_budget": initial_budget,
            "max_daily_loss": max_daily_loss,
            "trading_mode": trading_mode
        }
        await trading_state.set_trading_config(config)
        await trading_state.set_trading_mode(trading_mode)

        # Update risk limits
        await trading_state.set_risk_limits({
            "max_daily_loss": max_daily_loss,
            "max_position_size": settings.MAX_POSITION_SIZE_USD
        })

        # Remove existing job if any
        await self._remove_job()

        # Use provided callback or default placeholder
        callback = agent_callback or self._default_agent_cycle

        # Add new job with wrapped exception handler
        self._scheduler.add_job(
            self._safe_execution_wrapper,
            trigger="interval",
            seconds=self.cycle_interval,
            id=self._job_id,
            args=[callback],
            replace_existing=True,
            max_instances=1
        )
        await trading_state.set_trading_active(True)
        logger.info(
            "Trading workflow started",
            symbols=symbols,
            mode=trading_mode,
            interval_sec=self.cycle_interval
        )

    async def stop_trading(self) -> None:
        """Stop the scheduled job and set active flag to False."""
        await self._remove_job()
        await trading_state.set_trading_active(False)
        logger.info("Trading workflow stopped")

    async def emergency_stop(self) -> None:
        """
        Immediate halt: purge jobs, set emergency flag,
        disable further trading.
        """
        await self._remove_job()
        await trading_state.set_trading_active(False)
        await trading_state.set_emergency_active(True)
        logger.warning("EMERGENCY STOP ACTIVATED – all trading halted")

    async def update_risk_limits(self, max_daily_loss: float, max_position_size: float) -> None:
        """Dynamically change risk parameters (no restart needed)."""
        if max_daily_loss <= 0 or max_position_size <= 0:
            raise ValueError("Risk limits must be > 0")
        await trading_state.set_risk_limits({
            "max_daily_loss": max_daily_loss,
            "max_position_size": max_position_size
        })
        logger.info("Risk limits updated", max_daily_loss=max_daily_loss, max_position_size=max_position_size)

    async def switch_mode(self, new_mode: str) -> None:
        """Switch between paper and live trading while workflow is active."""
        if new_mode not in ("paper", "live"):
            raise ValueError("Mode must be 'paper' or 'live'")
        await trading_state.set_trading_mode(new_mode)
        # Also update stored config
        config = await trading_state.get_state()
        config["trading_config"]["trading_mode"] = new_mode
        logger.info("Trading mode switched", new_mode=new_mode)

    async def _remove_job(self) -> None:
        """Remove the background job if it exists."""
        try:
            self._scheduler.remove_job(self._job_id)
        except JobLookupError:
            pass  # Job not present

    async def _safe_execution_wrapper(self, callback: Callable[[], Awaitable[None]]) -> None:
        """
        Wraps the agent callback with try/except to catch any exception,
        log it, and prevent scheduler crash.
        """
        # Do not run if emergency active
        state = await trading_state.get_state()
        if state["emergency_active"]:
            logger.debug("Skipping trading cycle – emergency stop active")
            return
        if not state["trading_active"]:
            logger.debug("Skipping trading cycle – trading not active")
            return

        try:
            logger.debug("Starting trading cycle")
            await callback()
            logger.debug("Trading cycle completed successfully")
        except Exception as e:
            logger.exception(
                "Agent cycle raised an exception – continuing scheduler",
                error=str(e),
                exc_info=True
            )

    async def _default_agent_cycle(self) -> None:
        """
        Placeholder agent logic. Replace this with your real LangGraph workflow.
        Uses existing MockBinanceTool and PortfolioService for demonstration.
        """
        from backend.db.base import async_session_factory
        from backend.models.models import User  # needed for user_id; we'll assume first user

        logger.info("Running default agent cycle (placeholder)")
        # Obtain a test user – in real scenario you'd pass user_id from the start call
        async with async_session_factory() as db:
            from sqlalchemy import select
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            if not user:
                logger.warning("No user found – cannot run trading cycle")
                return

            # Get current portfolio state
            binance = MockBinanceTool()
            portfolio_svc = PortfolioService(binance)
            portfolio = await portfolio_svc.get_current_portfolio(db, user.id)

            logger.info(
                "Default cycle metrics",
                total_balance=portfolio.total_balance,
                available_cash=portfolio.available_cash,
                trading_mode=(await trading_state.get_state())["trading_mode"]
            )
            # Here you would call your AI agent decision maker
            # and execute trades via binance.place_order()
