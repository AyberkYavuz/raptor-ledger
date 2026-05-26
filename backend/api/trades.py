# backend/api/trades.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.db.base import get_db
from backend.schemas.auth import StandardResponse
from backend.schemas.portfolio import TradeHistoryData, OpenPositionSchema
from backend.services.portfolio_service import PortfolioService
from backend.tools.mock_binance_tool import MockBinanceTool
from backend.core.dependencies import get_current_user
from backend.models.models import User

router = APIRouter(prefix="/api/trades", tags=["Trade Ledger Monitoring"])
binance_tool = MockBinanceTool()
portfolio_service = PortfolioService(binance_tool)


@router.get("", response_model=StandardResponse[List[TradeHistoryData]])
async def get_trade_history(
    symbol: Optional[str] = Query(None, description="Filter parameters by asset pairing"),
    limit: int = Query(100, description="Pagination extraction upper boundary"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves historical trade actions pulled from the relational data engine layer."""
    data = await portfolio_service.get_trade_history(db, current_user.id, symbol=symbol, limit=limit)
    return StandardResponse(success=True, message="Trade logs extracted successfully.", data=data)


@router.get("/open-positions", response_model=StandardResponse[List[OpenPositionSchema]])
async def get_open_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves exposures currently unresolved on external exchanges."""
    data = await portfolio_service.get_open_positions(db, current_user.id)
    return StandardResponse(success=True, message="Active trading asset tracking compiled.", data=data)
