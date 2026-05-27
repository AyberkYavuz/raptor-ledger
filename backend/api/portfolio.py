# backend/api/portfolio.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.db.base import get_db
from backend.schemas.auth import StandardResponse
from backend.schemas.portfolio import PortfolioStatusData, PortfolioHistoryData
from backend.services.portfolio_service import PortfolioService
from backend.tools.mock_binance_tool import get_mock_binance
from backend.core.dependencies import get_current_user  # Core auth check fence
from backend.models.models import User

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio Tracking"])
binance_tool = get_mock_binance()
portfolio_service = PortfolioService(binance_tool)


@router.get("", response_model=StandardResponse[PortfolioStatusData])
async def get_portfolio_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves current execution platform balance tracking matrices and open risks."""
    data = await portfolio_service.get_current_portfolio(db, current_user.id)
    return StandardResponse(success=True, message="Portfolio status loaded.", data=data)


@router.get("/history", response_model=StandardResponse[List[PortfolioHistoryData]])
async def get_portfolio_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves point-in-time snapshot histories across execution horizons."""
    data = await portfolio_service.get_portfolio_history(db, current_user.id)
    return StandardResponse(success=True, message="Portfolio history snapshots loaded.", data=data)
