# backend/schemas/portfolio.py
from datetime import datetime
from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class OpenPositionSchema(BaseModel):
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float


class PortfolioStatusData(BaseModel):
    total_balance: float
    available_cash: float
    total_invested: float
    daily_pnl: float
    win_rate: float
    sharpe_ratio: float
    open_positions: List[OpenPositionSchema]


class PortfolioHistoryData(BaseModel):
    timestamp: datetime
    balance: float


class TradeHistoryData(BaseModel):
    trade_id: str
    symbol: str
    action: str
    quantity: float
    price: float
    timestamp: datetime

    class Config:
        from_attributes = True
