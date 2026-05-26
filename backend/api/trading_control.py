# backend/api/trading_control.py
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import get_db
from backend.core.dependencies import get_current_user
from backend.core.exceptions import raise_http_exception
from backend.models.models import User
from backend.services.scheduler_service import TradingScheduler
from backend.core.state import trading_state
from backend.tools.mock_binance_tool import MockBinanceTool
from backend.services.portfolio_service import PortfolioService

logger = structlog.get_logger("raptor_ledger.api.trading_control")
router = APIRouter(prefix="/api/trading", tags=["Trading Control"])

logger.info("trading_control.py begins!")

# Global scheduler instance
scheduler = TradingScheduler()


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
    symbol: str = Path(..., description="Trading pair symbol, e.g., BTCUSDT"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually close an open position (emergency override).
    Bypasses the '/api/trading' prefix to fulfill the explicit contract:
    DELETE /api/trades/open-positions/{symbol}
    """
    binance = MockBinanceTool()
    portfolio_svc = PortfolioService(binance)

    open_positions = await portfolio_svc.get_open_positions(db, current_user.id)
    position = next((p for p in open_positions if p.symbol == symbol), None)
    if not position:
        raise_http_exception(
            status_code=404,
            error_code="NO_OPEN_POSITION",
            message=f"No open position found for symbol {symbol}."
        )

    try:
        executed = await binance.place_order(
            symbol=symbol,
            side="SELL",
            quantity=position.quantity,
            simulate_slippage=True
        )
        exit_price = float(executed["price"])
        logger.info(
            "Manual position closed",
            symbol=symbol,
            quantity=position.quantity,
            exit_price=exit_price,
            user_id=str(current_user.id)
        )
        return TradingResponse(
            success=True,
            message="Position closed successfully.",
            data={"symbol": symbol, "exit_price": exit_price}
        )
    except Exception as e:
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
