# backend/api/trading_control.py
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from backend.models.models import Trade

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import get_db
from backend.core.dependencies import get_current_user
from backend.core.exceptions import raise_http_exception
from backend.models.models import User
from backend.services.scheduler_service import TradingScheduler
from backend.core.state import trading_state
from backend.tools.mock_binance_tool import get_mock_binance
from backend.services.portfolio_service import PortfolioService

logger = structlog.get_logger("raptor_ledger.api.trading_control")
router = APIRouter(prefix="/api/trading", tags=["Trading Control"])

logger.info("trading_control.py begins!")

# Global scheduler instance
scheduler = TradingScheduler()


binance = get_mock_binance()


# ---------- Request Schemas with Custom Validation ----------
class StartTradingRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1)
    initial_budget: float
    max_daily_loss: float
    trading_mode: str

    @field_validator("symbols")
    def validate_symbols(cls, v):
        if not v:
            raise_http_exception(
                status_code=400,
                error_code="INVALID_TRADING_CONFIGURATION",
                message="Validation error. symbols list cannot be empty."
            )
        return v

    @field_validator("initial_budget")
    def validate_initial_budget(cls, v):
        if v <= 0:
            raise_http_exception(
                status_code=400,
                error_code="INVALID_TRADING_CONFIGURATION",
                message="Validation error. initial_budget must be greater than 0."
            )
        return v

    @field_validator("max_daily_loss")
    def validate_max_daily_loss(cls, v):
        if v <= 0:
            raise_http_exception(
                status_code=400,
                error_code="INVALID_TRADING_CONFIGURATION",
                message="Validation error. max_daily_loss must be greater than 0."
            )
        return v

    @field_validator("trading_mode")
    def validate_trading_mode(cls, v):
        if v not in ("paper", "live"):
            raise_http_exception(
                status_code=400,
                error_code="INVALID_TRADING_CONFIGURATION",
                message="Validation error. trading_mode must be 'paper' or 'live'."
            )
        return v


class UpdateRiskLimitsRequest(BaseModel):
    max_daily_loss: float = Field(..., gt=0)
    max_position_size: float = Field(..., gt=0)


class SwitchModeRequest(BaseModel):
    trading_mode: str

    @field_validator("trading_mode")
    def validate_mode(cls, v):
        if v not in ("paper", "live"):
            raise_http_exception(
                status_code=400,
                error_code="INVALID_TRADING_CONFIGURATION",
                message="Validation error. trading_mode must be 'paper' or 'live'."
            )
        return v


class TradingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# ---------- Endpoints ----------
@router.post("/start", response_model=TradingResponse)
async def start_trading(
    req: StartTradingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start the AI trading workflow (background scheduler)."""
    try:
        await scheduler.start_trading(
            symbols=req.symbols,
            initial_budget=req.initial_budget,
            max_daily_loss=req.max_daily_loss,
            trading_mode=req.trading_mode,
            agent_callback=None
        )
        return TradingResponse(
            success=True,
            message="Trading workflow started successfully.",
            data={"workflow_status": "active"}
        )
    except ValueError as e:
        raise_http_exception(400, "INVALID_TRADING_CONFIGURATION", str(e))
    except Exception as e:
        logger.exception("Failed to start trading", error=str(e))
        raise_http_exception(500, "INTERNAL_ERROR", "Internal server error")


@router.post("/stop", response_model=TradingResponse)
async def stop_trading(current_user: User = Depends(get_current_user)):
    await scheduler.stop_trading()
    return TradingResponse(success=True, message="Trading workflow stopped successfully.")


@router.post("/emergency-stop", response_model=TradingResponse)
async def emergency_stop(current_user: User = Depends(get_current_user)):
    await scheduler.emergency_stop()
    return TradingResponse(success=True, message="Emergency stop activated.")


@router.put("/risk-limits", response_model=TradingResponse)
async def update_risk_limits(
    req: UpdateRiskLimitsRequest,
    current_user: User = Depends(get_current_user)
):
    await scheduler.update_risk_limits(req.max_daily_loss, req.max_position_size)
    return TradingResponse(success=True, message="Risk limits updated successfully.")


@router.post("/paper-live", response_model=TradingResponse)
async def switch_mode(
    req: SwitchModeRequest,
    current_user: User = Depends(get_current_user)
):
    await scheduler.switch_mode(req.trading_mode)
    return TradingResponse(
        success=True,
        message="Trading mode updated successfully.",
        data={"trading_mode": req.trading_mode}
    )


# ---------- Manual Position Close – exact contract path ----------
# Overrides router prefix to match DELETE /api/trades/open-positions/{symbol}
@router.delete("/api/trades/open-positions/{symbol}", response_model=TradingResponse)
async def close_position_manually(
    symbol: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Close a position using database‑computed net quantity."""
    portfolio_svc = PortfolioService(binance)

    # 1. Compute net position from trades table
    net_qty = await portfolio_svc.get_net_position(db, current_user.id, symbol)
    if net_qty <= 0:
        raise_http_exception(404, "NO_OPEN_POSITION", f"No open position for {symbol} (net={net_qty})")

    # 2. Get current market price
    current_price = await binance.get_market_price(symbol)

    # 3. Execute market SELL
    try:
        executed = await binance.place_order(
            symbol=symbol,
            side="SELL",
            quantity=net_qty,
            simulate_slippage=True
        )
        exit_price = float(executed["price"])

        # 4. Record the SELL trade in the database
        new_trade = Trade(
            user_id=current_user.id,
            symbol=symbol,
            action="SELL",
            quantity=net_qty,
            price=exit_price,
            profit_loss=0.0,  # optionally compute later
            order_id=executed["orderId"],
            timestamp=datetime.utcnow()
        )
        db.add(new_trade)
        await db.commit()

        logger.info(
            "Manual position closed (DB recorded)",
            symbol=symbol, quantity=net_qty, exit_price=exit_price,
            user_id=str(current_user.id)
        )
        return TradingResponse(
            success=True,
            message="Position closed successfully.",
            data={"symbol": symbol, "exit_price": exit_price}
        )
    except Exception as e:
        await db.rollback()
        logger.exception("Manual close failed", error=str(e))
        raise_http_exception(500, "CLOSE_FAILED", str(e))


# ---------- Status endpoint (helper) ----------
@router.get("/status", response_model=TradingResponse)
async def get_trading_status(current_user: User = Depends(get_current_user)):
    state = await trading_state.get_state()
    return TradingResponse(
        success=True,
        message="Current trading status",
        data=state
    )


# ---------- TEMPORARY DEBUG: Create a test position ----------
@router.post("/debug/buy/{symbol}")
async def debug_buy(
    symbol: str,
    quantity: float = 0.001,
    current_user: User = Depends(get_current_user)
):
    """DEBUG ONLY: Force a market buy to create an open position for testing."""
    price = await binance.get_market_price(symbol)
    order = await binance.place_order(symbol, "BUY", quantity, simulate_slippage=True)
    return TradingResponse(
        success=True,
        message="Test position created",
        data={"symbol": symbol, "quantity": quantity, "price": float(order["price"])}
    )
