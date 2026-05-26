# backend/api/trading_control.py
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import get_db
from backend.core.dependencies import get_current_user
from backend.models.models import User
from backend.services.scheduler_service import TradingScheduler
from backend.core.state import trading_state
from backend.tools.mock_binance_tool import MockBinanceTool
from backend.services.portfolio_service import PortfolioService

logger = structlog.get_logger("raptor_ledger.api.trading_control")
router = APIRouter(prefix="/api/trading", tags=["Trading Control"])

logger.info("trading_control.py begins")

# Global scheduler instance (singleton)
scheduler = TradingScheduler()

# --- Request/Response Schemas (matching api_contracts.txt) ---


class StartTradingRequest(BaseModel):
    symbols: List[str] = Field(..., min_items=1)
    initial_budget: float = Field(..., gt=0)
    max_daily_loss: float = Field(..., gt=0)
    trading_mode: str = Field(..., pattern="^(paper|live)$")


class UpdateRiskLimitsRequest(BaseModel):
    max_daily_loss: float = Field(..., gt=0)
    max_position_size: float = Field(..., gt=0)


class SwitchModeRequest(BaseModel):
    trading_mode: str = Field(..., pattern="^(paper|live)$")


class TradingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# --- Endpoints ---


@router.post("/start", response_model=TradingResponse)
async def start_trading(
    req: StartTradingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start the AI trading workflow (background scheduler)."""
    try:
        # You can pass a custom agent callback that uses the user context
        # Here we use the default placeholder; in production you'd inject a LangGraph agent
        await scheduler.start_trading(
            symbols=req.symbols,
            initial_budget=req.initial_budget,
            max_daily_loss=req.max_daily_loss,
            trading_mode=req.trading_mode,
            agent_callback=None   # uses default _default_agent_cycle
        )
        return TradingResponse(
            success=True,
            message="Trading workflow started successfully.",
            data={"workflow_status": "active"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to start trading", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/stop", response_model=TradingResponse)
async def stop_trading(current_user: User = Depends(get_current_user)):
    """Stop the trading workflow gracefully."""
    await scheduler.stop_trading()
    return TradingResponse(
        success=True,
        message="Trading workflow stopped successfully."
    )


@router.post("/emergency-stop", response_model=TradingResponse)
async def emergency_stop(current_user: User = Depends(get_current_user)):
    """Immediately kill all trading activity."""
    await scheduler.emergency_stop()
    return TradingResponse(
        success=True,
        message="Emergency stop activated."
    )


@router.put("/risk-limits", response_model=TradingResponse)
async def update_risk_limits(
    req: UpdateRiskLimitsRequest,
    current_user: User = Depends(get_current_user)
):
    """Update runtime risk parameters."""
    await scheduler.update_risk_limits(req.max_daily_loss, req.max_position_size)
    return TradingResponse(
        success=True,
        message="Risk limits updated successfully."
    )


@router.post("/paper-live", response_model=TradingResponse)
async def switch_mode(
    req: SwitchModeRequest,
    current_user: User = Depends(get_current_user)
):
    """Switch between paper and live trading."""
    await scheduler.switch_mode(req.trading_mode)
    return TradingResponse(
        success=True,
        message="Trading mode updated successfully.",
        data={"trading_mode": req.trading_mode}
    )


@router.delete("/trades/open-positions/{symbol}", response_model=TradingResponse)
async def close_position_manually(
    symbol: str = Path(..., description="Trading pair symbol, e.g., BTCUSDT"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manual position close (emergency override).
    Uses the MockBinanceTool to simulate a market sell.
    """
    binance = MockBinanceTool()
    portfolio_svc = PortfolioService(binance)

    # Get current open positions to find the quantity
    open_positions = await portfolio_svc.get_open_positions(db, current_user.id)
    position = next((p for p in open_positions if p.symbol == symbol), None)
    if not position:
        raise HTTPException(status_code=404, detail=f"No open position for {symbol}")

    try:
        # Execute market sell
        executed = await binance.place_order(
            symbol=symbol,
            side="SELL",
            quantity=position.quantity,
            simulate_slippage=True
        )
        exit_price = float(executed["price"])
        logger.info(f"Manually closed {symbol} at {exit_price}", user_id=str(current_user.id))

        return TradingResponse(
            success=True,
            message="Position closed successfully.",
            data={"symbol": symbol, "exit_price": exit_price}
        )
    except Exception as e:
        logger.exception("Manual close failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Add a status endpoint to query current trading state (optional but helpful)
@router.get("/status", response_model=TradingResponse)
async def get_trading_status(current_user: User = Depends(get_current_user)):
    """Return current trading state (active, mode, risk limits)."""
    state = await trading_state.get_state()
    return TradingResponse(
        success=True,
        message="Current trading status",
        data=state
    )
