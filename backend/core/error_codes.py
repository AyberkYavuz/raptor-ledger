# backend/core/error_codes.py
"""
Error code definitions for the Raptor Ledger platform.
Matches the error_codes.md specification.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes used across the system."""

    # 400 Bad Request
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_TRADING_CONFIGURATION = "INVALID_TRADING_CONFIGURATION"

    # 401 Unauthorized
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"

    # 409 Conflict
    TRADING_ALREADY_ACTIVE = "TRADING_ALREADY_ACTIVE"

    # 422 Unprocessable Entity
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE"

    # 502 Bad Gateway
    BINANCE_API_ERROR = "BINANCE_API_ERROR"
    LLM_QUOTA_EXCEEDED = "LLM_QUOTA_EXCEEDED"

    # 500 Internal Server Error
    BACKTEST_DATA_MISSING = "BACKTEST_DATA_MISSING"

    # Additional for internal use
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
