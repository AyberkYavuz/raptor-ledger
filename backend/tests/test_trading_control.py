# backend/tests/test_trading_control.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.services.scheduler_service import TradingScheduler


@pytest.mark.asyncio
async def test_safe_wrapper_catches_exception():
    scheduler = TradingScheduler()

    # Create a failing callback
    async def failing_callback():
        raise ValueError("Intentional failure")

    # The wrapper should log but not raise
    await scheduler._safe_execution_wrapper(failing_callback)
    # No exception propagated – test passes


@pytest.mark.asyncio
async def test_safe_wrapper_skips_when_emergency():
    scheduler = TradingScheduler()
    mock_callback = AsyncMock()
    # Set emergency active
    from backend.core.state import trading_state
    await trading_state.set_emergency_active(True)

    await scheduler._safe_execution_wrapper(mock_callback)
    mock_callback.assert_not_awaited()

    # Cleanup
    await trading_state.set_emergency_active(False)
