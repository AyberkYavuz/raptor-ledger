"""
Unit tests for Module 2: Mock Infrastructure (MockBinanceTool, FakeLLM, factory)
"""

import pytest
from backend.tools.mock_binance_tool import get_mock_binance
from backend.tools.fake_llm import FakeLLM
from backend.tools.factory import get_binance_tool, get_llm


@pytest.mark.asyncio
async def test_mock_binance_get_balance():
    tool = get_mock_binance()
    balance = await tool.get_balance()
    assert "USDT" in balance
    assert balance["USDT"] == 500.0
    assert "BTC" in balance
    assert balance["BTC"] == 0.01


@pytest.mark.asyncio
async def test_mock_binance_get_market_price():
    tool = get_mock_binance()
    price = await tool.get_market_price("BTCUSDT")
    # Price should be around base 65000 with ±0.1% drift
    assert 64000 < price < 66000


@pytest.mark.asyncio
async def test_mock_binance_place_buy_order():
    tool = get_mock_binance()
    initial_balance = await tool.get_balance()
    initial_btc = initial_balance["BTC"]

    order = await tool.place_order("BTCUSDT", "BUY", 0.002)
    assert order["status"] == "FILLED"
    assert order["side"] == "BUY"

    new_balance = await tool.get_balance()
    assert new_balance["BTC"] == pytest.approx(initial_btc + 0.002, rel=1e-9)
    # USDT decreased by approx quantity * price
    assert new_balance["USDT"] < initial_balance["USDT"]


@pytest.mark.asyncio
async def test_mock_binance_insufficient_balance():
    tool = get_mock_binance()
    with pytest.raises(Exception) as exc_info:
        # Try to buy more BTC than USDT can afford
        await tool.place_order("BTCUSDT", "BUY", 100.0)
    assert "INSUFFICIENT_BALANCE" in str(exc_info.value)


@pytest.mark.asyncio
async def test_mock_binance_simulate_timeout():
    tool = get_mock_binance()
    tool.simulate_timeout = True
    with pytest.raises(Exception) as exc_info:
        await tool.get_balance()
    assert "BINANCE_API_ERROR" in str(exc_info.value)
    tool.simulate_timeout = False  # reset


@pytest.mark.asyncio
async def test_fake_llm_sentiment():
    llm = FakeLLM()
    resp = await llm.generate("What is the sentiment of crypto market?")
    assert "market_sentiment" in resp
    assert resp["market_sentiment"] == "bullish"
    assert resp["confidence"] > 0.7


@pytest.mark.asyncio
async def test_fake_llm_decision():
    llm = FakeLLM()
    resp = await llm.generate("Make a trade decision for BTCUSDT")
    assert resp["decision"] in ("BUY", "SELL", "HOLD")
    assert resp["confidence"] > 0.8


@pytest.mark.asyncio
async def test_fake_llm_low_confidence():
    llm = FakeLLM()
    llm.simulate_low_confidence = True
    resp = await llm.generate("decision for BTC")
    assert resp["confidence"] < 0.6
    assert resp["decision"] == "HOLD"


@pytest.mark.asyncio
async def test_fake_llm_timeout():
    llm = FakeLLM()
    llm.simulate_timeout = True
    with pytest.raises(TimeoutError):
        await llm.generate("any prompt")
    llm.simulate_timeout = False


@pytest.mark.asyncio
async def test_factory_returns_mocks():
    binance = get_binance_tool()
    llm = get_llm()
    from backend.tools.mock_binance_tool import MockBinanceTool
    assert isinstance(binance, MockBinanceTool)  # compare with class, not instance
    assert isinstance(llm, FakeLLM)
