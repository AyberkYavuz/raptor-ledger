# backend/core/state.py
import asyncio
from typing import Dict, Any, Optional


class TradingState:
    """Thread‑safe (async‑safe) singleton state for trading lifecycle."""
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.trading_active = False
        self.emergency_active = False
        self.trading_mode = "paper"          # "paper" or "live"
        self.risk_limits = {
            "max_daily_loss": 20.0,
            "max_position_size": 50.0
        }
        self.trading_config = {
            "symbols": [],
            "initial_budget": 0.0,
            "max_daily_loss": 20.0,
            "trading_mode": "paper"
        }

    async def set_trading_active(self, active: bool) -> None:
        async with self._lock:
            self.trading_active = active

    async def set_emergency_active(self, active: bool) -> None:
        async with self._lock:
            self.emergency_active = active

    async def set_trading_mode(self, mode: str) -> None:
        async with self._lock:
            self.trading_mode = mode

    async def set_risk_limits(self, limits: Dict[str, float]) -> None:
        async with self._lock:
            self.risk_limits.update(limits)

    async def set_trading_config(self, config: Dict[str, Any]) -> None:
        async with self._lock:
            self.trading_config.update(config)

    async def get_state(self) -> Dict[str, Any]:
        async with self._lock:
            return {
                "trading_active": self.trading_active,
                "emergency_active": self.emergency_active,
                "trading_mode": self.trading_mode,
                "risk_limits": self.risk_limits.copy(),
                "trading_config": self.trading_config.copy()
            }


# Global singleton instance
trading_state = TradingState()
