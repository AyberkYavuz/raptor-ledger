## CONTEXT
- Database schema: database_schema.md (Trade and PortfolioSnapshot tables present)
- API contracts: Section 18.8, 18.9
- Existing: backend/db/models.py, backend/api/auth.py,
backend/tools/mock_binance_tool.py
## MODULE: Portfolio & Trade History
### Goal
Implement database services and structured REST APIs to track balance fields,
order archives, and open exposures.
### Components to implement
- backend/services/portfolio_service.py: Asynchronous logical operations:
- get_current_portfolio(user_id): Retrieves liquid assets via Binance Tool,
gathers trade logs from DB to compute positions, and tallies daily profit metrics.
- get_trade_history(user_id, filters): Paginated SQLAlchemy extraction for
historical trade rows.
- get_open_positions(user_id): Derives exposures via transactional aggregation
(sum of BUY tokens minus matched SELL events).
- backend/api/portfolio.py: Protected endpoints mapping GET /api/portfolio and GET
/api/portfolio/history to serve snapshot responses.
- backend/api/trades.py: Protected endpoints GET /api/trades and GET
/api/trades/open-positions.
### Output format
Provide database service layers and routing modules. Ensure all calls are
protected by the get_current_user authorization fence.
