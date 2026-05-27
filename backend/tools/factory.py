# backend/tools/factory.py
"""
Tool factory – provides Binance and LLM implementations based on environment flags.
Respects USE_MOCK_BINANCE and USE_FAKE_LLM settings from config.
"""

from typing import Union

from backend.core.config import settings
from backend.tools.mock_binance_tool import MockBinanceTool, get_mock_binance
from backend.tools.fake_llm import FakeLLM

import structlog
from structlog.stdlib import BoundLogger

logger: BoundLogger = structlog.get_logger(__name__)

logger.info("factory.py begins")

_mock_binance_instance = get_mock_binance()  # store the singleton instance


def get_binance_tool() -> MockBinanceTool:
    """
    Factory method for Binance tool.
    Returns MockBinanceTool if USE_MOCK_BINANCE=True, else RealBinanceTool (future).
    """
    use_mock = getattr(settings, "USE_MOCK_BINANCE", True)
    if use_mock:
        return _mock_binance_instance
    # In The Future, you'll add:
    # from backend.tools.real_binance_tool import RealBinanceTool
    # return RealBinanceTool()
    raise NotImplementedError("RealBinanceTool not yet implemented. Set USE_MOCK_BINANCE=true for now.")


def get_llm() -> FakeLLM:
    """
    Factory method for LLM client.
    Returns FakeLLM if USE_FAKE_LLM=True, else RealLLM (future).
    """
    use_fake = getattr(settings, "USE_FAKE_LLM", True)
    if use_fake:
        return FakeLLM()
    # In The Future, you'll add:
    # from backend.tools.real_llm import RealLLM
    # return RealLLM()
    raise NotImplementedError("RealLLM not yet implemented. Set USE_FAKE_LLM=true for now.")
