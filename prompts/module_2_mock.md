## CONTEXT
- Project conventions: PROJECT_CONVENTIONS.md
- Error codes: error_codes.md
- Existing code: backend/core/config.py, backend/core/logging.py
## MODULE: Mock Infrastructure
### Goal
Implement MockBinanceTool and FakeLLM classes that replicate real API reactions
without cost or runtime dependency.
### Components to implement
- backend/tools/mock_binance_tool.py: Class MockBinanceTool providing:
- get_balance() -> Static mock map (e.g., {"BTC": 0.01, "USDT": 500.0})
- get_market_price(symbol) -> Deterministic spot base price shifted randomly by
minor fraction drift.
- place_order(symbol, side, quantity) -> Returns a simulated FILLED execution
record, establishing price points. Includes flags for slippage simulation.
- backend/tools/fake_llm.py: Class FakeLLM with async method generate(prompt,
schema). Slices prompt keywords:
- Contains 'sentiment' -> returns mock bullish structured response.
- Contains 'decision' -> returns mock BUY structure response.
- Supports error flags to simulate timeouts or garbled non-JSON syntax.
- backend/tools/factory.py: Structural provider method mapping get_binance_tool()
and get_llm() to mock wrappers based on USE_MOCK_BINANCE and USE_FAKE_LLM
environment settings.
### Output format
Provide full code representations for all tool classes with clear inline docstring
usage illustrations.
