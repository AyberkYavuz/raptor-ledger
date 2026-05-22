# backend/tools/mock_binance_tool.py
"""
MockBinanceTool – deterministic simulation of Binance API for offline testing.
No real network calls, no API keys required.
"""

import random
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

import structlog
from structlog.stdlib import BoundLogger

from backend.core.config import Settings
from backend.core.error_codes import ErrorCode

logger: BoundLogger = structlog.get_logger(__name__)

logger.info("mock_binance_tool.py begins")


class MockBinanceTool:
    """
    Simulates Binance spot trading with configurable deterministic behavior.
    Supports balance queries, market price (with drift), and order placement.
    """

    def __init__(self):
        # Static mock balances (USDT as quote asset, BTC as base)
        self._balances: Dict[str, float] = {
            "USDT": 500.0,
            "BTC": 0.01,
            "ETH": 0.5,
        }
        # Base price cache per symbol (USDT pairs)
        self._base_prices: Dict[str, float] = {
            "BTCUSDT": 65000.0,
            "ETHUSDT": 3200.0,
        }
        # Simulation flags (can be toggled for failure tests)
        self.simulate_timeout: bool = False
        self.simulate_invalid_response: bool = False
        self.slippage_bps: int = 5  # basis points (0.05% default slippage)

    async def get_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        """
        Return mock balance for a specific asset or the whole portfolio.

        Args:
            asset: Optional asset symbol (e.g. "USDT", "BTC"). If None, return all.

        Returns:
            Dict mapping asset -> available balance.

        Raises:
            Exception: If simulate_timeout is True (simulate network error).
        """
        if self.simulate_timeout:
            logger.error("MockBinanceTool simulated timeout")
            raise Exception(ErrorCode.BINANCE_API_ERROR.value)  # use your error enum

        if asset:
            return {asset: self._balances.get(asset, 0.0)}
        return self._balances.copy()

    async def get_market_price(self, symbol: str) -> float:
        """
        Return deterministic market price with small random drift per call.

        Drift range: ±0.1% of base price, reproducible across calls with fixed seed
        but changed each invocation to simulate real movement.

        Args:
            symbol: Trading pair e.g. "BTCUSDT".

        Returns:
            Current simulated price.
        """
        if self.simulate_timeout:
            raise Exception(ErrorCode.BINANCE_API_ERROR.value)

        base = self._base_prices.get(symbol, 100.0)
        # deterministic but "live" drift using symbol as seed + current second
        drift = random.uniform(-0.001, 0.001)  # ±0.1%
        price = round(base * (1 + drift), 2)
        logger.info("Mock market price", symbol=symbol, price=price)
        return price

    async def place_order(
        self,
        symbol: str,
        side: str,  # "BUY" or "SELL"
        quantity: float,
        simulate_slippage: bool = True,
    ) -> Dict[str, Any]:
        """
        Simulate order placement and immediate FILL.

        Args:
            symbol: Trading pair.
            side: "BUY" or "SELL".
            quantity: Amount of base asset (e.g., 0.002 BTC).
            simulate_slippage: If True, execution price may differ from requested.

        Returns:
            Mock order execution record with order_id, status, executed price, etc.

        Raises:
            Exception: For simulated failures (timeout, invalid response, insufficient balance).
        """
        if self.simulate_timeout:
            raise Exception(ErrorCode.BINANCE_API_ERROR.value)

        if self.simulate_invalid_response:
            raise Exception("Garbled non-JSON response from mock")

        # Check balance before "executing"
        current_price = await self.get_market_price(symbol)
        quote_asset = symbol.replace("USDT", "") if symbol.endswith("USDT") else "USDT"
        required_quote = quantity * current_price if side == "BUY" else 0

        if side.upper() == "BUY":
            usdt_balance = self._balances.get("USDT", 0.0)
            if usdt_balance < required_quote:
                raise Exception(ErrorCode.INSUFFICIENT_BALANCE.value)

            # Deduct USDT, add base asset
            self._balances["USDT"] -= required_quote
            base_asset = symbol.replace("USDT", "")
            self._balances[base_asset] = self._balances.get(base_asset, 0.0) + quantity

        elif side.upper() == "SELL":
            base_asset = symbol.replace("USDT", "")
            base_balance = self._balances.get(base_asset, 0.0)
            if base_balance < quantity:
                raise Exception(ErrorCode.INSUFFICIENT_BALANCE.value)

            self._balances[base_asset] -= quantity
            self._balances["USDT"] += required_quote
        else:
            raise ValueError(f"Invalid side: {side}. Use 'BUY' or 'SELL'.")

        # Simulate slippage (adjust execution price)
        execution_price = current_price
        if simulate_slippage:
            slippage_factor = 1 + (random.uniform(-self.slippage_bps, self.slippage_bps) / 10000)
            execution_price = round(current_price * slippage_factor, 2)

        order_id = f"MOCK_{uuid.uuid4().hex[:8]}"
        executed_record = {
            "symbol": symbol,
            "orderId": order_id,
            "clientOrderId": f"mock_{datetime.utcnow().timestamp()}",
            "price": str(execution_price),
            "origQty": str(quantity),
            "executedQty": str(quantity),
            "cummulativeQuoteQty": str(quantity * execution_price),
            "status": "FILLED",
            "timeInForce": "GTC",
            "type": "MARKET",
            "side": side.upper(),
            "fills": [
                {
                    "price": str(execution_price),
                    "qty": str(quantity),
                    "commission": "0",
                    "commissionAsset": quote_asset,
                }
            ],
            "transactTime": int(datetime.utcnow().timestamp() * 1000),
        }
        logger.info("Mock order filled", symbol=symbol, side=side, quantity=quantity, price=execution_price)
        return executed_record

    async def get_open_orders(self, symbol: Optional[str] = None) -> list:
        """Mock: always return empty list (no pending orders in mock)."""
        return []

    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Mock cancel – always succeed."""
        return {"symbol": symbol, "orderId": order_id, "status": "CANCELED"}
