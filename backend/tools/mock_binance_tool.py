# backend/tools/mock_binance_tool.py
import random
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import asyncio

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
        self._balances: Dict[str, float] = {
            "USDT": 500.0,
            "BTC": 0.01,
            "ETH": 0.5,
        }
        self._base_prices: Dict[str, float] = {
            "BTCUSDT": 65000.0,
            "ETHUSDT": 3200.0,
        }
        self.simulate_timeout: bool = False
        self.simulate_invalid_response: bool = False
        self.slippage_bps: int = 5
        # Lock to make balance updates thread-safe for asyncio
        self._balance_lock = asyncio.Lock()

    async def get_balance(self, asset: Optional[str] = None) -> Dict[str, float]:
        if self.simulate_timeout:
            logger.error("MockBinanceTool simulated timeout")
            raise Exception(ErrorCode.BINANCE_API_ERROR.value)

        async with self._balance_lock:
            if asset:
                return {asset: self._balances.get(asset, 0.0)}
            return self._balances.copy()

    async def get_market_price(self, symbol: str) -> float:
        if self.simulate_timeout:
            raise Exception(ErrorCode.BINANCE_API_ERROR.value)

        base = self._base_prices.get(symbol, 100.0)
        drift = random.uniform(-0.001, 0.001)
        price = round(base * (1 + drift), 2)
        logger.info("Mock market price", symbol=symbol, price=price)
        return price

    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        simulate_slippage: bool = True,
    ) -> Dict[str, Any]:
        if self.simulate_timeout:
            raise Exception(ErrorCode.BINANCE_API_ERROR.value)
        if self.simulate_invalid_response:
            raise Exception("Garbled non-JSON response from mock")

        current_price = await self.get_market_price(symbol)
        quote_asset = symbol.replace("USDT", "") if symbol.endswith("USDT") else "USDT"
        required_quote = quantity * current_price if side == "BUY" else 0

        async with self._balance_lock:
            if side.upper() == "BUY":
                usdt_balance = self._balances.get("USDT", 0.0)
                if usdt_balance < required_quote:
                    raise Exception(ErrorCode.INSUFFICIENT_BALANCE.value)

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
            "fills": [{"price": str(execution_price), "qty": str(quantity), "commission": "0", "commissionAsset": quote_asset}],
            "transactTime": int(datetime.utcnow().timestamp() * 1000),
        }
        logger.info("Mock order filled", symbol=symbol, side=side, quantity=quantity, price=execution_price)
        return executed_record

    async def reset_balances(self, initial_usdt: float = 500.0, initial_btc: float = 0.01, initial_eth: float = 0.5):
        """Reset all balances to a known state – useful for testing and emergency reset."""
        async with self._balance_lock:
            self._balances = {
                "USDT": initial_usdt,
                "BTC": initial_btc,
                "ETH": initial_eth,
            }
        logger.info("Mock balances reset", balances=self._balances)


# ---------- Singleton accessor ----------
_mock_binance_instance: Optional[MockBinanceTool] = None


def get_mock_binance() -> MockBinanceTool:
    """Return the global singleton instance of MockBinanceTool."""
    global _mock_binance_instance
    if _mock_binance_instance is None:
        _mock_binance_instance = MockBinanceTool()
    return _mock_binance_instance


def reset_mock_binance():
    """Reset the singleton instance (useful for test isolation)."""
    global _mock_binance_instance
    if _mock_binance_instance is not None:
        # Optionally reset balances as well
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            # If called from async context, we can await; otherwise create task
        except RuntimeError:
            loop = None
        # For simplicity, just create a new instance
        _mock_binance_instance = MockBinanceTool()
