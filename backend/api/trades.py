# backend/api/trades.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from backend.db.base import get_db
from backend.schemas.auth import StandardResponse
from backend.schemas.portfolio import TradeHistoryData
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
    start_date: Optional[datetime] = Query(None, description="ISO-8601 start datetime filter boundary (e.g., 2026-05-12T00:00:00Z)"),
    end_date: Optional[datetime] = Query(None, description="ISO-8601 end datetime filter boundary (e.g., 2026-05-13T00:00:00Z)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves historical trade actions pulled from the relational data engine layer with optional temporal filtering."""
    data = await portfolio_service.get_trade_history(
        db=db,
        user_id=current_user.id,
        symbol=symbol,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    return StandardResponse(success=True, message="Trade logs extracted successfully.", data=data)
